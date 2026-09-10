import requests

from . import graph_auth

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _get(path: str, params: dict | None = None) -> dict:
    token = graph_auth.get_token()
    resp = requests.get(
        f"{GRAPH_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def list_channel_messages(team_id: str, channel_id: str) -> list[dict]:
    data = _get(f"/teams/{team_id}/channels/{channel_id}/messages", params={"$top": 50})
    return data.get("value", [])


def list_my_chats() -> list[dict]:
    data = _get("/me/chats", params={"$top": 50})
    return data.get("value", [])


def list_chat_messages(chat_id: str) -> list[dict]:
    data = _get(f"/chats/{chat_id}/messages", params={"$top": 50})
    return data.get("value", [])


def message_mentions_user(message: dict, user_id: str) -> bool:
    for mention in message.get("mentions", []) or []:
        mentioned_user = (mention.get("mentioned") or {}).get("user") or {}
        if mentioned_user.get("id") == user_id:
            return True
    return False
