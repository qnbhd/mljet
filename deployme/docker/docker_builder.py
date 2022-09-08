from pathlib import Path
import pickle
import shutil
import tempfile

from deployme.utils import call
from deployme.utils import copy_model
from deployme.utils import copy_template_files
from deployme.utils import get_random_name
from deployme.utils.logging import init
from deployme.utils.utils import merge_requirements


init(verbose=True)

BASE_IMAGE = "python:3.10-slim-bullseye"


def build_image(model_path, image_name, base_image):
    """Build a Docker image for the project."""
    project_path = Path.cwd() / "lama_project"
    project_path.mkdir(
        exist_ok=True, parents=True
    )  # TODO: make tempfolder
    templates_path = Path(__file__).parent.parent / "template"
    copy_template_files(project_path, templates_path)

    call(f"pipreqsnb {Path.cwd()}")
    call(
        f'merge_requirements {project_path / "requirements.txt"} {project_path.parent / "requirements.txt"}'
    )
    call(
        f'mv {project_path.parent / "requirements-merged.txt"} {project_path / "requirements.txt"}'
    )

    copy_model(project_path, model_path)

    call(
        f"docker build --build-arg BASE_IMAGE={base_image} --no-cache --tag {image_name} {str(project_path)}"
    )


def run_image(image_name, container_name=None, port=5000):
    """Run builded Docker image."""
    container_name = (
        container_name if container_name else get_random_name()
    )
    call(
        f"docker run -p {port}:5000 --name {container_name} {image_name}"
    )


def deploy_to_docker(
    model,
    image_name,
    base_image=BASE_IMAGE,
    container_name=None,
    need_run=True,
    port=5000,
):
    model_path = tempfile.mkdtemp()
    model_path = f"{model_path}/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    build_image(Path(model_path), image_name, base_image=base_image)
    if need_run:
        run_image(
            image_name, container_name=container_name, port=port
        )
    shutil.rmtree(model_path, ignore_errors=True)
