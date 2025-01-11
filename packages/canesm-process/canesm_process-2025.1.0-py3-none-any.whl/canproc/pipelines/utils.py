from canproc.dag import DAGProcess
from pathlib import Path
import logging
import yaml
from typing import Literal
import re
import uuid
import ast


OPERATION_MAP = {
    "+": "xr.add",
    "-": "xr.sub",
    "*": "xr.mul",
    "/": "xr.truediv",
    "**": "xr.pow",
    ">": "xr.gt",
    ">=": "xr.ge",
    "<": "xr.lt",
    "<=": "xr.le",
    "==": "xr.eq",
}


class UUID:

    def __init__(self):
        self.uuid = uuid.uuid4()

    @property
    def short(self):
        return str(self.uuid)[0:8]

    @property
    def long(self):
        return str(self.uuid)


def canesm_52_filename(input_dir: Path, variable: str) -> str:
    return (input_dir / "*_gs.001*").as_posix()


def canesm_6_filename(input_dir: Path, variable: str) -> str:
    return (input_dir / f"{variable}.nc").as_posix()


def get_name_from_dict(data: dict):
    # add check for multiple keys
    return list(data.keys())[0]  # probably don't need to create a list


def include_pipelines(config: Path) -> list[list | str]:
    """iteratively traverse yaml files to include nested pipelines

    Parameters
    ----------
    config : Path
        initial yaml file

    Returns
    -------
    list
        yaml file or list of yaml files found in config
    """

    source_dir = Path(config).parent.absolute()
    yaml_file = source_dir / config
    config = yaml.safe_load(open(source_dir / config))
    pipelines = []
    if "pipelines" in config:
        for pipeline in config["pipelines"]:
            pipelines.append(include_pipelines(source_dir / pipeline))
        return pipelines
    return yaml_file


def flatten_list(nested_list: list):
    """recursively flatten a list

    Parameters
    ----------
    nested_list : list
        list of list of list...

    Returns
    -------
    list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def format_reuse(pipeline: dict):
    """move the reuse tag from the stage level to the variable level.
    This is to avoid collisions when merging stages from different files.

    Parameters
    ----------
    pipeline : dict


    Returns
    -------
    pipeline: dict
        input pipeline with "reuse" keys moved
    """

    for stage in pipeline.keys():

        if stage == "setup":
            continue

        if "reuse" not in pipeline[stage]:
            continue

        for idx, variable in enumerate(pipeline[stage]["variables"]):
            if isinstance(variable, str):
                variable = {variable: {"reuse": pipeline[stage]["reuse"]}}
            else:
                name = get_name_from_dict(variable)
                variable[name]["reuse"] = pipeline[stage]["reuse"]
            pipeline[stage]["variables"][idx] = variable

        del pipeline[stage]["reuse"]
    return pipeline


def merge_lists(a, b):
    """
    merge two lists preserving order as best as possible
    """

    copy = [el for el in a]
    idx = 0
    for el in b:
        # if element doesn't exist insert it at appropriate position
        try:
            idx = copy.index(el)
        except ValueError:
            copy.insert(idx + 1, el)
    return copy


def merge_pipelines(a: dict, b: dict):
    """merge partial pipelines into a single pipeline

    Parameters
    ----------
    a : dict
    b : dict

    Returns
    -------
    dict
        merged pipeline

    Raises
    ------
    Exception
        dictionaries have overlap that cannot be safely merged
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_pipelines(a[key], b[key])
            elif a[key] != b[key]:
                if isinstance(a[key], list) and isinstance(b[key], list):
                    a[key] = merge_lists(a[key], b[key])
                else:
                    raise Exception(f"Conflict at {key} with values {a[key]}, {b[key]}")
        else:
            a[key] = b[key]
    return a


def parse_formula(formula: str) -> list[str]:
    # checks left-most matches first so keep then first. E.g. test "<=" before "<"
    vars = [v.strip() for v in re.split("\\+|-|\\/|\\*|\\>=|\\>|\\<=|\\<|==", formula)]
    ops = [op.strip() for op in re.split("|".join(vars), formula) if op.strip()]
    return vars, ops


ast_ops = {
    ast.Pow: "**",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.GtE: ">=",
    ast.Gt: ">",
    ast.LtE: "<=",
    ast.Lt: "<",
    ast.Eq: "==",
}


def parse_node(op: ast.AST, attr_name: Literal["left", "right"]):
    """_summary_

    Parameters
    ----------
    op : ast.AST

    attr_name : str
        attribute of the node, either "left" or "right"

    Returns
    -------
    str | float | int
    """
    side = getattr(op, attr_name)
    if isinstance(side, ast.Name):
        return side.id
    elif isinstance(side, ast.BinOp):
        return binary_op_to_name(side)
    elif isinstance(side, ast.Constant):
        return side.value


def binary_op_to_name(op: ast.AST):
    """Recursively convert an AST node to a string"""
    left = parse_node(op, "left")
    right = parse_node(op, "right")
    return f"[{left}{ast_ops[type(op.op)]}{right}]"


class AstParser(ast.NodeVisitor):
    """Parse formula into a DAG using the `ast` module

    Examples
    --------

    >>> import ast
    >>> parser = AstParser()
    >>> tree = ast.parse("A * 2.0 + B / (C + D)")
    >>> dag = parser.build_dag(tree)
    """

    def __init__(self):
        super().__init__()
        self._nodes = []

    def parse_node(self, op: ast.AST):

        if isinstance(op, ast.BinOp):
            return binary_op_to_name(op)
        elif isinstance(op, ast.Name):
            return op.id
        elif isinstance(op, ast.Constant):
            return op.value
        else:
            return op

    def generic_visit(self, node: ast.AST):

        if isinstance(node, ast.BinOp):

            left_name = self.parse_node(node.left)
            right_name = self.parse_node(node.right)
            self._nodes.append(
                {
                    "name": binary_op_to_name(node),
                    "function": OPERATION_MAP[ast_ops[type(node.op)]],
                    "args": [left_name, right_name],
                }
            )
        elif isinstance(node, ast.Compare):
            # NOTE: This assumes only a single comparator,
            # eg. A < B < C is not allowed
            left_name = self.parse_node(node.left)
            right_name = self.parse_node(node.comparators[0])
            self._nodes.append(
                {
                    "name": f"[{left_name}{ast_ops[type(node.ops[0])]}{right_name}]",
                    "function": OPERATION_MAP[ast_ops[type(node.ops[0])]],
                    "args": [left_name, right_name],
                }
            )

        super().generic_visit(node)

    def build_dag(self, tree: ast.AST) -> dict:
        """build a dag from an abstract syntax tree.

        Parameters
        ----------
        tree : ast.AST
            formula parsed into an abstract syntax tree.

        Returns
        -------
        dict
            dictionary compatible for conversion to `DAG`
        """
        self._nodes = []
        self.generic_visit(tree)
        return {"dag": self._nodes, "output": self._nodes[0]["name"]}
