import os
import pickle
from pathlib import Path
from unittest.mock import patch

from sklearn.linear_model import LogisticRegression

from deployme.cli.commands.cook import cook
from deployme.contrib.supported import Strategy


def test_cook():
    model_path = Path(__file__).parent.joinpath("model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(LogisticRegression(), f)

    with patch(
        "deployme.cli.commands.cook.deployme_cook", return_value=True
    ) as mock_cook:
        # CliRunner is not used here because ValueError is raised
        # ISSUE: https://github.com/pytest-dev/pytest/issues/3344
        ctx = cook.make_context("cook", ["docker", "--model", str(model_path)])
        cook.invoke(ctx)
        assert isinstance(
            mock_cook.mock_calls[0].kwargs["model"], LogisticRegression
        )
        assert mock_cook.mock_calls[0].kwargs["strategy"] == Strategy.DOCKER

    os.remove(model_path)
