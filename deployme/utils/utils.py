import logging
from pathlib import Path
import shutil

import executor


log = logging.getLogger(__name__)


def copy_template_files(
    project_path: Path,
    templates_path: Path,
):
    for file_name in [
        "Dockerfile.lama",
        "app.py",
        "requirements.txt",
    ]:
        dest_file = (
            "Dockerfile"
            if file_name.startswith("Dockerfile")
            else file_name
        )
        dest_path = project_path / dest_file
        if not dest_path.exists():
            src = templates_path / file_name
            shutil.copyfile(str(src), str(dest_path))
        else:
            print(
                f"{dest_file} already exists and won't be overwritten."
            )


def merge_requirements(project_path: Path):
    with open(project_path / "requirements.txt", "a") as wfd:
        with open(project_path.parent / "requirements.txt") as fd:
            user_reqs = "\n" + fd.read()
            wfd.write(user_reqs)


def copy_model(
    project_path: Path,
    model_path: Path,
):
    new_model_path = project_path / "models"
    new_model_path.mkdir(exist_ok=True, parents=True)
    new_model_path = new_model_path / "model.pkl"
    shutil.copyfile(str(model_path), str(new_model_path))


def call(cmd, **kwargs):
    log.debug(cmd)
    executor.execute(cmd)
