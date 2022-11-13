"""Module that contains app builder."""

import importlib
import importlib.util
import inspect
import re
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import (
    Callable,
    Dict,
    Optional,
    Sequence,
    Union,
)

from black import (
    FileMode,
    format_str as process_black,
)
from isort.api import sort_code_string
from mypy.api import run as _mypy_run
from returns.iterables import Fold
from returns.pipeline import (
    flow,
    is_successful,
)
from returns.pointfree import bind
from returns.result import (
    ResultE,
    Success,
    safe,
)

from deployme.cookie.validator import validate
from deployme.utils.types import PathLike

_Module = Union[str, ModuleType]

__all__ = [
    "MypyValidationError",
    "replace_functions_by_names",
    "insert_import",
    "mypy_run",
    "build_backend",
]

pyfunc_with_body = re.compile(
    r"(?P<indent>[ \t]*)(async def|def)[ \t]*(?P<name>\w+)\s*\((?P<params>.*?)\)(?:[ "
    r"\t]*->[ \t]*(?P<return>\w+))?:(?P<body>(?:\n(?P=indent)(?:[ \t]+[^\n]*)|\n)+)"
)


class MypyValidationError(Exception):
    """Exception raised when the template is not passing mypy check."""


def replace_functions_by_names(source, names2repls: Dict[str, Callable]):
    """Replace functions by names in source code with `repl_codes`."""
    new_source = source
    replaced = []

    for m in pyfunc_with_body.finditer(source):
        source_with_signature = m.group(0)
        name = m.group("name")
        if name not in names2repls:
            continue
        argspec = m.group("params")
        argscount = len(argspec.split(","))
        if argscount != len(inspect.getfullargspec(names2repls[name]).args):
            raise TypeError(
                f"Method `{name}` takes {argscount} arguments, but "
                f"{len(inspect.getfullargspec(names2repls[name]).args)} were given"
            )
        repl_code = inspect.getsource(names2repls[name])
        after_black = process_black(repl_code, mode=FileMode())
        new_source = new_source.replace(source_with_signature, after_black)
        replaced.append(name)

    if len(replaced) != len(names2repls):
        raise ValueError(
            f"Replaced {len(replaced)} functions, but {len(names2repls)} were given"
        )

    return process_black(new_source, mode=FileMode())


def insert_import(text: str, deps: Sequence[str]):
    """
    Inserts import into text.

    Args:
        text: text to insert import into.
        deps: imports to insert.

    Returns:
        Text with inserted import.
    """

    if isinstance(deps, str):
        raise TypeError("`deps` must be a sequence of strings, not a string")
    if not all(isinstance(dep, str) for dep in deps):
        raise TypeError("`deps` must be a sequence of strings")

    return "\n".join([*[f"import {dep}" for dep in deps], text])


def mypy_run(text):
    """
    Run mypy check on template.

    Args:
        text: Source code of template.

    Returns:
        Result with mypy output.
    """

    res = _mypy_run(["-c", text])
    if res[2]:
        raise MypyValidationError(res[0])
    return res[0]


def build_backend(
    template_path: PathLike,
    methods_to_replace: Sequence[str],
    methods: Sequence[Callable],
    imports: Optional[Sequence[str]] = None,
    ignore_mypy: bool = False,
) -> str:
    """
    Build app from template.

    Args:
        template_path: path to template.
        methods_to_replace: methods to replace in template.
        methods: methods to replace with.
        imports: imports to insert into template.
        ignore_mypy: ignore mypy check.

    Returns:
        Result with app source code.

    Template specification:
        - template should have __main__ entrypoint.
        - template should have methods to replace, associated with passed methods.
        - template should have associated methods-endpoints.
        - template should have typing, that is pass mypy check.

    Some:
        Reporting intermediate ddd data such as the current trial number
        back to the framework, as done in :class:`~deployme.cookie.cutter.MyPyValidationError`.

    Raises:
        :class:`MypyValidationError`: if template is not passing mypy check.
        :class:`ValidationError`: if template is not passing validation.
        :class:`TypeError`: if template is not passing validation.
        FileNotFoundError: if template is not found.

    .. note::
        After app is built, it should be formatted with black, isort.
    """

    if len(methods_to_replace) != len(methods):
        raise ValueError(
            "methods_to_replace and methods must be the same length"
        )

    template_path = Path(template_path).resolve()
    imports = imports or []

    if not template_path.exists():
        raise FileNotFoundError(f"Template `{template_path}` not found")

    spec = importlib.util.spec_from_file_location("$server", template_path)

    if spec is None:
        raise ImportError(f"Failed to make spec from `{template_path}`")

    template_path = str(template_path)

    with open(template_path, encoding="utf-8") as f:
        text = f.read()

    # merge validation's results into one
    validation_result: ResultE = Fold.collect(  # type: ignore
        (
            # Checks:
            # entrypoint exists
            # existence of methods
            # existence of associated endpoints
            safe(validate)(text, methods_to_replace),
            # mypy check
            safe(mypy_run if not ignore_mypy else lambda x: x)(text),
        ),
        Success(()),
    )

    # if `validation_result` is `Failure`, then raise exception
    if not is_successful(validation_result):
        # take first error
        raise validation_result.failure()  # type: ignore

    # Built pipeline:
    # 1. Replace methods in template with passed methods.
    # 2. Insert imports into template.
    # 3. Format template with black.
    # 4. Format template with isort.
    # TODO (qnbhd): Mypy check crashes if mypy version != 0.950
    text_result = flow(  # type: ignore
        text,
        safe(
            partial(
                replace_functions_by_names,
                names2repls=dict(zip(methods_to_replace, methods)),
            )
        ),
        bind(safe(partial(insert_import, deps=imports))),
        bind(safe(partial(process_black, mode=FileMode()))),
        bind(safe(sort_code_string)),
    )

    if not is_successful(text_result):
        raise text_result.failure()

    return text_result.unwrap()
