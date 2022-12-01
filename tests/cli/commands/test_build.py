import os
import pickle
from pathlib import Path
from unittest.mock import patch

from sklearn.linear_model import LogisticRegression

from deployme.cli.commands.build import build


def test_build():
    model_path = Path(__file__).parent.joinpath("model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(LogisticRegression(), f)

    with patch(
        "deployme.cli.commands.build.project_build", return_value=True
    ) as mock_local:
        # CliRunner is not used here because ValueError is raised
        # ISSUE: https://github.com/pytest-dev/pytest/issues/3344
        ctx = build.make_context("build", ["--model", str(model_path)])
        build.invoke(ctx)
        assert isinstance(
            mock_local.mock_calls[0].kwargs["model"], LogisticRegression
        )

    os.remove(model_path)
