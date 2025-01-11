from typing import Dict

list_of_steps: Dict[str, Dict] = {
    "ingest": "Maui-Hawaii-fires-Aug-23-damage-2025-01-09-GgnjQC",
    "label": "",
    "train": "",
    "predict": "",
    "summarize": "",
}

items = (
    [f"`{step}`" for step in list_of_steps]
    + [
        (
            "[`{}`](https://kamangir-public.s3.ca-central-1.amazonaws.com/{}.tar.gz)".format(
                object_name,
                object_name,
            )
            if object_name
            else ""
        )
        for object_name in list_of_steps.values()
    ]
    + [
        (
            "[![image](https://github.com/kamangir/assets/blob/main/blue-sandbox/{}.png?raw=true)](#)".format(
                object_name,
            )
            if object_name
            else ""
        )
        for object_name in list_of_steps.values()
    ]
)
