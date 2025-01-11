import os
from blue_options.env import load_config, load_env

load_env(__name__)
load_config(__name__)


DAMAGES_TEST_DATASET_OBJECT_NAME = os.getenv(
    "DAMAGES_TEST_DATASET_OBJECT_NAME",
    "",
)
