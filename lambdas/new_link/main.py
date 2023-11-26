import json
import os
import requests
from dataclasses import dataclass

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

CHANNEL_ID = 1173627431609962639
TOKEN = os.environ.get("DISCORD_TOKEN")


def lambda_handler(event, context):
    link = event.get("link")
    author = event.get("author")
    created_at = event.get("created_at")

    send_message(
        CHANNEL_ID,
        {
            "content": "",
            "embeds": [
                {
                    "title": "새 링크가 추가되었습니다.",
                    "description": f"**링크**: {link}\n**작성자**: `{author}`\n**시간**: `{created_at}`",
                    "url": link,
                    "color": 5814783,
                    "author": {
                        "name": f"{author}"
                    }
                }
            ],
            "components": [
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.STRING_SELECT,
                            "custom_id": CUSTOM_ID.CATEGORY_SELECT,
                            "placeholder": "카테고리",
                            "min_values": 1,
                            "max_values": 1,
                            "options": [
                                {
                                    "label": c,
                                    "value": c,
                                } for c in CATEGORY_OPTIONS.keys()
                            ],
                        },
                    ]
                },
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.BUTTON,
                            "label": "거절",
                            "style": BUTTON_STYLE.DANGER,
                            "custom_id": CUSTOM_ID.REJECT_LINK_BUTTON,
                        }
                    ]
                },
            ]
        }
    )

    return {
        "message": "success"
    }
