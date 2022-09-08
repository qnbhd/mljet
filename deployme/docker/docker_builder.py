from pathlib import Path
import pickle
import shutil
import tempfile
import os

import warnings
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator


from deployme.utils import copy_models
from deployme.utils import copy_template_files
from deployme.utils import get_random_name
from deployme.utils.logging import init

from pipreqsnb import pipreqsnb
from merge_requirements.manage_file import ManageFile, Merge
import docker


init(verbose=True)

BASE_IMAGE = "python:3.10-slim-bullseye"

docker_client = docker.from_env()


def merge_reqs(first_file, second_file):
    mf = ManageFile(
        first_file,
        second_file
    )

    mg = Merge(mf)
    mg.generate_requirements_txt()


def build_image(model_path, image_name, base_image):
    """Build a Docker image for the project."""
    project_path = Path.cwd() / "project"
    project_path.mkdir(
        exist_ok=True, parents=True
    )  # TODO: make tempfolder
    templates_path = Path(__file__).parent.parent / "template"
    copy_template_files(project_path, templates_path)

    project_reqs_path = str(project_path / "requirements.txt")
    pipreqsnb_reqs_path = str(project_path.parent / "requirements.txt")

    pipreqsnb.main()
    merge_reqs(project_reqs_path, pipreqsnb_reqs_path)
    shutil.move(f'{str(project_path.parent / "requirements-merged.txt")}', project_reqs_path)
    if os.path.isfile(pipreqsnb_reqs_path):
        os.remove(pipreqsnb_reqs_path)

    copy_models(project_path, model_path)

    docker_client.images.build(buildargs={'BASE_IMAGE': base_image}, tag=image_name, path=str(project_path))


def run_image(image_name, model_type, n_workers, container_name=None, port=5000):
    """Run builded Docker image."""
    container_name = (
        container_name if container_name else get_random_name()
    )
    docker_client.containers.run(image=image_name, environment={'MODEL_TYPE': model_type, 'N_WORKERS': n_workers}, name=container_name, ports={'5000': port}, detach=True)


def deploy_to_docker(
    model,
    image_name,
    base_image=BASE_IMAGE,
    container_name=None,
    need_run=True,
    port=5000,
    preprocessor=None,
    n_workers=4,
    data_example=None,
):
    has_preprocessing = preprocessor is not None
    models_path = tempfile.mkdtemp()
    model_path = f"{models_path}/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    if "lightautoml" in str(type(model)):
        model_type = "LAMA"
    elif isinstance(model, Pipeline):
        model_type = "sklearn_pipe"
    elif isinstance(model, BaseEstimator):
        model_type = "sklearn_model"
        if not has_preprocessing:
            warnings.warn(
                "If you'd like to use a raw data as API input, you could provide preprocessor object"
                "callable object with preprocess data logic. Otherwise your API will accept only "
                "preprocessed data as an input."
            )

    if has_preprocessing:
        preprocessor_path = f"{models_path}/preprocessor.pkl"
        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)

    build_image(
        Path(models_path),
        image_name,
        base_image=base_image,
    )
    if need_run:
        run_image(
            image_name,
            model_type=model_type,
            n_workers=n_workers,
            container_name=container_name,
            port=port,
        )
    shutil.rmtree(models_path)
