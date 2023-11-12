import json
import os
import requests

CHANNEL_ID = 1173171908922048653
TOKEN = os.environ.get("DISCORD_TOKEN")

def lambda_handler(event, context):
    link = event.get("link")
    author = event.get("author")
    created_at = event.get("created_at")

    res = requests.post(
        f"https://discordapp.com/api/channels/{CHANNEL_ID}/messages",
        headers = {
            "Content-Type":"application/json",
            "Authorization":f"Bot {TOKEN}"
        },
        data = json.dumps({
            "content": "",
            "embeds": [
                {
                    "title": "새 링크가 추가되었습니다.",
                    "description": f"**링크**: {link}\n**작성자**: `{author}`\n**시간**: `{created_at}`",
                    "url": link,
                    "color": 5814783
                }
            ],
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "승인",
                            "style": 1,
                            "custom_id": "approve_link"
                        },
                        {
                            "type": 2,
                            "label": "거절",
                            "style": 4,
                            "custom_id": "reject_link"
                        }
                    ]
                }
            ]
        })
    )

    if res.status_code != 200:
        raise Exception(f"Failed to send message to Discord: {res.status_code} {res.text}")

    return {
        "message" : "success"
    }
