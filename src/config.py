import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


AZURE_TENANT_ID = _require("AZURE_TENANT_ID")
AZURE_CLIENT_ID = _require("AZURE_CLIENT_ID")

TEAMS_WATCH_TEAM_ID = _require("TEAMS_WATCH_TEAM_ID")
TEAMS_WATCH_CHANNEL_ID = _require("TEAMS_WATCH_CHANNEL_ID")
GRAPH_MY_USER_ID = _require("GRAPH_MY_USER_ID")

TELEGRAM_BOT_TOKEN = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _require("TELEGRAM_CHAT_ID")

POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "30"))

GRAPH_SCOPES = [
    "ChannelMessage.Read.All",
    "Chat.Read",
    "Team.ReadBasic.All",
    "Channel.ReadBasic.All",
    "User.Read",
]
