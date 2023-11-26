import json
import os

import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import events

PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

APPROVE_LOG_CHANNEL_ID = 1173639682219847740
REJECT_LOG_CHANNEL_ID = 1173639815439335485


def middleware(event, context):
    print(f"event {event}")  # debug print
    print(event["rawBody"])

    # verify the signature
    try:
        raw_body = event.get("rawBody")
        auth_sig = event['params']['header'].get('x-signature-ed25519')
        auth_ts = event['params']['header'].get('x-signature-timestamp')

        message = auth_ts.encode() + raw_body.encode()
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(
            message,
            bytes.fromhex(auth_sig)
        )  # raises an error if unequal
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # ping pong
    body = event.get('body')
    if body.get("type") == TYPE.PING:
        return {
            "type": 1
        }

    # event handler
    custom_id = body.get("data", {}).get("custom_id", None)
    print(f"{custom_id=}")

    match custom_id:
        case CUSTOM_ID.CATEGORY_SELECT:
            return events.category_select(body)
        case CUSTOM_ID.SUB_CATEGORY_SELECT:
            return events.sub_category_select(body)
        case CUSTOM_ID.SUB_CATEGORY_CANCEL_BUTTON:
            return events.sub_category_cancel_button(body)
        case CUSTOM_ID.REJECT_LINK_BUTTON:
            return events.reject(body)
        case CUSTOM_ID.APPROVE_LINK_MODAL:
            return events.approve_link_modal(body)
        case _:
            # invalid custom_id
            return {
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"{custom_id=}\n\n```{event.get('rawBody')}```",
                }
            }


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return res
