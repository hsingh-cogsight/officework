# Teams → Telegram notifier (POC, piece 1)

Polls Microsoft Teams every `POLL_INTERVAL_SECONDS` and sends a Telegram
message when:
- any message lands in one specific watched channel, or
- you're @mentioned in any 1:1/group chat.

Reply-from-Telegram-back-to-Teams (piece 2) is not built yet.

## Known POC limitation

Mention detection covers **chats** (1:1 and group) via `/me/chats`. It does
**not** yet scan every channel in every team you belong to for mentions —
only the one channel configured as `TEAMS_WATCH_CHANNEL_ID` (where it
notifies on *all* messages, not just mentions). Extending mention-detection
to all channels means enumerating every joined team/channel via
`Team.ReadBasic.All` + `Channel.ReadBasic.All`, which is a straightforward
follow-up if you need it.

## Setup

### 1. Azure AD app registration

Portal → Azure Active Directory → App registrations → New registration.

- Supported account types: accounts in your organizational directory only
  (single tenant) is fine for personal use.
- Authentication → enable "Allow public client flows" (required for device
  code login — no client secret needed).
- API permissions → Microsoft Graph → **Delegated**:
  - `ChannelMessage.Read.All`
  - `Chat.Read`
  - `Team.ReadBasic.All`
  - `Channel.ReadBasic.All`
  - `User.Read`
  - `offline_access` (usually included by default)
- Click "Grant admin consent" if your tenant requires it for these scopes
  (it likely does — `ChannelMessage.Read.All` is commonly admin-gated). If
  you're not a tenant admin, get one to click this button once; the app
  itself needs no further changes from them after that.

Copy the **Application (client) ID** and **Directory (tenant) ID** into `.env`.

### 2. Find the IDs you're watching

- `GRAPH_MY_USER_ID`: call `GET https://graph.microsoft.com/v1.0/me` (e.g.
  via [Graph Explorer](https://developer.microsoft.com/graph/graph-explorer))
  and copy `id`.
- `TEAMS_WATCH_TEAM_ID` / `TEAMS_WATCH_CHANNEL_ID`: `GET /me/joinedTeams`
  for the team id, then `GET /teams/{team-id}/channels` for the channel id.

### 3. Telegram bot

- Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
  into `TELEGRAM_BOT_TOKEN`.
- Send your new bot any message, then visit
  `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `message.chat.id`
  into `TELEGRAM_CHAT_ID`.

### 4. Run

```bash
cp .env.example .env   # fill in the values above
pip install -r requirements.txt
python main.py
```

First run prints a device-login URL + code — open it in a browser and sign
in as yourself. After that it refreshes silently from `.token_cache.json`
(gitignored — don't commit it, it holds your refresh token).
