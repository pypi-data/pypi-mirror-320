from typing import List

from blue_options.terminal import show_usage, xtra


def help_ingest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~download,~upload", mono=mono)

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
        "ingest @damage data.",
        mono=mono,
    )


help_functions = {
    "ingest": help_ingest,
}
