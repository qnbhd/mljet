"""Module for scanning Python files for requirements."""

import ast
import functools
import json
import logging
import pathlib
from itertools import chain
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)

import importlib_metadata
from merge_requirements.manage_file import Merge

from deployme.utils.types import PathLike

log = logging.getLogger(__name__)


class CustomMerge(Merge):
    """
    Custom merge method inherited from Merge class
    in merge_requirements.manage_file
    """

    def pickup_deps(
        self, ignore_prefixes: List[str], unique: bool = True
    ) -> List[str]:
        """
        Custom method to pick up dependencies

        Args:
            ignore_prefixes: list of prefixes to ignore
            unique: if True, return unique dependencies

        Returns:
            List of dependencies

        """

        array = []

        for package, version in self.dict_libs.items():
            if len(version) > 0:
                array.append("".join(f"{package}=={version}"))
            else:
                array.append("".join(f"{package}"))

        dependencies = cleanup_dependencies(array, ignore_prefixes)

        if unique:
            dependencies = list(set(dependencies))

        return dependencies


def cleanup_dependencies(
    deps: List[str], ignore_prefixes: List[str]
) -> List[str]:
    """
    Cleanup dependencies from unwanted prefixes

    Args:
        deps: List of dependencies
        ignore_prefixes: List of prefixes to ignore

    Returns:
        List: List of dependencies without unwanted prefixes

    Raises:
        None

    """

    cleaned = []

    for dep in deps:

        if (
            next((prefix for prefix in ignore_prefixes if prefix in dep), None)
            is not None
        ):
            continue

        cleaned.append(dep)

    return cleaned


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

    with open(path, encoding="utf-8") as fin:
        source_js = json.load(fin)

    code = []

    if source_js["nbformat"] >= 4:
        for cell in source_js["cells"]:
            for line in cell["source"]:
                code.append(line)
    else:
        for cell in source_js["worksheets"][0]["cells"]:
            for line in cell["input"]:
                code.append(line)

    return "\n".join(code)


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
