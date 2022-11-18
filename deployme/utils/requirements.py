"""Module for scanning Python files for requirements."""

import ast
import functools
import json
import logging
import pathlib
import re
from itertools import chain
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)

import importlib_metadata
from packaging.version import (
    Version,
    parse,
)
from pkg_resources import Requirement

from deployme.utils.nb import get_code_from_ipynb
from deployme.utils.types import PathLike

log = logging.getLogger(__name__)


# pep345
python_package_name_pattern = (
    r"([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9])"
)
# pep440 canonical
python_version_template = (
    r"([1-9][0-9]*!)?(0|[1-9][0-9]*)"
    r"(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?"
    r"(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?"
)
# final template
template = (
    r"^(?P<package_name>"
    + python_package_name_pattern
    + r")"
    + r"==(?P<version>"
    + python_version_template
    + r")$"
)
pinned_version_requirement = re.compile(template)


def validate(req):
    if not pinned_version_requirement.match(req):
        raise ValueError(
            f"Invalid requirement: {req}, should be pinned with `==`"
        )
    return req


class _ComparableRequirement:
    """
    Combines :class:`pkg_resources.ComparableRequirement`
    and :class:`packaging.version.Version`.
    Adds the ability to check package names and compare them.
    Supports only pinned versions.

    >>> a = _ComparableRequirement("a==1.0")
    >>> b = _ComparableRequirement("a==1.0")
    >>> a == b
    True
    >>> b = _ComparableRequirement("a==1.2")
    >>> a < b
    True
    >>> a > b
    False
    >>> a == _ComparableRequirement("a==1.0.dev0")
    False

    .. note::
        For comparison, names must be equal, otherwise
        :class:`AssertionError` will be raised.
    """

    def __init__(self, requirement: str):
        self._requirement = Requirement.parse(requirement)
        assert len(self._requirement.specs) == 1, "Only one spec is allowed"
        assert self._requirement.marker is None, "Markers are not supported"
        assert self._requirement.extras == (), "Extras are not supported"
        self._version = parse(self._requirement.specs[0][1])
        assert isinstance(self._version, Version), (
            "Requirement must be parsed"
            " as :class:`packaging.version.Version`"
        )

    @property
    def name(self):
        return self._requirement.key

    @property
    def version(self):
        return self._version

    def _check(self, other):
        assert isinstance(
            other, _ComparableRequirement
        ), "Other must be an instance of :class:`ComparableRequirement`"
        assert self.name == other.name, "Names must be equal"
        return other

    def __lt__(self, other):
        return self.version < self._check(other).version

    def __le__(self, other):
        return self.version <= self._check(other).version

    def __ge__(self, other):
        return self.version >= self._check(other).version

    def __gt__(self, other):
        return self.version > self._check(other).version

    def __eq__(self, other):
        return self.version == self._check(other).version

    def __ne__(self, other):
        return self.version != self._check(other).version

    def __str__(self):
        return f"{self.name}=={self.version}"


def merge(*requirements_lists: List[str]) -> List[str]:
    """
    Merge requirements lists.

    Args:
        requirements_lists: list of requirements

    Returns:
        Merged requirements
    """
    requirements_gen = (
        _ComparableRequirement(validate(requirement))
        for requirements_list in requirements_lists
        for requirement in requirements_list
    )
    name2version: Dict[str, _ComparableRequirement] = {}
    for requirement in requirements_gen:
        name2version[requirement.name] = min(
            name2version.get(requirement.name, requirement), requirement
        )
    return sorted([str(version) for version in name2version.values()])


def merge_requirements_txt(
    *files: PathLike, ignore_prefixes: Optional[List[str]] = None
) -> List[str]:
    """
    Merge requirements.txt files.

    Args:
        files: list of requirements.txt files
        ignore_prefixes: list of prefixes to ignore

    Returns:
        Final requirements.txt file content
    """

    ignore_prefixes = ignore_prefixes or []
    requirements_lists = []

    for file in files:
        with open(file, "r") as f:
            requirements = f.readlines()
        requirements = [
            r.strip() for r in filter(lambda x: x.strip(), requirements)
        ]
        requirements = [
            r
            for r in requirements
            if all(not r.startswith(p) for p in ignore_prefixes)
        ]
        requirements_lists.append(requirements)

    return merge(*requirements_lists)


