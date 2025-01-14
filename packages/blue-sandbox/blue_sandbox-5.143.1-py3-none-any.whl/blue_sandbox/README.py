import os

from blue_objects import file, README

from blue_sandbox import NAME, VERSION, ICON, REPO_NAME
from blue_sandbox.microsoft_building_damage_assessment import (
    README as microsoft_building_damage_assessment_README,
)
from blue_sandbox.list import list_of_experiments

items = [
    "{}[`{}`]({}) {} [![image]({})]({}) {}".format(
        experiment["ICON"],
        experiment_name,
        experiment["url"],
        experiment["status"],
        experiment["marquee"],
        experiment["url"],
        experiment["title"],
    )
    for experiment_name, experiment in list_of_experiments.items()
    if experiment_name != "template"
]


def build():
    return all(
        [
            README.build(
                items=items,
                path=os.path.join(file.path(__file__), ".."),
                ICON=ICON,
                NAME=NAME,
                VERSION=VERSION,
                REPO_NAME=REPO_NAME,
            ),
            README.build(
                path=os.path.join(file.path(__file__), "cemetery"),
                ICON=ICON,
                NAME=NAME,
                VERSION=VERSION,
                REPO_NAME=REPO_NAME,
            ),
            README.build(
                items=microsoft_building_damage_assessment_README.items,
                cols=len(microsoft_building_damage_assessment_README.list_of_steps),
                path=os.path.join(
                    file.path(__file__), "microsoft_building_damage_assessment"
                ),
                ICON=ICON,
                NAME=NAME,
                VERSION=VERSION,
                REPO_NAME=REPO_NAME,
            ),
            README.build(
                path=os.path.join(file.path(__file__), "sagesemseg"),
                ICON=ICON,
                NAME=NAME,
                VERSION=VERSION,
                REPO_NAME=REPO_NAME,
            ),
        ]
    )
