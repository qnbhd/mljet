# Contributing
Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:


## Report Bugs

Report bugs at Issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.


## Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with “bug” and “help wanted” is open to whoever wants to implement it.


## Implement Features

Look through the GitHub issues for features. Anything tagged with “enhancement” and “help wanted” is open to whoever wants to implement it.


## Write Documentation

mljet could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.


## Submit Feedback

The best way to send feedback is to file an issue at Issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Ready to contribute? Here’s how to set up mljet for local development.


# Workflow

1. Fork the mljet repo on GitHub.

2. Clone your fork locally:

```
$ git clone
```

3. Install your local copy into a virtualenv. Assuming you have venv installed, this is how you set up your fork for local development:

```
$ cd mljet/
$ python3 -m venv env
$ source env/bin/activate
$ pip install -e .
```

4. Create a branch for local development:

```
$ git checkout -b name-of-your-bugfix-or-feature
```
Now you can make your changes locally.

5. When you’re done making changes, check that your changes pass black, isort, flake8, mypy and the tests, including testing other Python versions with tox:

```
$ black .
$ isort mljet/
$ flake8 .
$ mypy .
$ pytest
```

To get flake8 and mypy to run automatically, consider installing a plugin for your editor. 6. Commit your changes and push your branch to GitHub:

```
$ git add .
$ git commit -m "Your detailed description of your changes."
$ git push origin name-of-your-bugfix-or-feature
```

Submit a pull request through the GitHub website.


## Commit message guidelines
We use semantic-release to automate the release process. This requires that commit messages are formatted correctly. Please read the semantic-release documentation for more information.

## Pull Request Guidelines
Before you submit a pull request, check that it meets these guidelines:

- The pull request should include tests.
- If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
- The pull request should work for Python 3.8, 3.9 and 3.10. Check our CI configuration for the exact versions that are tested.
- If the pull request adds or changes a command line interface, it should include an example of how to use it in the docstring.
- Pull requests should be based on the main branch.

If you are adding a new dependency, please make sure it is added to `requirements.txt` and `requirements-dev.txt`, `pyproject.toml`.

## Code style guidelines

We use `black`, `isort`, `flake8`, `mypy` and `pylint` to enforce a consistent code style. Please make sure your code is compliant by running these tools before submitting a pull request.

```
black .
isort mljet/
flake8 .
mypy .
pylint .
```

## Functional programming

We use functional programming to make the code more readable and maintainable. This means that we avoid using mutable variables and side-effects as much as possible. This also means that we prefer functions over classes, and that we prefer immutable data structures like tuples and namedtuples over mutable data structures like lists and dictionaries.
We use the returns library to make working with functional programming in Python easier.

Please read the documentation for this library before contributing.
It is worth noting, however, that we try to make sure that the return value and arguments of functions written in functional style are not containerized. This will simplify testing, and also gives ease of transition of the function to imperative style.

## Docstrings
We use Google style docstrings. Please make sure your docstrings are compliant by running pydocstyle before submitting a pull request.

```
pydocstyle .
```
