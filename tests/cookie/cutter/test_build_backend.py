from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest

from deployme.cookie.cutter import build_backend

DEFAULTS_BACKENDS_PATH = Path(__file__).parent.parent.parent.parent.joinpath(
    "deployme", "cookie", "templates", "backends"
)

FLASK_TEMPLATE_PATH = DEFAULTS_BACKENDS_PATH.joinpath("_flask", "server.py")
SANIC_TEMPLATE_PATH = DEFAULTS_BACKENDS_PATH.joinpath("_sanic", "server.py")


def predict(model, data):
    return model.predict(data).tolist()


def predict_proba(model, data):
    return model.predict_proba(data).tolist()


# incorrect because name != 'predict'
def some_incorrect_predict(model, data, data2):
    return 2


def test_default_backends_exists():
    assert FLASK_TEMPLATE_PATH.exists()
    assert SANIC_TEMPLATE_PATH.exists()


@pytest.mark.parametrize(
    "template_path, methods_to_replace, methods, imports, expectation",
    [
        (
            FLASK_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [predict, predict_proba],
            None,
            does_not_raise(),
        ),
        (
            SANIC_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [predict, predict_proba],
            None,
            does_not_raise(),
        ),
        (
            FLASK_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [predict, predict_proba],
            ["numpy"],
            does_not_raise(),
        ),
        (
            SANIC_TEMPLATE_PATH,
            ["predict"],
            [predict, predict_proba],
            None,
            pytest.raises(ValueError),
        ),
        (
            "not_existing_path",
            ["predict", "predict_proba"],
            [predict, predict_proba],
            [],
            pytest.raises(FileNotFoundError),
        ),
        (
            Path(__file__).parent.parent.joinpath(
                "files", "exists_but_not_importable.ml"
            ),
            ["predict", "predict_proba"],
            [predict, predict_proba],
            [],
            pytest.raises(ImportError),
        ),
        (
            FLASK_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [some_incorrect_predict, predict_proba],
            [],
            pytest.raises(TypeError),
        ),
        (
            FLASK_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [predict, predict_proba],
            "some_import_into_string",
            pytest.raises(TypeError),
        ),
        (
            FLASK_TEMPLATE_PATH,
            ["predict", "predict_proba"],
            [predict, predict_proba],
            [1, 2, 3],  # imports must be sequence of strings
            pytest.raises(TypeError),
        ),
    ],
)
def test_build_backend(
    template_path, methods_to_replace, methods, imports, expectation
):
    with expectation:
        build_backend(template_path, methods_to_replace, methods, imports)
