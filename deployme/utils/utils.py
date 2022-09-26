import logging
from pathlib import Path
import shutil

from merge_requirements.manage_file import ManageFile

from deployme.utils.requirements import CustomMerge


log = logging.getLogger(__name__)


def copy_template_files(
    project_path: Path,
    templates_path: Path,
):
    """
    Copy template files to the project folder

    Args:
        project_path: Path to the project folder
        templates_path: Path to the templates folder

    """

    for file_name in [
        "Dockerfile",
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

        if dest_path.exists():
            log.debug(
                f"File {dest_path} already exists, overwriting..."
            )

        src = templates_path / file_name
        shutil.copyfile(str(src), str(dest_path))


def merge_reqs(first_file, second_file, to):
    """
    Merge requirements.txt files

    Args:
        first_file: Path to the first requirements.txt file
        second_file: Path to the second requirements.txt file
        to: Path to the merged requirements.txt file

    """

    mf = ManageFile(first_file, second_file)

    mg = CustomMerge(mf)
    deps = mg.pickup_deps(ignore_prefixes=["deployme"])

    with open(to, "w", encoding="utf-8") as f:
        f.write("\n".join(deps))


def copy_project_files(
    project_path: Path,
    old_path: str,
    folder_name: str,
):
    """
    Copy project files to the project folder

    Args:
        project_path: Path to the project folder
        old_path: Path to the project folder
        folder_name: Name of the project folder

    """

    new_model_path = project_path / folder_name
    shutil.rmtree(new_model_path, ignore_errors=True)
    shutil.copytree(str(old_path), str(new_model_path))