def get_source_from_notebook(path: PathLike) -> str:
    """
    Extract the source code from a Jupyter notebook

    Args:
        path: Path to the notebook

    Returns:
        The source code as a string

    Raises:
        RuntimeError: If the notebook is not valid JSON
    """

    code_cells = get_code_from_ipynb(path)

    return "\n".join(code_cells)


@functools.lru_cache(None)
def freeze() -> Dict[str, str]:
    """
    Get a dictionary of installed packages and their versions

    Returns:
        A dictionary of installed packages and their versions
    """

    return {
        dist.metadata["Name"]: dist.version
        for dist in importlib_metadata.distributions()
    }


@functools.lru_cache(None)
def get_pkgs_distributions() -> dict:
    """
    Get a dictionary of installed packages and their module names

    Returns:
        A dictionary of installed packages and their module names
    """

    return {
        mod: pkg_list[0]
        for mod, pkg_list in importlib_metadata.packages_distributions().items()
    }


def extract_modules(
    node: Union[ast.Import, ast.ImportFrom],
    ignore_mods: Optional[List[str]] = None,
) -> dict:
    """
    Extract the modules from an import node

    Args:
        node: The import node
        ignore_mods: List of modules to ignore

    """

    packages = freeze()
    package2module = get_pkgs_distributions()

    ignore_mods = ignore_mods or []

    pool = {}

    if isinstance(node, ast.Import):

        for pkg_name in filter(lambda x: x.name in package2module, node.names):
            mod = package2module.get(pkg_name.name)

            if mod not in ignore_mods and mod in packages:
                pool[mod] = packages[mod]

    if isinstance(node, ast.ImportFrom) and node.module:
        base_mod, *_ = node.module.partition(".")

        mod = package2module.get(base_mod)

        if mod not in ignore_mods and mod and mod in packages:
            pool[mod] = packages[mod]

    return pool


def scan_requirements(
    path: PathLike,
    extensions: Optional[List[str]] = None,
    ignore_mods: Optional[List[str]] = None,
    ignore_names: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    Scan a directory of file for requirements.

    Args:
        path: Path to the directory
        extensions: List of file extensions to scan. Defaults to ['py', 'ipynb']
        ignore_mods: List of modules to ignore
        ignore_names: List of file/dirs names to ignore

    Returns:
        A dict of requirements and their versions

    Raises:
        ValueError: If the path is not correct
    """

    base = pathlib.Path(path)

    extensions = extensions or ["py", "ipynb"]

    ignore_mods = ignore_mods or []
    ignore_names = ignore_names or ["venv", ".venv"]

    pool = {}

    gen: Iterable = (base,)

    if base.is_dir():
        gen = filter(
            lambda x: all(name not in x.parts for name in ignore_names),  # type: ignore
            chain(*[base.glob(f"*.{ext}") for ext in extensions]),
        )

    for script in gen:

        if script.suffix == ".ipynb":
            source_code = get_source_from_notebook(script)
        else:
            with open(script, encoding="utf-8") as fin:
                source_code = fin.read()

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            log.info(
                f"File `{script}` skipped, because it is"
                f" not containing valid Python code."
            )
            continue

        for node in filter(
            lambda x: isinstance(x, (ast.Import, ast.ImportFrom)),
            ast.walk(tree),
        ):
            # noinspection PyTypeChecker
            mods = extract_modules(
                node, ignore_mods=ignore_mods  # type: ignore
            )
            pool.update(mods)

    return pool


def make_requirements_txt(
    path: PathLike,
    out_path: PathLike = "requirements.txt",  # type: ignore
    strict: Optional[bool] = True,
    extensions: Optional[List[str]] = None,
    ignore_mods: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    Make a requirements.txt file from a directory of files.

    Args:
        path: Path to the directory
        out_path: Path to the output file
        extensions: List of file extensions to scan. Defaults to ['py', 'ipynb']
        strict: Set only the exact version of the packages
        ignore_mods: List of modules to ignore

    Returns:
        A dict of requirements and their versions

    Raises:
        ValueError: If the path is not correct
    """

    requirements = scan_requirements(
        path, extensions, ignore_mods=ignore_mods or []
    )

    specifier = "==" if strict else ">="

    with open(out_path, "w", encoding="utf-8") as fin:
        for pkg, version in requirements.items():
            fin.write(f"{pkg}{specifier}{version}\n")

    return requirements
