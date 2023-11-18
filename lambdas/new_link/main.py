import json
import os
import requests
from dataclasses import dataclass

CHANNEL_ID = 1173627431609962639
TOKEN = os.environ.get("DISCORD_TOKEN")
CATEGORY_OPTIONS = [
    "개발 - C/C++",
    "개발 - 프론트엔드 / 웹",
    "개발 - Java",
    "개발 - Python",
    "개발 - Go",
    "개발 - 플러터",
    "개발 - 언어 기타",
    "개발 - 언어 비교",
    "운영 - DevOps",
    "운영 - AWS",
    "운영 - Observability",
    "CS - 알고리즘",
    "CS - 데이터베이스 DB",
    "CS - 네트워크",
    "CS - Test",
    "CS - Linux",
    "CS - 디자인패턴",
    "게임 - 유니티",
    "게임 - 게임 서버",
    "보안 - 보안 일반",
    "비개발 - 디자인",
    "기타 - 개발 일반 (개발 문화/철학/방법론, 개발자 성장)",
    "기타 - Git",
    "기타 - AI",
    "기타 - 데이터 사이언스",
    "기타 - 미분류",
]


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


def lambda_handler(event, context):
    link = event.get("link")
    author = event.get("author")
    created_at = event.get("created_at")

    res = requests.post(
        f"https://discordapp.com/api/channels/{CHANNEL_ID}/messages",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {TOKEN}"
        },
        data=json.dumps({
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
                                } for c in CATEGORY_OPTIONS
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
                            "custom_id": "reject_link"
                        }
                    ]
                },
            ]
        })
    )

    if res.status_code != 200:
        raise Exception(
            f"Failed to send message to Discord: {res.status_code} {res.text}")

    return {
        "message": "success"
    }
