from pathlib import Path
import pickle
import shutil
import tempfile

from deployme.utils import call
from deployme.utils import copy_model
from deployme.utils import copy_template_files
from deployme.utils import get_random_name


BASE_IMAGE = "python:3.7-slim-buster"


def build_image(model_path, image_name, base_image):
    """Build a Docker image for the project."""
    project_path = Path.cwd() / "lama_project"
    project_path.mkdir(
        exist_ok=True, parents=True
    )  # TODO: make tempfolder
    templates_path = Path(__file__).parent.parent / "template"
    copy_template_files(project_path, templates_path)
    copy_model(project_path, model_path)

    command = (
        [
            "docker",
            "build",
        ]
        + ["--build-arg", f"BASE_IMAGE={base_image}"]
        + ["--tag", image_name]
        + [str(project_path)]
    )
    call(command)


def run_image(image_name, container_name=None, port=5000):
    """Run builded Docker image."""
    container_name = (
        container_name if container_name else get_random_name()
    )
    command = (
        ["docker", "run"]
        + ["-p", f"{port}:5000"]
        + ["--name", container_name]
        + [image_name]
    )
    call(command)


def deploy_to_docker(
    model,
    image_name,
    base_image=BASE_IMAGE,
    container_name=None,
    need_run=True,
    port=5000,
):
    model_path = tempfile.mkdtemp()
    model_path = f"{model_path}/model_lama.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    build_image(Path(model_path), image_name, base_image=base_image)
    if need_run:
        run_image(
            image_name, container_name=container_name, port=port
        )
    shutil.rmtree(model_path)
