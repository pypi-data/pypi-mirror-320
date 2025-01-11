from typing import List

from blue_options.terminal import show_usage, xtra

list_of_events = ["Maui-Hawaii-fires-Aug-23"]


def help_ingest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra("~download,dryrun,", mono=mono),
            "event=<event>",
            xtra(",~gdal,~rm,~upload", mono=mono),
        ]
    )

    args = [
        "[--verbose 1]",
    ]

    return show_usage(
        [
            "@damage",
            "ingest",
            f"[{options}]",
            "[-|<object-name>]",
        ]
        + args,
        "ingest <event> -> <object-name>.",
        {
            "event: {}".format(" | ".join(list_of_events)): [],
        },
        mono=mono,
    )


help_functions = {
    "ingest": help_ingest,
}
