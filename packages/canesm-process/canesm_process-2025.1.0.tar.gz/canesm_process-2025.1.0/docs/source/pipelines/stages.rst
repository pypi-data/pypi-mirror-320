.. _stages:


Stages
------

A "stage" is a logical grouping of operations. Aside from the :code:`setup` stage, 
all stages apply a series of operations to a list of variables. Outputs from one stage 
may be used as inputs to following stages if desired. 

A :code:`stage` has a few options:


Variables
*********

A list of variables to process in this stage. The variable name should correspond to a CanESM variable.

.. code-block:: yaml

    mystage:
      variables:
        - GT
        - ST


Applying Operations
*******************

DAG Format
^^^^^^^^^^
Operations can be applied to a variable using the :code:`DAG` format.

.. code-block:: yaml

    mystage:
      variables:
        - GT:
            dag:
              dag:
                - name: ST
                  function: xr.self.rename
                  kwargs:
                    GT: ST
              output: ST


Shortcuts
^^^^^^^^^

Common operations can be applied using some keyword shortcuts. These are expanded internally to their :code:`DAG` representation so are equivalent.


.. code-block:: yaml

    mystage:
      variables:
        - GT:
          # convert to fahrenheit and rename to "ST"
            rename: ST
            scale: 1.8
            shift: 32


Computed Values
^^^^^^^^^^^^^^^

It is common to combine multiple CanESM variables into an output variable. As a shorthand these can be provided as a formula. For example, 
if we wanted to take the difference between a few monthly averaged fields we could write:


.. code-block:: yaml

    monthly:
      variables:
        - OLR
        - FSR
        - FSO
      computed:
        - BALT: "FSO-FSR-OLR"


Formula parsing is based on python's :code:`ast` module, so most arithmetic syntax supported by python can be used.
For example, :code:`BALT: "2.4 * (FSO + FSR) - ((OLR - FSR) / (OLR + FSR))"` would be a valid (if meaningless) formula.

.. note:: 

  Any variables used in a formula must be present in :code:`variables`


Masking Values
^^^^^^^^^^^^^^

We can create and apply masks using the :code:`mask` keyword. For example, lets say we want the monthly 
average of cloud tops for deep convection (:code:`TCD`). First, we need to mask the native data on the locations that
have deep convection, :code:`CDCB > 0`, then perform a monthly resampling of that masked data. To accomplish
this we use two stages: in the first stage we apply a mask to :code:`TCD` and in the second we take the monthly average
using this masked data.



.. code-block:: yaml

    setup:
      stages:
        - transforms
        - monthly

    transforms:
      variables:
        - CDCB
        - TCD:
            rename: CI
            mask: CDCB > 0

    monthly:
      reuse: transforms
      variables:
        - TCD



Branching from a Variable
^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it can be useful to branch a variable (think of this as a git branch) 
where we are spinning off a copy at a known point. This can be useful
if we want to keep both the original and a new version of the variable around 
for later modifications. As an example, in CMIP we need to save the same variable
twice, but with a different name. One way to accomplish that is through branching.


.. code-block:: yaml

    transforms:
      variables:
        - RH:
            rename: relative_humidity

    monthly:
      reuse: transforms
      variables:
        - RH
      computed:
        - RH_clear_sky:
            branch: RH
            rename: relative_humidity_clear_sky
