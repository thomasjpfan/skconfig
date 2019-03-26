skconfig
========

Scikit-learn sampling and validation library.

Features
--------

``skconfig`` is provides two key features: Validation of parameters for
scikit-learn models, and sampling these parameters. The sampling depends on 
`ConfigSpace <https://github.com/automl/ConfigSpace>`_.

Validation
..........

``skconfig`` creates a DSL for defining the search space for a sklearn model.
For example, we can defined a ``LogRegressionValidator`` as follows:

.. code-block:: python

    class LogRegressionValidator(BaseValidator):
        estimator = LogisticRegression
        
        penalty = StringParam("l2", "l1")
        dual = BoolParam()
        tol = FloatIntervalParam(lower=0, include_lower=False)
        C = FloatIntervalParam(lower=0)
        fit_intercept = BoolParam()
        intercept_scaling = FloatIntervalParam(lower=0, include_lower=False)
        class_weight = NoneParam()
        random_state = UnionParam(IntParam(), NoneParam())
        solver = StringParam("newton-cg", "lbfgs", "liblinear", "sag", "saga", "warn")
        max_iter = IntIntervalParam(lower=1)
        multi_class = StringParam("ovr", "multinomial", "auto", "warn")
        verbose = IntParam()
        warm_start = BoolParam()
        n_jobs = UnionParam(NoneParam(), IntIntervalParam(lower=-1))
        
        forbiddens = [
            ForbiddenAnd([ForbiddenEquals("penalty", "l1"), 
                          ForbiddenIn("solver", ["newton-cg", "sag", "lbfgs"])]),
            ForbiddenAnd([ForbiddenEquals("solver", "liblinear"), 
                          ForbiddenEquals("multi_class", "multinomial")]),
        ]


With this validator object, we can validate a set of parameters:

.. code-block:: python

    validator = LogRegressionValidator()

    # Does not raise an exception
    validator.validate_params(multi_class="ovr")

    # These will raise an exception
    validator.validate_params(penalty="hello world")
    validator.validate_params(solver="liblinear", multi_class="multinomial")
    validator.validate_params(penalty="l1", solver="sag")

    params_dict = {"penalty": "l1", "solver": "sag"}
    validator.validate_params(**params_dict)

Or validate a estimator:

.. code-block:: python

    est = LogisticRegression(solver="liblienar")
    validator.validate_estimator(est)  # Will not raise

Sampling
........

To sample the parameter space, a ``skconfig`` has a DSL for defining the 
distribution to be sampled from: 

.. code-block:: python

    sampler = Sampler(
        validator, 
        dual=UniformBoolDistribution(),
        C=UniformFloatDistribution(0.0, 1.0),
        solver=CategoricalDistribution(
            ["newton-cg", "lbfgs", "liblinear", "sag", "saga"]),
        random_state=UnionDistribution(
            ConstantDistribution(None), UniformIntDistribution(0, 10)),
        penalty=CategoricalDistribution(["l2", "l1"]),
         multi_class=CategoricalDistribution(["ovr", "multinomial"])
    )    

To sample from we call `sample`:

.. code-block:: python

    params_sample = sampler.sample(5)

which returns a list of 5 parameter dicts to be passed to `set_params`:

.. code-block:: python

    [{'C': 0.38684515891991544,
      'dual': True,
      'multi_class': 'ovr',
      'penalty': 'l2',
      'solver': 'lbfgs',
      'random_state': 1},
     {'C': 0.017914312843795077,
      'dual': True,
      'multi_class': 'ovr',
      'penalty': 'l2',
      'solver': 'lbfgs',
      'random_state': 0},
     {'C': 0.7044064976675997,
      'dual': True,
      'multi_class': 'ovr',
      'penalty': 'l2',
      'solver': 'liblinear',
      'random_state': 7},
     {'C': 0.9066951378139576,
      'dual': False,
      'multi_class': 'ovr',
      'penalty': 'l2',
      'solver': 'sag',
      'random_state': 10},
     {'C': 0.10402966368097444,
      'dual': True,
      'multi_class': 'multinomial',
      'penalty': 'l2',
      'solver': 'saga',
      'random_state': 7}]

To create an estimator from the first paramter item in ``params_sample``:

.. code-block:: python

    est = LogisticRegression(**params_sample[0])
    # or
    est.set_params(**params_sample[0])

Serialization
.............

The sampler can be serialized into a json:

.. code-block:: python

    import json
    json_serialized = json.dumps(sampler.to_dict(), indent=2)
    print(json_serialized)

which outputs:

.. code-block:: python

    {
        "dual": {
            "default": true,
            "type": "UniformBoolDistribution"
        },
        "C": {
            "lower": 0.0,
            "upper": 1.0,
            "default": 0.0,
            "log": false,
            "type": "UniformFloatDistribution"
        },
        "solver": {
            "choices": [
            "newton-cg",
            "lbfgs",
            "liblinear",
            "sag",
            "saga"
            ],
            "default": "newton-cg",
            "type": "CategoricalDistribution"
        },
        "random_state": {
            "type": "UnionDistribution",
            "dists": [
            {
                "type": "ConstantDistribution",
                "value": null
            },
            {
                "lower": 0,
                "upper": 10,
                "default": 0,
                "log": false,
                "type": "UniformIntDistribution"
            }
            ]
        },
        "penalty": {
            "choices": [
            "l2",
            "l1"
            ],
            "default": "l2",
            "type": "CategoricalDistribution"
        },
        "multi_class": {
            "choices": [
            "ovr",
            "multinomial"
            ],
            "default": "ovr",
            "type": "CategoricalDistribution"
        }
    }

To load the sampler from json

.. code-block:: python

    sampler_dict = json.loads(json_serialized)
    sampler_new = Sampler(validator).from_dict(sampler_dict)


Installation
------------

You can install skconfig directly from pypi:

.. code-block:: bash

    pip install git+https://github.com/thomasjpfan/skconfig

Development
-----------

The development version can be installed by running ``make dev``. Then we can lint ``make lint`` and tests by running ``pytest``.
