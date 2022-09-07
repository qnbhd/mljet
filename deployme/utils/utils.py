from pathlib import Path
import shutil
import subprocess

import click


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


def copy_model(
    project_path: Path,
    model_path: Path,
):
    new_model_path = project_path / "models"
    new_model_path.mkdir(exist_ok=True, parents=True)
    new_model_path = new_model_path / "model_lama.pkl"
    shutil.copyfile(str(model_path), str(new_model_path))


def call(cmd, **kwargs):
    click.echo(" ".join(c for c in cmd))
    exit_code = subprocess.run(cmd, **kwargs).returncode
    if exit_code:
        raise click.exceptions.Exit(code=exit_code)
