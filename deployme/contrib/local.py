"""Local runner"""

import logging
from pathlib import Path
from typing import (
    Optional,
    Union,
)

from returns.iterables import Fold
from returns.pipeline import is_successful
from returns.result import (
    Success,
    safe,
)

from deployme.contrib.project_builder import full_build
from deployme.contrib.validator import (
    validate_ret_backend,
    validate_ret_model,
    validate_ret_port,
)
from deployme.utils.logging_ import init
from deployme.utils.types import (
    Estimator,
    PathLike,
)

log = logging.getLogger(__name__)


def local(
    model: Estimator,
    backend: Union[str, Path, None] = None,
    port: int = 5000,
    scan_path: Optional[PathLike] = None,
    verbose: bool = False,
    ignore_mypy: bool = False,
) -> bool:
    """Cook project"""

    init(verbose=verbose)

    log.info("Cooking project structure")

    val_result = Fold.collect(
        [
            safe(validate_ret_port)(port),
            safe(validate_ret_backend)(backend),
            safe(validate_ret_model)(model),
        ],
        Success(()),
    )

    if not is_successful(val_result):
        raise val_result.failure()

    # TODO (qnbhd): Maybe reuse model type?
    port, backend_path, _ = val_result.unwrap()  # type: ignore

    assert isinstance(backend_path, Path)

    scan_path = Path(scan_path) if scan_path else Path.cwd()

    project_path = Path.cwd().joinpath("build")

    build_result = safe(full_build)(
        project_path,
        backend_path,
        backend_path.joinpath("server.py"),
        scan_path,
        [model],
        ["model"],
        filename="server.py",
        ignore_mypy=ignore_mypy,
    )

    if not is_successful(build_result):
        raise build_result.failure()

    log.info("Project structure successfully built")

    return True
