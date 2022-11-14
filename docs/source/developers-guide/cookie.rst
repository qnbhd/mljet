======
Cookie
======

The `Cookie` module is needed to validate
and create final .py files with template-based services.

**Cookie** has next structure:

.. code::

    ├── cutter.py        -- Cutter for create final .py files
    ├── templates        -- Templates for services
    │     ├── backends   -- Folder with backends templates
    │     └── ml         -- Folder with ML model's wrappers
    └── validator.py     -- Validator for check correctness of service

---------
Templates
---------

~~~~~~~~
Backends
~~~~~~~~

This directory contains `.py` templates for backends based on
different frameworks, such as `flask`, `sanic`, or `fastapi`.

Using exactly regular files allows you to use the full power of static analyzers,
formatter and linters. It also makes them easy to run without any extra steps.

This approach also makes it very easy to create "clean" files without any extra effort.

All templates must obey some specification.

    Template specification:
        - template should have __main__ entrypoint.
        - template should have methods to replace, associated with passed methods.
        - template should have associated methods-endpoints.
        - template should have typing, that is pass mypy check.

Example of template:

.. code:: python3

    import ... # import all needed modules

    loaded_model = ...

    # model wrappers
    # need to be replaced with real model wrappers
    # can be simple stubs or real wrappers
    def predict(model, data) -> list: ...
    def predict_proba(model, data) -> list: ...

    # framework-specific endpoints
    # endpoints functions name must must be marked with a
    # special prefix, which is specified in the file
    # in method `_get_assoc_endpoint_name`
    # now it is `_<model method>`
    # for example for `predict` we have `_predict`
    @app.post("/predict")
    def _predict(...) -> ...: ...

    # entrypoint
    if __name__ == "__main__":
        ...

The logic from the `dispatcher.py` file is used to dynamically
search for existing backends by name.

It is also worth noting that each template must have a `Dockerfile`
as well as a dependency file.

~~
ML
~~

This directory contains `.py` templates for ML models wrappers.

Let's look at the file for an sklearn model:

.. code:: python3

    """Module that contains Scikit-learn model method's wrappers."""
    from deployme.contrib.supported import ModelType

    # This constant is needed to determine the type of model
    USED_FOR = [ModelType.SKLEARN_MODEL, ModelType.SKLEARN_PIPE]

    # this method need to cast numpy array to list
    # for `predict` method
    def predict(model, data) -> list:
        return model.predict(data).tolist()

    # this method need to cast numpy array to list
    # for `predict_proba` method
    def predict_proba(model, data) -> list:
        return model.predict_proba(data).tolist()


At the build stage, these functions replace the
functions in the files that describe the backends.


---------
Validator
---------

The validator is used to check templates for compliance with
the specification, described above.


------
Cutter
------

Templates undergo the following checks before being assembled:

- Validation from `validator` module.
- Static-typing check with `mypy`.

After the checks, the final files are assembled directly based
on the template.

- Model's wrappers replacement.
- Import's insertion.
- `Black` formatting.
- `Isort` formatting.

Replacing a function with an appropriate one is done by
searching for a regular expression. All the logic for this
is in the function `replace_functions_by_names`.
It also checks to see if the number of arguments matches,
and if the function names match.
