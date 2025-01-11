from blueness import module

from blue_sandbox import NAME
from blue_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def ingest(
    event_name: str,
    object_name: str,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.ingest({event_name}) -> {object_name}")

    logger.info("🪄")

    return True
