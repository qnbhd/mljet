"""CLI cook command module."""

import logging
import pickle
from pathlib import Path

import click

from mljet import cook as mljet_cook
from mljet.contrib.supported import Strategy
from mljet.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS
from mljet.utils.logging_ import init
from mljet.utils.serializers import detect_model_serializer

log = logging.getLogger(__name__)


@click.command("cook")
@click.argument(
    "strategy",
    type=click.Choice([s.replace("Strategy.", "").lower() for s in Strategy]),
)
@click.option(
    "--model",
    "model_path",
    "-m",
    type=click.Path(exists=True),
    required=True,
    help="Path to the model file.",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(list(SUPPORTED_BACKENDS.keys())),
    default="flask",
    help="Backend name to use as a template.",
)
@click.option(
    "--requirements-file",
    "additional_reqs",
    "-r",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to requirements.txt file.",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=None,
    help="Port to use.",
)
@click.option(
    "--tag",
    "-t",
    default=None,
    help="Docker image tag.",
)
@click.option(
    "--container-name",
    "-cn",
    default=None,
    help="Name of the container.",
)
@click.option(
    "--base-image",
    "-bi",
    default=None,
    help="Docker base image.",
)
@click.option(
    "--scan-path",
    "-s",
    type=click.Path(exists=True),
    default=str(Path.cwd()),
    help="Path to scan for requirements.",
)
@click.option(
    "--ignore-mypy",
    "-ig",
    is_flag=True,
    default=False,
    help="Ignore mypy errors.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Verbose mode.",
)
@click.option(
    "--workers",
    "-j",
    type=int,
    default=1,
    help="Number of workers to use.",
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Silent mode (detached).",
)
def cook(
    model_path,
    strategy,
    backend,
    port,
    tag,
    container_name,
    base_image,
    scan_path,
    ignore_mypy,
    verbose,
    workers,
    silent,
    additional_reqs,
):
    """Builds and deploys the project."""

    if strategy == "local" and (
        container_name is not None or tag is not None or base_image is not None
    ):
        raise click.BadParameter(
            "Container name, tag and base image are not supported "
            "for local strategy."
        )

    init(verbose)

    scan_path = Path(scan_path).resolve()
    model_path = Path(model_path).resolve()

    serializer = detect_model_serializer(model_path)
    # TODO (qnbhd): add support for other serializers
    log.info("Detected model serializer: [bold red]%s[/]", serializer)
    if serializer != "pickle":
        raise NotImplementedError(f"Unsupported serializer: {serializer}")
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    strategy = Strategy[strategy.upper()]

    mljet_cook(
        model=model,
        strategy=strategy,
        backend=backend,
        port=port,
        tag=tag,
        base_image=base_image,
        scan_path=scan_path,
        verbose=verbose,
        ignore_mypy=ignore_mypy,
        need_run=True,
        n_workers=workers,
        silent=silent,
        additional_requirements_files=additional_reqs,
    )

    log.info("Done!")
    log.info(f'Project was built in {Path.cwd() / "build"}')
