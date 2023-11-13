import json
import os
from dataclasses import dataclass
import re

import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


@dataclass
class INTERACTION_CALLBACK_TYPE:
    # https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object
    PONG = 1
    ACK_NO_SOURCE = 2
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9
    PREMIUM_REQUIRED = 10


@dataclass
class TYPE:
    PING = 1
    BUTTON = 3
    MODAL = 5


@dataclass
class CUSTOM_ID:
    CATEGORY_SELECT = "category_select"
    APPROVE_LINK_MODAL = "approve_link_modal"
    REJECT_LINK_BUTTON = "reject_link"


@dataclass
class COMPONENT_TYPE:
    # https://discord.com/developers/docs/interactions/message-components#component-object-component-types
    ACTION_ROW = 1
    BUTTON = 2
    STRING_SELECT = 3
    TEXT_INPUT = 4
    USER_SELECT = 5
    ROLE_SELECT = 6
    MENTIONABLE_SELECT = 7
    CHANNEL_SELECT = 8


@dataclass
class TEXT_INPUT_STYLE:
    # https://discord.com/developers/docs/interactions/message-components#text-input-object-text-input-interaction
    SHORT = 1
    PARAGRAPH = 2


@dataclass
class BUTTON_STYLE:
    # https://discord.com/developers/docs/interactions/message-components#button-object-button-styles
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


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


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def delete_message(channel_id: int, message_id: int):
    res = requests.delete(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
    )
    if res.status_code != 204:
        raise Exception(
            f"Failed to delete message: {res.status_code} {res.text}")


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
    if ping_pong(body):
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
                                # "value": "",
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

        delete_message(channel_id, message_id)

        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"거절되었습니다.\n||{link}||",
                # "flags": 64  # 64 is the flag for ephemeral messages
            }
        }
    elif custom_id == CUSTOM_ID.APPROVE_LINK_MODAL:
        title = body["data"]["components"][0]["components"][0]["value"]
        link = body["data"]["components"][1]["components"][0]["value"]
        full_category = body["data"]["components"][2]["components"][0]["custom_id"]
        category, subcategory = full_category.split(" - ")
        author = body["message"]["embeds"][0]["author"]["name"]

        OWNER = "junah201"
        REPO = "GaeBari.github.io"
        WORKFLOW_ID = 75948897

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
        delete_message(channel_id, message_id)

        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"처리완료.\n||{link}||",
                # "flags": 64  # 64 is the flag for ephemeral messages
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
