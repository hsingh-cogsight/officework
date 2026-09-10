"""Tracks the newest message timestamp we've already notified on,
per resource (the watched channel, and each chat id), so restarts
don't re-notify and polling doesn't double-fire.
"""
import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "..", ".watch_state.json")


def _load() -> dict:
    if not os.path.exists(_PATH):
        return {}
    with open(_PATH, "r") as f:
        return json.load(f)


def _save(state: dict) -> None:
    with open(_PATH, "w") as f:
        json.dump(state, f)


def get_last_seen(resource_key: str) -> str | None:
    return _load().get(resource_key)


def set_last_seen(resource_key: str, timestamp: str) -> None:
    state = _load()
    current = state.get(resource_key)
    if current is None or timestamp > current:
        state[resource_key] = timestamp
        _save(state)
