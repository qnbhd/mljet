import logging
from pathlib import Path
import shutil

import executor
from merge_requirements.manage_file import ManageFile
from merge_requirements.manage_file import Merge


log = logging.getLogger(__name__)


def copy_template_files(
    project_path: Path,
    templates_path: Path,
) -> None:
    for file_name in [
        "Dockerfile.lama",
        "app.py",
        "requirements.txt",
        "base_preprocessor.py",
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


def merge_requirements(project_path: Path) -> None:
    with open(project_path / "requirements.txt", "a") as wfd:
        with open(project_path.parent / "requirements.txt") as fd:
            user_reqs = "\n" + fd.read()
            wfd.write(user_reqs)


def merge_reqs(first_file: str, second_file: str) -> None:
    mf = ManageFile(first_file, second_file)

    mg = Merge(mf)
    mg.generate_requirements_txt()


def copy_project_files(
    project_path: Path,
    old_path: str,
    folder_name: str,
) -> None:
    new_model_path = project_path / folder_name
    shutil.copytree(str(old_path), str(new_model_path))


def call(cmd: str, **kwargs) -> None:
    log.debug(cmd)
    executor.execute(cmd)
