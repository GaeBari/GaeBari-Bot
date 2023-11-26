try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

APPROVE_LOG_CHANNEL_ID = 1173639682219847740
REJECT_LOG_CHANNEL_ID = 1173639815439335485


def category_select(body: dict) -> dict:
    """카테고리를 선택했을 때 발생하는 이벤트 핸들러"""

    link = body["message"]["embeds"][0]["url"]
    author = body["message"]["embeds"][0]["author"]["name"]
    category = body.get("data", {}).get("values", [None])[0]

    return {
        "type": INTERACTION_CALLBACK_TYPE.UPDATE_MESSAGE,
        "data": {
            "embed": [
                {
                    "title": "서브 카테고리 선택",
                    "description": f"**링크**: {link}\n**작성자**: `{author}`",
                    "url": link,
                    "author": {
                        "name": f"{author}"
                    },
                    "fields": [
                        {
                            "name": '카테고리',
                            "value": category
                        }
                    ],
                }
            ],
            "components": [
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.STRING_SELECT,
                            "custom_id": CUSTOM_ID.SUB_CATEGORY_SELECT,
                            "placeholder": "서브 카테고리",
                            "min_values": 1,
                            "max_values": 1,
                            "options": [
                                {
                                    "label": c,
                                    "value": f"{category}-{c}",
                                } for c in CATEGORY_OPTIONS[category]
                            ],
                        },
                    ]
                },
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.BUTTON,
                            "label": "취소",
                            "style": BUTTON_STYLE.DANGER,
                            "custom_id": CUSTOM_ID.SUB_CATEGORY_CANCEL_BUTTON,
                        }
                    ]
                },
            ],
        }
    }


def sub_category_select(body: dict) -> dict:
    """서브 카테고리를 선택했을 때 발생하는 이벤트 핸들러"""

    link = body["message"]["embeds"][0]["url"]
    author = body["message"]["embeds"][0]["author"]["name"]
    full_category = body.get("data", {}).get("values", [None])[0]

    return {
        "type": INTERACTION_CALLBACK_TYPE.MODAL,
        "data": {
            "title": f"{full_category}",
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
                            "custom_id": full_category,
                            "label": "카테고리",
                            "placeholder": full_category,
                            "style": TEXT_INPUT_STYLE.SHORT,
                            "min_length": 1,
                            "max_length": 1000,
                            "value": full_category,
                        }
                    ]
                },
            ]
        }
    }


def sub_category_cancel_button(body: dict) -> dict:
    """서브 카테고리 선택을 취소했을 때 발생하는 이벤트 핸들러"""

    link = body["message"]["embeds"][0]["url"]
    author = body["message"]["embeds"][0]["author"]["name"]

    return {
        "type": INTERACTION_CALLBACK_TYPE.UPDATE_MESSAGE,
        "data": {
            "content": "",
            "embed": [
                {
                    "title": "새 링크가 추가되었습니다.",
                    "description": f"**링크**: {link}\n**작성자**: `{author}`",
                    "url": link,
                    "color": 5814783,
                    "author": {
                        "name": f"{author}"
                    },
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
            ],
        }
    }


def reject(body: dict) -> dict:
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


def approve_link_modal(body: dict) -> dict:
    title = body["data"]["components"][0]["components"][0]["value"]
    link = body["data"]["components"][1]["components"][0]["value"]
    full_category = body["data"]["components"][2]["components"][0]["custom_id"]
    category, subcategory = full_category.split("-")
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
            "flags": 64
        }
    }
