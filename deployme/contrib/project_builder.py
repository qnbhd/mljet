"""Project builder."""

import json
import logging
import pickle
import shutil
from functools import partial
from pathlib import Path
from typing import (
    Callable,
    Optional,
    Sequence,
)

from merge_requirements.manage_file import ManageFile
from returns.converters import flatten
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
    Failure,
    ResultE,
    Success,
    safe,
)

from deployme.contrib.analyzer import get_methods_names_and_associated_wrappers
from deployme.cookie.cutter import build_backend as cook_backend
from deployme.utils.requirements import (
    CustomMerge,
    PathLike,
    make_requirements_txt,
)

get_mna_aw = safe(get_methods_names_and_associated_wrappers)

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


def init_project_directory(path: PathLike, force=False) -> ResultE[Path]:
    """Initializes project directory."""
    path = Path(path)
    # check if path exists
    if path.exists() and not force:
        return Failure(ValueError(f"Path `{path}` already exists"))
    # create path
    path.mkdir(parents=True, exist_ok=True)
    path.joinpath("models").mkdir(parents=True, exist_ok=True)
    path.joinpath("data").mkdir(parents=True, exist_ok=True)
    return Success(path)


def dumps_models(
    path: PathLike,
    models: Sequence,
    models_names: Sequence[str],
    serializer=pickle,
    ext="pkl",
) -> ResultE[Path]:
    """Dumps models to models_path."""
    models_path = Path(path) / "models"
    return Fold.collect(  # type: ignore
        [
            # write serialized model to models_path
            managed_write(
                models_path / f"{name}.{ext}",
                lambda stream: serializer.dump(
                    model, stream  # pylint: disable=W0640
                ),
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


def build_backend(
    path: PathLike,
    filename: str,
    template_path: PathLike,
    models: Sequence,
    imports: Optional[Sequence[str]] = None,
) -> ResultE:
    path_wrapped = Path(path)
    imports = imports or []
    cook = partial(cook_backend, template_path=template_path, imports=imports)
    return (
        # get methods and associated wrappers
        Fold.collect(
            [
                get_mna_aw(model).bind(lambda x: Success(IO(x)))  # type: ignore
                for model in models
            ],
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
        # return Success if everything is ok
        .bind(lambda x: Success(path))
    )


def copy_backend_dockerfile(
    project_path: PathLike, backend_path: PathLike
) -> ResultE[Path]:
    """Copies backend Dockerfile to project_path."""
    backend_dockerfile = Path(backend_path).joinpath("Dockerfile")
    project_dockerfile = Path(project_path).joinpath("Dockerfile")
    shutil.copyfile(backend_dockerfile, project_dockerfile)
    return Success(Path(project_path))


def build_requirements_txt(
    project_path: PathLike,
    backend_path: PathLike,
    scan_path: PathLike,
) -> ResultE[Path]:
    """Builds requirements.txt"""

    scan_path = Path(scan_path)
    backend_reqs = Path(backend_path).joinpath("requirements.txt")
    target_reqs_path = Path(project_path).joinpath("requirements.txt")
    make_reqs_txt = safe(make_requirements_txt)

    # try to scan and make requirements.txt
    result = make_reqs_txt(
        scan_path, out_path=target_reqs_path, ignore_mods=["deployme"]
    )

    if not is_successful(result):
        return result

    log.info(
        f"Was founded next requirements: {json.dumps(flatten(result), indent=4)}"
    )

    return flow(
        # setup merge-reqs
        CustomMerge(ManageFile(backend_reqs, target_reqs_path)),
        # merge backend requirements with project requirements
        safe(lambda mg: mg.pickup_deps(ignore_prefixes=["deployme"])),
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
        bind(lambda _: Success(project_path)),  # type: ignore
    )


def full_build(
    project_path: PathLike,
    backend_path: PathLike,
    template_path: PathLike,
    scan_path: PathLike,
    models: Sequence,
    models_names: Sequence[str],
    filename: str = "backend.py",
    imports: Optional[Sequence[str]] = None,
    serializer=pickle,
    ext="pkl",
) -> ResultE[Path]:
    """Builds project."""
    imports = imports or []
    result = (
        init_project_directory(project_path, force=True)
        .bind(
            partial(
                build_backend,
                filename=filename,
                template_path=template_path,
                models=models,
                imports=imports,
            )
        )
        .bind(partial(copy_backend_dockerfile, backend_path=backend_path))
        .bind(
            partial(
                build_requirements_txt,
                backend_path=backend_path,
                scan_path=scan_path,
            )
        )
        .bind(
            partial(
                dumps_models,
                models=models,
                models_names=models_names,
                serializer=serializer,
                ext=ext,
            )
        )
    )
    return result
