"""Delegated Graph auth via device code flow.

Run this module's `get_token()` once interactively (it will print a
device-login URL + code). After that, the token cache on disk lets
every later run refresh silently with no browser interaction --
until Azure AD forces a re-consent (permission change, revoked
session, etc.), at which point the device code prompt returns.
"""
import atexit
import os

import msal

from . import config

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".token_cache.json")

_cache = msal.SerializableTokenCache()
if os.path.exists(CACHE_PATH):
    _cache.deserialize(open(CACHE_PATH, "r").read())


def _save_cache():
    if _cache.has_state_changed:
        with open(CACHE_PATH, "w") as f:
            f.write(_cache.serialize())


atexit.register(_save_cache)

_app = None


def _get_app() -> msal.PublicClientApplication:
    global _app
    if _app is None:
        _app = msal.PublicClientApplication(
            config.AZURE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}",
            token_cache=_cache,
        )
    return _app


def get_token() -> str:
    app = _get_app()
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(config.GRAPH_SCOPES, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=config.GRAPH_SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to create device flow: {flow}")
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(f"Graph auth failed: {result.get('error_description')}")

    _save_cache()
    return result["access_token"]
