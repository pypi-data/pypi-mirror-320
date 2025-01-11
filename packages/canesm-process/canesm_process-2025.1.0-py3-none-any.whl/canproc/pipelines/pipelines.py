from canproc.pipelines.utils import (
    flatten_list,
    format_reuse,
    get_name_from_dict,
    include_pipelines,
    merge_pipelines,
    canesm_52_filename,
    canesm_6_filename,
    parse_formula,
)
from canproc.pipelines.variable import Variable
from canproc import DAG, merge
from pathlib import Path
import yaml


class Pipeline:
    """
    Convert a YAML configuration file to a DAG pipeline


    Example
    -------

    >>> from canproc.pipelines import Pipeline
    >>> pipeline = Pipeline('config.yaml', '/space/hall6/...', '/space/hall6/...')
    >>> dag = pipeline.render()

    """

    def __init__(
        self, config: str | Path, input_dir: str | Path, output_dir: str | Path | None = None
    ):
        """Pipeline initialization

        Parameters
        ----------
        config : str | Path
            path to the yaml configuration file
        input_dir : str | Path
            directory of input files
        output_dir : str | Path | None, optional
            top-level directory for output files, by default same as input directory.
            Sub-directories specified in `config` are relative to this location
        """

        self.path = config
        self.config = yaml.safe_load(open(config, "r"))
        self.variables: dict[str, Variable] = {}
        self.stages: list[str] = []
        self.directories: dict[str, Path] = {}

        self.input_dir = Path(input_dir)
        if output_dir is None:
            self.output_dir = input_dir
        else:
            self.output_dir = Path(output_dir)

        self.file_lookup = (
            canesm_52_filename
            if self.config["setup"]["canesm_version"] == "5.2"
            else canesm_6_filename
        )

        self.directories = self.config["setup"]["output_directories"]
        for directory in self.directories:
            self.directories[directory] = self.output_dir / Path(self.directories[directory])

    def _include_pipelines(self):
        """Collect and merge all the sub pipelines"""

        if "pipelines" not in self.config:
            self.config = format_reuse(self.config)
            return

        pipelines = flatten_list(include_pipelines(self.path))

        del self.config["pipelines"]
        for pipeline in pipelines:
            pipeline = yaml.safe_load(open(pipeline, "r"))
            pipeline = format_reuse(pipeline)
            self.config = merge_pipelines(self.config, pipeline)

    def _setup_stages(self):
        """Initialize the pipeline stages"""
        self.stages = self.config["setup"]["stages"]
        for stage in self.stages:
            if stage not in self.config:
                try:
                    self.stages.remove(stage)
                except ValueError:
                    pass

    def _initialize_variables(self):
        """
        Collect variables from all stages (`variables` and `computed`)
        """

        for stage in self.stages:
            for var in self.config[stage]["variables"]:
                if isinstance(var, dict):
                    name = get_name_from_dict(var)
                else:
                    name = var
                self.variables[name] = Variable(name, get_filename=self.file_lookup, from_file=True)

        for stage in self.stages:
            if "computed" in self.config[stage]:
                for var in self.config[stage]["computed"]:
                    name = get_name_from_dict(var)
                    self.variables[name] = Variable(name, from_file=False)

    def _open_files(self):
        """
        Open all the necessary files
        """
        for var in self.variables.values():
            if var.from_file:
                var.open(
                    self.input_dir,
                    engine=self.config["setup"]["file_format"],
                    assume_single_var=self.config["setup"]["canesm_version"] != "5.2",
                )
                var.add_tag("native")

    @staticmethod
    def parse_name_and_variable(var):
        if isinstance(var, dict):
            name = get_name_from_dict(var)
            variable = var[name]
        else:
            name = var
            variable = var
        return name, variable

    def _add_stage_to_variable(self, var: str | dict, stage: str):
        """Add a stage to a variable

        Parameters
        ----------
        var : str
            name of variable, or dictionary containing name as first key
        stage : str
            stage name
        """

        name, variable = self.parse_name_and_variable(var)
        tag = variable["reuse"] if "reuse" in variable else None

        # specialized stages for variables
        if stage in ["daily", "monthly", "yearly"]:
            self.variables[name].resample(f"{stage}", method="mean", reuse_from_tag=tag)

        elif stage in ["rtd"]:
            self.variables[name].resample(resolution="yearly", reuse_from_tag="monthly")
            self.variables[name].add_tag("rtd:annual")
            self.variables[name].area_mean(reuse_from_tag="rtd:annual")

        elif stage in ["zonal"]:
            self.variables[name].zonal_mean(reuse_from_tag=tag)

        # general computation stages
        # TODO: should there be this distinction between variable and computation at all?
        if isinstance(var, dict):
            self._add_stage_to_computation(var, stage, tag=tag)
        else:
            self._write_and_tag(name, stage)

    def create_mask(self, formula: str, tag: list[str] | str | None = None, mask_tag: str = "mask"):
        vars, ops = parse_formula(formula)
        var = self.variables[vars[0]]
        var.from_formula(formula, self.variables, reuse_from_tag=tag)
        var.add_tag(mask_tag)
        return var

    def _add_stage_to_computation(self, var: dict, stage: str, tag: str | list[str] | None = None):
        """Add a stage to a computation

        Parameters
        ----------
        var : str
            dictionary containing name as first key
        stage : str
            stage name
        tag : str | list[str] | None
            If provided, start the computation from this tag.
        """

        # name = get_name_from_dict(var)
        # value = var[name]
        name, variable = self.parse_name_and_variable(var)
        if isinstance(variable, str):
            self.variables[name].from_formula(variable, self.variables, reuse_from_tag=tag)
            self.variables[name].rename(name)
        else:
            if "dag" in variable:
                self.variables[name].dag(
                    variable["dag"], reuse_from_tag=tag, variables=self.variables
                )
            else:
                # branch if needed before applying other operations
                if "branch" in variable:
                    self.variables[name].branch_from_variable(
                        self.variables[variable["branch"]], reuse_from_tag=tag
                    )
                    del variable["branch"]

                for key in variable:
                    if key in self.variables[name].allowed_operations:
                        # TODO: think about *args, **kwargs as inputs to avoid this if/else and make this more generic
                        if key == "mask":
                            vars, ops = parse_formula(variable[key])
                            if len(ops) > 0:
                                mask_tag = f"mask_{stage}"
                                mask = self.create_mask(variable[key], tag=tag, mask_tag=mask_tag)
                                self.variables[name].mask(mask, reuse_from_tag=mask_tag)
                            else:
                                mask = self.variables[variable[key]]
                                self.variables[name].mask(mask, reuse_from_tag=tag)
                        else:
                            if key in ["rename", "destination"]:
                                arg = variable[key]
                            else:
                                # evaluate factor for computation
                                try:
                                    arg = float(variable[key])
                                except ValueError as e:
                                    arg = eval(variable[key])
                            getattr(self.variables[name], key)(arg)
                    else:
                        if key in ["reuse"]:
                            continue
                        else:
                            raise ValueError(f"options for {name} are not recognized")

        self._write_and_tag(name, stage)

    def _write_and_tag(self, name, stage):

        self.variables[name].add_tag(stage)
        try:
            self.variables[name].write(output_dir=self.directories[stage])
        except KeyError:
            pass
        self.variables[name].store_output()

    def _build_dag(self):

        for stage in self.stages:
            for var in self.config[stage]["variables"]:
                self._add_stage_to_variable(var, stage)
            if "computed" in self.config[stage]:
                for var in self.config[stage]["computed"]:
                    self._add_stage_to_computation(var, stage, tag=stage)

    def _merge_stages(self):
        return merge([v.render() for v in self.variables.values()])

    def render(self) -> DAG:
        """render a DAG suitable for running

        Returns
        -------
        DAG

        """
        self._include_pipelines()
        self._setup_stages()
        self._initialize_variables()
        self._open_files()
        self._build_dag()
        return self._merge_stages()


def canesm_pipeline(
    config: str | Path, input_dir: str | Path, output_dir: str | Path | None = None
):
    pipeline = Pipeline(config, input_dir, output_dir)
    return pipeline.render()
