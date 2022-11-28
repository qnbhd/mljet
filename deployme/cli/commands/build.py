"""CLI build command module."""

import logging
import pickle
from pathlib import Path

import click

from deployme.contrib.actions.project_build import project_build
from deployme.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS
from deployme.utils.logging_ import init
from deployme.utils.serializers import detect_model_serializer

log = logging.getLogger(__name__)


@click.command("build")
@click.option(
    "--backend",
    "-b",
    type=click.Choice(SUPPORTED_BACKENDS.keys()),
    default="flask",
    help="Backend to use.",
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
    "--scan-path",
    "-s",
    type=click.Path(exists=True),
    default=str(Path.cwd()),
    help="Path to the directory with models.",
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
def build(
    backend, additional_reqs, scan_path, model_path, ignore_mypy, verbose
):
    """Builds the project."""

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

    project_build(
        model=model,
        backend=backend,
        scan_path=scan_path,
        verbose=verbose,
        ignore_mypy=ignore_mypy,
        additional_requirements_files=additional_reqs,
    )

    log.info("Done!")
    log.info(f'Project was built in {Path.cwd() / "build"}')
