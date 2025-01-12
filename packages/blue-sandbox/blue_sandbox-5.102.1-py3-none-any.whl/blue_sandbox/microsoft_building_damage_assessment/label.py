import os

from blueness import module
from blue_objects import metadata, file, objects
from blue_objects.env import abcli_path_git

from blue_sandbox import NAME
from blue_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def label(
    object_name: str,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.label: {object_name}")

    geojson_filename = os.path.join(
        abcli_path_git,
        "building-damage-assessment/data/demo/labels/Maui_Wildfires_August_0.geojson",
    )

    if not file.copy(
        geojson_filename,
        objects.path_of(
            filename="label.geojson",
            object_name=object_name,
        ),
    ):
        return False

    return metadata.post_to_object(
        object_name,
        "label",
        {"geojson": geojson_filename},
    )
