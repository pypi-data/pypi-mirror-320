# Public Project AllOnIAModel

The main purpose of this module is to provide data scientists with the
:obj:`~alloniamodel.model.AllOnIAModel` class, that wraps the notion of AI
model to include an automatic persistence of trained models, with a complete
history of their trainings and the associated metrics. This allows for an easier
monitoring of the model performances, and the prediction pipeline is lighter
as it does not require to redefine every intermediary functions, like feature
engineering.

This persistence is done through the
:obj:`~alloniamodel.model.AllOnIAModel.save` method that pickles an instance of
the class to S3 using `cloudpickle <https://github.com/cloudpipe/cloudpickle>`_.
Then, creating a model with a name that already exists on
S3 will load it automatically.

This allows for an online monitoring of the model metrics, learning after
learning, prediction after prediction.

The user can trigger training and prediction pipelines through the
:obj:`~alloniamodel.model.AllOnIAModel.learn` and
:obj:`~alloniamodel.model.AllOnIAModel.apply` methods (see :ref:`pipeline_steps`).

Most methods of the training or prediction pipelines will accept custom keyword
arguments, which allows :obj:`~alloniamodel.model.AllOnIAModel` to cover a wide
range of use-cases. See :ref:`custom_keyword`.

Even though it is a public package, it is not intended to be used outside
AllOnIA's plateform.

You can find the user documentation at [this URL](https://aleia-team.gitlab.io/public/alloniamodel)

This is a public project. Everyone is welcome to contribute to it.

## Basic usage

To use this class, the user needs to provide some mandatory inputs :

### Mandatory user-defined **instance** attributes for learning

Assuming an instance of the class was created like that :

```python
from alloniamodel import AllOnIAModel

model = AllOnIAModel("iris_classification")
```

The following attributes/methods must be defined/called for the instance :

* :obj:`~alloniamodel.model.AllOnIAModel.set_variables`

```python
predictives = ("feature 1", "feature 2", "feature 3", "feature 4")
targets = ("target 1",)
model.set_variables(predictives, targets)
```

Note that there is a default value for predictive and target variables, `("x",)`
and `("y",)`,
but it will most of the time only be useful if using :obj:`~alloniamodel.utils.SpecialDataFormat`
objects.

* :obj:`~alloniamodel.model.AllOnIAModel.model` or
  :obj:`~alloniamodel.model.AllOnIAModel.model_class`

```python
model.model = KNeighborsClassifier(n_neighbors=1)
# OR
model.model_class = KNeighborsClassifier
```

The user can specify any kind of model here, as long as it is a class with
the fit and predict methods. The name of the fit and predict methods are
respectively `fit` and `predict` by default but can be changed through the
:obj:`~alloniamodel.model.AllOnIAModel.fit_function_name` and
:obj:`~alloniamodel.model.AllOnIAModel.predict_function_name` attributes.
The fit method should accept `X` as first argument, and
`y` as second, if target variables were specified (that is why
:obj:`~alloniamodel.model.AllOnIAModel.set_variables` must be called before setting
the model). If no target variables were specified, it is assumed that the given
model does not accept a `y` argument in its fit method. The predict method
should accept `X` as first argument.

* :obj:`~alloniamodel.model.AllOnIAModel.raw_set` (see :ref:`data_input`)

Once those are defined, the user can do

```python
model.learn()
model.save()
```

But the user might also want to specify more things :

### Optional user-defined **instance** attributes for learning

* :obj:`~alloniamodel.model.AllOnIAModel.add_validator`

```python
model.add_validator("surname name", "mail@adress", "admin")
```

Validators are not implemented yet, but in a futur update, any training or
prediction will trigger a reporting sent to the specified adresses.

* :obj:`~alloniamodel.model.AllOnIAModel.train_val_test_split_function` (see :ref:`split`)

```python
from mytools import some_split_function

model.train_val_test_split_function = some_split_function
```

* :obj:`~alloniamodel.model.AllOnIAModel.set_set_sizes`

```python
# Set the validation and test set sizes, as fraction of the raw set size.
model.set_set_sizes(0.1, 0.2)
```

* :obj:`~alloniamodel.model.AllOnIAModel.feature_engineering_function` (see :ref:`feature_engineering`)

```python
from mytools import some_feature_engineering_function

model.feature_engineering_function = some_feature_engineering_function
```

* :obj:`~alloniamodel.model.AllOnIAModel.compute_metrics_function` (see :ref:`evaluating`)

```python
from mytools import some_compute_metrics_function

model.compute_metrics_function = some_compute_metrics_function
```

### Mandatory user-defined **instance** attributes for prediction

* :obj:`~alloniamodel.model.AllOnIAModel.observations_set` (see :ref:`data_input`)

### Optional user-defined **instance** attributes for prediction

* :obj:`~alloniamodel.model.AllOnIAModel.postprocess_function` (see :ref:`pipeline_predict`)

```python
from mytools import some_postprocess_function

model.postprocess_function = some_postprocess_function
```

### Simple learning example

Here you can find detailed notebooks, custom functions and prediction pipelines
examples : :ref:`examples`.

### Monitoring

See :ref:`monitoring`.

## Installation

```bash
pip install alloniamodel
```

## Contributing

This is an open-source project. Everyone is welcome to contribute to it. To do
so, fork the repository, add your features/fixes on your forked repository,
then open a merge request to the original repository.

### Install dependencies using poetry

This project uses [Poetry](https://python-poetry.org/) to manage its
working environment. Install it before coding in the project.

Then, run 

 ```bash 
poetry env use python3.12
poetry install
poetry run pre-commit install
```

### Testing

Tests are separated into several groups, that can require different packages.

You can run them all using tox:

```bash
poetry run pytest
```

#### Coverage

We use `pytest-cov` to display the coverage, so, after run
tests you can check the reports (term, html, xml are enabled), if you want to
improve your coverage, the better thing to do is to check the html report in
your browser:

```bash
open htmlcov/index.html
```

### Lint

To run the linters used by this project, you can run:

```bash
poetry run pre-commit run # Run lint only on staged files

# Manually check conventional commits format:
poetry run pre-commit run gitlint --hook-stage commit-msg --commit-msg-filename .git/COMMIT_EDITMSG
```

### User documentation

The documentation source files are located in [here](docs/source/). If you add
new features, please add them to the documentation as well.

You can buid the documentation locally by doing

```bash
cd docs
make html
```

The produced documentation should then be readable by opening the file in
docs/build/html/index.html in a web browser.
