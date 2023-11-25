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
        }
    )

    return {
        "message": "success"
    }
