"""Local runner"""

import logging
from pathlib import Path

from returns.iterables import Fold
from returns.pipeline import is_successful
from returns.result import Success

from deployme.contrib.project_builder import full_build
from deployme.contrib.validator import (
    validate_ret_backend,
    validate_ret_model,
    validate_ret_port,
)
from deployme.utils.logging_ import init

log = logging.getLogger(__name__)


def local(
    model,
    backend=None,
    port=5000,
    scan_path=None,
    verbose=False,
) -> bool:
    """Cook project"""

    init(verbose=verbose)

    log.info("Cooking project structure")

    val_result = Fold.collect(
        [
            validate_ret_port(port),
            validate_ret_backend(backend),
            validate_ret_model(model),
        ],
        Success(()),
    )

    if not is_successful(val_result):
        raise val_result.failure()

    # TODO (qnbhd): Maybe reuse model type?
    port, backend_path, _ = val_result.unwrap()

    assert isinstance(backend_path, Path)

    scan_path = Path(scan_path) if scan_path else Path.cwd()

    project_path = Path.cwd().joinpath("build")

    build_result = full_build(
        project_path,
        backend_path,
        backend_path.joinpath("server.py"),
        scan_path,
        [model],
        ["model"],
        filename="server.py",
    )

    if not is_successful(build_result):
        raise build_result.failure()

    log.info("Project structure successfully built")

    return True
