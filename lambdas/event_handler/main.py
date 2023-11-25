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

PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

APPROVE_LOG_CHANNEL_ID = 1173639682219847740
REJECT_LOG_CHANNEL_ID = 1173639815439335485


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(
        message,
        bytes.fromhex(auth_sig)
    )  # raises an error if unequal


def middleware(event, context):
    print(f"event {event}")  # debug print
    print(event["rawBody"])

    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # ping pong
    body = event.get('body')
    if body.get("type") == TYPE.PING:
        return {
            "type": 1
        }

    # button handler
    custom_id = body.get("data", {}).get("custom_id", None)
    print(f"{custom_id=}")

    if custom_id == CUSTOM_ID.CATEGORY_SELECT:
        link = body.get("message", {}).get("embeds", [])[0].get("url")
        category = body.get("data", {}).get("values", [None])[0]

        return {
            "type": INTERACTION_CALLBACK_TYPE.MODAL,
            "data": {
                "title": f"{category}",
                "custom_id": CUSTOM_ID.APPROVE_LINK_MODAL,
                "components": [
                    {
                        "type": COMPONENT_TYPE.ACTION_ROW,
                        "components": [
                            {
                                "type": COMPONENT_TYPE.TEXT_INPUT,
                                "custom_id": "title_input",
                                "label": "제목",
                                "style": TEXT_INPUT_STYLE.SHORT,
                                "min_length": 1,
                                "max_length": 1000,
                                "required": True
                            }
                        ]
                    },
                    {
                        "type": COMPONENT_TYPE.ACTION_ROW,
                        "components": [
                            {
                                "type": COMPONENT_TYPE.TEXT_INPUT,
                                "custom_id": "link_input",
                                "label": "링크",
                                "style": TEXT_INPUT_STYLE.SHORT,
                                "min_length": 1,
                                "max_length": 1000,
                                "value": link,
                                "required": True
                            }
                        ]
                    },
                    {
                        "type": COMPONENT_TYPE.ACTION_ROW,
                        "components": [
                            {
                                "type": COMPONENT_TYPE.TEXT_INPUT,
                                "custom_id": category,
                                "label": "카테고리",
                                "placeholder": category,
                                "style": TEXT_INPUT_STYLE.SHORT,
                                "min_length": 1,
                                "max_length": 1000,
                                "value": category,
                                "required": True
                            }
                        ]
                    },

                ]
            }
        }
    elif custom_id == CUSTOM_ID.REJECT_LINK_BUTTON:
        message_id = body.get('message', {}).get("id")
        channel_id = body.get('message', {}).get("channel_id")
        link = body.get("message", {}).get("embeds", [])[0].get("url")
        author = body["message"]["embeds"][0]["author"]["name"]
        user_id = body["member"]["user"]["id"]

        delete_message(channel_id, message_id)

        send_message(
            REJECT_LOG_CHANNEL_ID,
            {
                "embeds": [
                    {
                        "title": "거절된 링크",
                        "color": 15670845,
                        "description": f"**링크**: `{link}`\n**작성자**: {author}\n**처리자**: <@{user_id}>"
                    }
                ]
            }
        )

        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"거절완료",
                "flags": 64  # 64 is the flag for ephemeral messages
            }
        }
    elif custom_id == CUSTOM_ID.APPROVE_LINK_MODAL:
        title = body["data"]["components"][0]["components"][0]["value"]
        link = body["data"]["components"][1]["components"][0]["value"]
        full_category = body["data"]["components"][2]["components"][0]["custom_id"]
        category, subcategory = full_category.split(" - ")
        author = body["message"]["embeds"][0]["author"]["name"]

        OWNER = "GaeBari"
        REPO = "GaeBari.github.io"
        WORKFLOW_ID = 75960089

        data = json.dumps({
            "ref": "main",
            "inputs": {
                "title": title,
                "link": link,
                "author": author,
                "category": category,
                "subcategory": subcategory,
            }
        })

        requests.post(
            f'https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches',
            headers={
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {GITHUB_TOKEN}',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data=data
        )

        message_id = body.get('message', {}).get("id")
        channel_id = body.get('message', {}).get("channel_id")
        user_id = body["member"]["user"]["id"]
        delete_message(channel_id, message_id)

        send_message(
            APPROVE_LOG_CHANNEL_ID,
            {
                "embeds": [
                    {
                        "title": title,
                        "color": 4582179,
                        "description": f"**링크**: `{link}`\n**카테고리**: {category}\n**서브카테고리**: {subcategory}\n**작성자**: {author}\n**처리자**: <@{user_id}>"
                    }
                ]
            }
        )

        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"처리완료",
                "flags": 64  # 64 is the flag for ephemeral messages
            }
        }

    return {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "tts": False,
            "content": f"{custom_id=}\n\n```{event.get('rawBody')}```",
            "embeds": [],
            "allowed_mentions": [],
        }
    }


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return res
