import argparse
from typing import List

from slack_sdk.web.slack_response import SlackResponse

from hartware_lib.adapters.slack import SlackAdapter
from hartware_lib.settings import load_settings, SlackBotSettings


def slack_send(command: List[str] | None = None) -> SlackResponse:
    parser = argparse.ArgumentParser(description="Slack message sender.")
    parser.add_argument("message", help="set the message")
    parser.add_argument("-c", "--channel", help="set the channel")

    args = parser.parse_args(command or None)

    settings = load_settings(SlackBotSettings, {})

    return SlackAdapter(settings).send(message=args.message, channel=args.channel)
