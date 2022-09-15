import os
from pathlib import Path

import pytest

from deployme.utils.requirements import freeze
from deployme.utils.requirements import get_pkgs_distributions
from deployme.utils.requirements import get_source_from_notebook
from deployme.utils.requirements import make_requirements_txt
from deployme.utils.requirements import scan_requirements


def test_reqscan():
    path = Path(__file__).parent / "files"
    fz = scan_requirements(path, extensions=["py", "ipynb", "txt"])

    assert "pandas" in fz
    assert "scikit-learn" in fz
    assert "numpy" in fz


def test_single():
    path = Path(__file__).parent / "files" / "f1.py"
    fz = scan_requirements(path)
    assert "scikit-learn" in fz


def test_get_source_from_notebook():
    path = Path(__file__).parent / "files" / "f5.ipynb"
    content = get_source_from_notebook(path)
    assert content == "from scipy import stats as ss"


def test_freeze():
    fz = freeze()
    assert "numpy" in fz
    assert "scipy" in fz
    assert "pandas" in fz
    assert "scikit-learn" in fz


def test_pkgs_distributions():
    fz = get_pkgs_distributions()
    assert "numpy" in fz
    assert "scipy" in fz
    assert "pandas" in fz
    assert "sklearn" in fz


@pytest.mark.parametrize(
    "strict, specifier, inv_specifier",
    (
        (True, "==", ">="),
        (False, ">=", "=="),
    ),
)
def test_make_requirements_txt(strict, specifier, inv_specifier):
    path = Path(__file__).parent / "files"
    make_requirements_txt(path, strict=strict)

    with open("requirements.txt") as f:
        content = f.read()

    assert "numpy" in content
    assert "scipy" in content
    assert "pandas" in content
    assert "scikit-learn" in content
    assert specifier in content and inv_specifier not in content

    os.remove("requirements.txt")
