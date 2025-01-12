import os

from blueness import module
from blue_objects import mlflow, metadata, file, objects, path
from blue_objects.env import abcli_path_git

from blue_sandbox import NAME
from blue_sandbox.env import ENCODED_BLOB_SAS_TOKEN
from blue_sandbox.microsoft_building_damage_assessment.sas_token import decode_token
from blue_sandbox.logger import logger


NAME = module.name(__file__, NAME)


# ... copy `configs/example_config.yml` and fill the first three sections.
def train(
    dataset_object_name: str,
    model_object_name: str,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.train: {dataset_object_name} -> {model_object_name}")

    config_filename = os.path.join(
        abcli_path_git,
        "building-damage-assessment/configs/example_config.yml",
    )
    success, config = file.load_yaml(config_filename)
    if not success:
        return False

    config["experiment_dir"] = objects.object_path(model_object_name)
    config["experiment_name"] = model_object_name

    config["imagery"]["rgb_fn"] = config["imagery"]["raw_fn"] = objects.path_of(
        filename="raw/maxar_lahaina_8_12_2023-visual.tif",
        object_name=dataset_object_name,
    )

    config["inference"]["output_subdir"] = objects.path_of(
        filename="outputs/",
        object_name=model_object_name,
    )
    config["inference"]["checkpoint_fn"] = objects.path_of(
        filename="checkpoints/last.ckpt",
        object_name=model_object_name,
    )

    config["infrastructure"]["container_name"] = "sandbox"
    config["infrastructure"][
        "storage_account"
    ] = "https://kamangir.blob.core.windows.net/"
    config["infrastructure"]["sas_token"] = decode_token(ENCODED_BLOB_SAS_TOKEN)
    config["infrastructure"]["relative_path"] = dataset_object_name

    config["labels"]["fn"] = objects.path_of(
        filename="label.geojson",
        object_name=dataset_object_name,
    )

    config["training"]["log_dir"] = objects.path_of(
        filename="logs/",
        object_name=model_object_name,
    )
    config["training"]["checkpoint_subdir"] = objects.path_of(
        filename="checkpoints/",
        object_name=model_object_name,
    )

    if not file.save_yaml(
        objects.path_of(
            filename="config.yml",
            object_name=model_object_name,
        ),
        config,
    ):
        return False

    return all(
        [
            mlflow.set_tags(
                model_object_name,
                {
                    "dataset": dataset_object_name,
                },
            ),
            metadata.post_to_object(
                model_object_name,
                "train",
                {
                    "dataset": dataset_object_name,
                },
            ),
        ]
    )
