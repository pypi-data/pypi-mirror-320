import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from blue_sandbox import NAME
from blue_sandbox.microsoft_building_damage_assessment.ingest import ingest
from blue_sandbox.microsoft_building_damage_assessment.label import label
from blue_sandbox.microsoft_building_damage_assessment.train import train
from blue_sandbox.microsoft_building_damage_assessment.sas_token import (
    decode_token,
    encode_token,
)
from blue_sandbox.help.microsoft_building_damage_assessment import list_of_events
from blue_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="decode_token | encode_token | ingest | label | train",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--dataset_object_name",
    type=str,
)
parser.add_argument(
    "--model_object_name",
    type=str,
)
parser.add_argument(
    "--event_name",
    type=str,
    default=list_of_events[0],
    help=" | ".join(list_of_events),
)
parser.add_argument(
    "--verbose",
    type=bool,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--token",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "decode_token":
    success = True
    print(decode_token(args.token))
elif args.task == "encode_token":
    success = True
    print(encode_token(args.token))
elif args.task == "ingest":
    success = ingest(
        object_name=args.object_name,
        event_name=args.event_name,
        verbose=args.verbose == 1,
    )
elif args.task == "label":
    success = label(
        object_name=args.object_name,
        verbose=args.verbose == 1,
    )
elif args.task == "train":
    success = train(
        dataset_object_name=args.dataset_object_name,
        model_object_name=args.model_object_name,
        verbose=args.verbose == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
