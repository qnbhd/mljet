import logging
import pickle
from pathlib import Path
from unittest.mock import patch

import dill
import joblib
from hypothesis import (
    given,
    settings,
    strategies as st,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from deployme.contrib.project_builder import full_build
from deployme.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS
from tests.iomock import DefaultIOMock


@given(
    project_path=st.from_regex(r"a[\w\d_-]+", fullmatch=True),
    backend_path=st.sampled_from([SUPPORTED_BACKENDS["sanic"]]),
    filename=st.from_regex(r"a[\w\d_-]+\.py", fullmatch=True),
    imports=st.lists(st.sampled_from(["pandas", "numpy", "sklearn"])),
    serializer=st.sampled_from([pickle, dill, joblib]),
    ext=st.from_regex(r"[\w\d_-]+", fullmatch=True),
    ignore_mypy=st.sampled_from([True]),
)
@settings(deadline=None)
def test_full_build(
    project_path,
    backend_path,
    filename,
    imports,
    serializer,
    ext,
    ignore_mypy,
):
    models = [RandomForestClassifier(), LogisticRegression()]
    models_names = ["rf", "lr"]
    template_path = Path(backend_path).joinpath("server.py")
    logging.disable(logging.CRITICAL)

    mocker = DefaultIOMock(to_forward=[template_path])
    with mocker:

        def mock_make_requirements_txt(path, out_path, *args, **kwargs):
            with open(out_path, "w") as f:
                f.write(
                    """
sanic==20.12.2"""
                )
                return {"sanic": "20.12.2"}

        with patch(
            "deployme.contrib.project_builder.make_requirements_txt",
            mock_make_requirements_txt,
        ):
            full_build(
                project_path,
                backend_path,
                template_path,
                project_path,
                models,
                models_names,
                filename,
                imports,
                serializer,
                ext,
                ignore_mypy,
            )

    expected = f"""
|                ├── {project_path}
|                    ├── {filename}
|                    ├── data
|                    ├── models
|                        ├── lr.{ext}
|                        ├── rf.{ext}
|                    ├── requirements.txt
"""

    assert expected.replace(" ", "") in mocker.fs_tree.replace(" ", "")

    logging.disable(logging.NOTSET)
