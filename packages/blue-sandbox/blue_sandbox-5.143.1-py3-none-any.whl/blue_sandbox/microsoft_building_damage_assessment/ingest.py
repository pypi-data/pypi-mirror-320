from blueness import module

from blue_objects import mlflow, metadata

from blue_sandbox import NAME
from blue_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def ingest(
    event_name: str,
    object_name: str,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.ingest({event_name}) -> {object_name}")

    return all(
        [
            mlflow.set_tags(
                object_name,
                {"event": event_name},
            ),
            metadata.post_to_object(
                object_name,
                "ingest",
                {"event": event_name},
            ),
        ]
    )
