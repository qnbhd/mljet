"""Module for scanning Python files for requirements."""

import ast
import functools
import json
import logging
import pathlib
from itertools import chain
from typing import Iterable, TypeVar, Union

import importlib_metadata
from merge_requirements.manage_file import Merge

PathLike = TypeVar("PathLike", str, pathlib.Path)

log = logging.getLogger(__name__)


class CustomMerge(Merge):
    """
    Custom merge method inherited from Merge class
    in merge_requirements.manage_file
    """

    def pickup_deps(self, ignore_prefixes: list, unique=True):
        """
        Custom method to pick up dependencies

        Args:
            ignore_prefixes (list): list of prefixes to ignore
            unique (bool): if True, return unique dependencies

        Returns:
            list: list of dependencies

        """

        array = []

        for key, value in self.dict_libs.items():
            if len(value) > 0:
                array.append("".join(f"{key}=={value}"))
            else:
                array.append("".join(f"{key}"))

        result = cleanup_deps(array, ignore_prefixes)

        if unique:
            result = list(set(result))

        return result


def cleanup_deps(deps: list, ignore_prefixes: list) -> list:
    """
    Cleanup dependencies from unwanted prefixes

    Args:
        deps (list): List of dependencies
        ignore_prefixes (list): List of prefixes to ignore

    Returns:
        list: List of dependencies without unwanted prefixes

    Raises:
        None

    """

    cleaned = []

    for dep in deps:

        if (
            next((p for p in ignore_prefixes if p in dep), None)
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

    with open(path, encoding="utf-8") as f:
        j = json.load(f)

    content = []

    if j["nbformat"] >= 4:
        for cell in j["cells"]:
            for line in cell["source"]:
                content.append(line)
    else:
        for cell in j["worksheets"][0]["cells"]:
            for line in cell["input"]:
                content.append(line)

    return "\n".join(content)


@functools.lru_cache(None)
def freeze() -> dict:
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


def extract_modules_from_node(
    node: Union[ast.Import, ast.ImportFrom], ignore_mods=None
) -> dict:
    """
    Extract the modules from an import node

    Args:
        node: The import node
        ignore_mods: List of modules to ignore

    """

    packages = freeze()
    package2module = get_pkgs_distributions()

    pool = {}

    if isinstance(node, ast.Import):

        for name in filter(
            lambda x: x.name in package2module, node.names
        ):
            n = package2module.get(name.name)

            if n not in ignore_mods and n in packages:
                pool[n] = packages[n]

    if isinstance(node, ast.ImportFrom) and node.module:
        basemod, *_ = node.module.partition(".")

        n = package2module.get(basemod)

        if n not in ignore_mods and n and n in packages:
            pool[n] = packages[n]

    return pool


def scan_requirements(
    path: PathLike,
    extensions=None,
    ignore_mods=None,
    ignore_names=None,
):
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
            lambda x: all(u not in x.parts for u in ignore_names),
            chain(*[base.glob(f"*.{ext}") for ext in extensions]),
        )

    for script in gen:

        if script.suffix == ".ipynb":
            content = get_source_from_notebook(script)
        else:
            with open(script, encoding="utf-8") as f:
                content = f.read()

        try:
            tree = ast.parse(content)
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
            mods = extract_modules_from_node(
                node, ignore_mods=ignore_mods  # type: ignore
            )
            pool.update(mods)

    return pool


def make_requirements_txt(
    path: PathLike,
    out_path: PathLike = "requirements.txt",  # type: ignore
    strict=True,
    extensions=None,
    ignore_mods=None,
):
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

    with open(out_path, "w", encoding="utf-8") as f:
        for pkg, version in requirements.items():
            f.write(f"{pkg}{specifier}{version}\n")

    return requirements
