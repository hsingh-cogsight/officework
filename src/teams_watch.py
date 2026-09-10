import re

from . import config, graph_client, state_store, telegram_notify

_TAG_RE = re.compile(r"<[^>]+>")


def _clean_body(message: dict) -> str:
    body = (message.get("body") or {}).get("content") or ""
    text = _TAG_RE.sub(" ", body)
    return " ".join(text.split())[:500]


def _sender_name(message: dict) -> str:
    frm = (message.get("from") or {}).get("user") or {}
    return frm.get("displayName") or "Unknown"


def _notify(source: str, message: dict) -> None:
    sender = _sender_name(message)
    text = _clean_body(message) or "(no text / attachment or reaction)"
    telegram_notify.send(f"<b>{source}</b>\n<b>{sender}:</b> {text}")


def _poll_resource(resource_key: str, messages: list[dict], source_label: str, only_if_mentions: bool) -> None:
    last_seen = state_store.get_last_seen(resource_key)
    # newest first from Graph -> process oldest to newest so notifications arrive in order
    messages = sorted(messages, key=lambda m: m.get("createdDateTime", ""))

    newest_seen = last_seen
    for message in messages:
        created = message.get("createdDateTime")
        if not created:
            continue
        if newest_seen is None or created > newest_seen:
            newest_seen = created

        is_new = last_seen is not None and created > last_seen
        if not is_new:
            continue
        if only_if_mentions and not graph_client.message_mentions_user(message, config.GRAPH_MY_USER_ID):
            continue
        _notify(source_label, message)

    if newest_seen is not None:
        state_store.set_last_seen(resource_key, newest_seen)


def poll_once() -> None:
    channel_messages = graph_client.list_channel_messages(
        config.TEAMS_WATCH_TEAM_ID, config.TEAMS_WATCH_CHANNEL_ID
    )
    _poll_resource(
        resource_key=f"channel:{config.TEAMS_WATCH_CHANNEL_ID}",
        messages=channel_messages,
        source_label="Watched channel",
        only_if_mentions=False,
    )

    for chat in graph_client.list_my_chats():
        chat_id = chat["id"]
        chat_name = chat.get("topic") or "Direct/Group chat"
        chat_messages = graph_client.list_chat_messages(chat_id)
        _poll_resource(
            resource_key=f"chat:{chat_id}",
            messages=chat_messages,
            source_label=f"Mentioned in: {chat_name}",
            only_if_mentions=True,
        )
