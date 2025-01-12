from typing import Dict

from blue_sandbox.env import DAMAGES_TEST_DATASET_OBJECT_NAME

list_of_steps: Dict[str, Dict] = {
    "ingest": {
        "object_name": DAMAGES_TEST_DATASET_OBJECT_NAME,
        "image_name": "Maui-Hawaii-fires-Aug-23-damage-2025-01-09-GgnjQC",
    },
    "label": {
        "object_name": "",
        "image_name": DAMAGES_TEST_DATASET_OBJECT_NAME,
    },
    "train": {
        "object_name": "",
        "image_name": "Maui-Hawaii-fires-Aug-23-model-2025-01-10-NQb8IS",
    },
    "predict": {"object_name": "", "image_name": ""},
    "summarize": {"object_name": "", "image_name": ""},
}

items = (
    [f"`{step}`" for step in list_of_steps]
    + [
        (
            "[`{}`](https://kamangir-public.s3.ca-central-1.amazonaws.com/{}.tar.gz)".format(
                step["object_name"],
                step["image_name"],
            )
            if step["object_name"]
            else ""
        )
        for step in list_of_steps.values()
    ]
    + [
        (
            "![image](https://github.com/kamangir/assets/blob/main/blue-sandbox/{}.png?raw=true)".format(
                step["image_name"],
            )
            if step["image_name"]
            else ""
        )
        for step in list_of_steps.values()
    ]
)
