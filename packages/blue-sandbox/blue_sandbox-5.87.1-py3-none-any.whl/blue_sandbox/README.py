import os

from blue_objects import file, README

from blue_sandbox import NAME, VERSION, ICON, REPO_NAME
from blue_sandbox.microsoft_building_damage_assessment import (
    README as microsoft_building_damage_assessment_README,
)


items = [
    "{}[`{}`]({}) [![image]({})]({}) {}".format(
        "🌐",
        "`@damages`",
        "https://github.com/kamangir/blue-sandbox/blob/main/blue_sandbox/microsoft_building_damage_assessment/README.md",
        "https://github.com/microsoft/building-damage-assessment/raw/main/figures/damage.png",
        "https://github.com/kamangir/blue-sandbox/blob/main/blue_sandbox/microsoft_building_damage_assessment/README.md",
        "Satellite imagery damage assessment workflow",
    )
] + [
    "{}[`{}`](#) [![image]({})](#) {}".format(
        ICON,
        f"experiment {index}",
        "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
        f"description of experiment {index} ...",
    )
    for index in range(2, 4)
]


def build():
    return README.build(
        items=items,
        path=os.path.join(file.path(__file__), ".."),
        ICON=ICON,
        NAME=NAME,
        VERSION=VERSION,
        REPO_NAME=REPO_NAME,
    ) and README.build(
        items=microsoft_building_damage_assessment_README.items,
        cols=len(microsoft_building_damage_assessment_README.list_of_steps),
        path=os.path.join(file.path(__file__), "microsoft_building_damage_assessment"),
        ICON=ICON,
        NAME=NAME,
        VERSION=VERSION,
        REPO_NAME=REPO_NAME,
    )
