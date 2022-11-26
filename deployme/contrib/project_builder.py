"""Project builder."""

import json
import logging
import pickle
import shutil
from functools import partial
from pathlib import Path
from typing import (
    Callable,
    List,
    Optional,
    Sequence,
)

from returns.io import (
    IO,
    impure_safe,
)
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

from deployme.contrib.analyzer import get_associated_methods_wrappers
from deployme.cookie.cutter import build_backend as cook_backend
from deployme.utils.requirements import (
    make_requirements_txt,
    merge_requirements_txt,
)
from deployme.utils.types import (
    Estimator,
    PathLike,
    Serializer,
)

get_mna_aw = safe(get_associated_methods_wrappers)

log = logging.getLogger(__name__)


@impure_safe
def managed_write(
    filepath: PathLike,
    writer: Callable,
    mode: str = "w",
) -> ResultE:
    """Writes obj to stream using writer."""
    with open(filepath, mode) as stream:
        writer(stream)
        return Success(Path(filepath))


def init_project_directory(path: PathLike, force: bool = False) -> Path:
    """Initializes project directory."""
    log.info("Initializing project directory")
    path = Path(path)
    # check if path exists
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists")
    # create path
    path.mkdir(parents=True, exist_ok=True)
    path.joinpath("models").mkdir(parents=True, exist_ok=True)
    path.joinpath("data").mkdir(parents=True, exist_ok=True)
    return path


def dumps_models(
    path: PathLike,
    models: Sequence[Estimator],
    models_names: Sequence[str],
    serializer: Serializer = pickle,  # type: ignore
    ext: str = "pkl",
) -> Path:
    """Dumps models to models_path."""
    log.info("Serializing models")
    models_path = Path(path) / "models"
    if len(models) != len(models_names):
        raise ValueError("models and models_names must be same length")
    dump_result = Fold.collect(  # type: ignore
        [
            # write serialized model to models_path
            managed_write(
                models_path / f"{name}.{ext}",
                lambda stream: serializer.dump(
                    model, stream
                ),  # pylint: disable=W0640
                mode="wb",
                # if everything is ok, return Success with model name
            ).bind(
                lambda _: Success(name)  # type: ignore # pylint: disable=W0640
            )  # type: ignore
            for name, model in zip(models_names, models)
        ],
        # push into tuple
        Success(()),
    )

    if not is_successful(dump_result):
        raise dump_result.failure()  # type: ignore

    return Path(path)


def build_backend(
    path: PathLike,
    filename: str,
    template_path: PathLike,
    models: Sequence,
    imports: Optional[Sequence[str]] = None,
    ignore_mypy: bool = False,
) -> Path:
    path_wrapped = Path(path)
    imports = imports or []
    cook = safe(
        partial(
            cook_backend,
            template_path=template_path,
            imports=imports,
            ignore_mypy=ignore_mypy,
        )
    )
    build_result = (
        # get methods and associated wrappers
        Fold.collect(
            [get_mna_aw(model).bind(lambda x: Success(IO(x))) for model in models],  # type: ignore
            # push into tuple, wrap into IO
            Success(()),
        )
        # merge methods and associated wrappers forall models
        .bind(
            partial(
                Fold.loop,  # type: ignore
                acc=IO({}),
                function=lambda x: lambda acc: {**acc, **x},
            )
        )
        # now we have dict with methods and associated wrappers
        # cook backend
        .bind(
            lambda mn: cook(
                methods_to_replace=mn.keys(),  # type: ignore
                methods=mn.values(),  # type: ignore
            )
        )
        # write backend to path
        .bind(
            lambda x: managed_write(  # type: ignore
                path_wrapped.joinpath(filename),
                lambda stream: stream.write(x),
            )
        )
    )

    if not is_successful(build_result):
        raise build_result.failure()

    return Path(path)


def copy_backend_dockerfile(
    project_path: PathLike, backend_path: PathLike
) -> Path:
    """Copies backend Dockerfile to project_path."""
    backend_dockerfile = Path(backend_path).joinpath("Dockerfile")
    project_dockerfile = Path(project_path).joinpath("Dockerfile")
    shutil.copyfile(backend_dockerfile, project_dockerfile)
    return Path(project_path)


def build_requirements_txt(
    project_path: PathLike,
    backend_path: PathLike,
    scan_path: PathLike,
    additional_requirements_files: Optional[Sequence[PathLike]] = None,
) -> Path:
    """Builds requirements.txt"""

    scan_path = Path(scan_path)
    backend_reqs = Path(backend_path).joinpath("requirements.txt")
    target_reqs_path = Path(project_path).joinpath("requirements.txt")
    make_reqs_txt = safe(make_requirements_txt)

    # try to scan and make requirements.txt
    log.info("Scanning and making requirements.txt")
    make_result = make_reqs_txt(
        scan_path, out_path=target_reqs_path, ignore_mods=["deployme"]
    )

    if not is_successful(make_result):
        raise make_result.failure()

    reqs = make_result.unwrap()
    if not reqs and not additional_requirements_files:
        log.warning(
            "No requirements in scan stage found. Service may not work properly."
            " You can pass `additional_requirements_files` arguments in top-level"
            " functions or via CLI with `--requirements-file/-r` option."
        )
    else:
        log.info(
            f"Was founded next requirements:" f" {json.dumps(reqs, indent=4)}"
        )

    additional_requirements_files = additional_requirements_files or []

    merge_reqs_result = flow(
        # setup merge-reqs
        safe(merge_requirements_txt)(
            backend_reqs, target_reqs_path, *additional_requirements_files
        ),
        # write to file
        bind(
            safe(
                lambda deps: (
                    managed_write(
                        target_reqs_path,
                        lambda stream: stream.write("\n".join(deps)),
                    )
                )
            )
        ),
    )

    if not is_successful(merge_reqs_result):
        raise merge_reqs_result.failure()

    return Path(project_path)


def full_build(
    project_path: PathLike,
    backend_path: PathLike,
    template_path: PathLike,
    scan_path: PathLike,
    models: Sequence,
    models_names: Sequence[str],
    filename: str = "server.py",
    imports: Optional[Sequence[str]] = None,
    serializer: Serializer = pickle,  # type: ignore
    ext: str = "pkl",
    ignore_mypy: bool = False,
    additional_requirements_files: Optional[Sequence[PathLike]] = None,
) -> ResultE[Path]:
    """Builds project."""
    imports = imports or []
    build_result = (
        safe(init_project_directory)(project_path, force=True)
        .bind(
            safe(
                partial(
                    build_backend,
                    filename=filename,
                    template_path=template_path,
                    models=models,
                    imports=imports,
                    ignore_mypy=ignore_mypy,
                )
            )
        )
        .bind(safe(partial(copy_backend_dockerfile, backend_path=backend_path)))
        .bind(
            safe(
                partial(
                    build_requirements_txt,
                    backend_path=backend_path,
                    scan_path=scan_path,
                    additional_requirements_files=additional_requirements_files,
                )
            )
        )
        .bind(
            safe(
                partial(
                    dumps_models,
                    models=models,
                    models_names=models_names,
                    serializer=serializer,
                    ext=ext,
                )
            )
        )
    )

    if not is_successful(build_result):
        raise build_result.failure()

    return build_result
