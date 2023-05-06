from pathlib import Path

from hypothesis import (
    given,
    strategies as st,
)

from mljet.contrib.project_builder import copy_backend_dockerfile
from tests.iomock import DefaultIOMock


@given(path=st.from_regex(r"[\w\d_-]+", fullmatch=True))
def test_copy_backend_dockerfile(path):
    """Test copy_backend_dockerfile."""
    mocker = DefaultIOMock()
    with mocker:
        Path("source").mkdir(parents=True, exist_ok=True)
        with open("source/Dockerfile", "w") as fo:
            fo.write("FROM python:3.8")
        Path(path).mkdir(parents=True, exist_ok=True)
        copy_backend_dockerfile("source", path)
    minima = min(path, "source")
    maxima = max(path, "source")
    assert (
        f"""
|    ├── {minima}
|        ├── Dockerfile
|    ├── {maxima}
|        ├── Dockerfile
"""
        in mocker.fs_tree
    )
