from abcli.help.generic import help_functions as generic_help_functions

from blue_sandbox import ALIAS

from blue_sandbox.help.microsoft_building_damage_assessment import (
    help_functions as help_microsoft_building_damage_assessment,
)


help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "microsoft_building_damage_assessment": help_microsoft_building_damage_assessment,
    }
)
