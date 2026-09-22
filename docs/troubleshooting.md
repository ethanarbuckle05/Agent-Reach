# Troubleshooting

## Xueqiu: API returns 400

**Symptom:** `agent-reach doctor` shows Xueqiu as ⚠️ and reports `HTTP Error 400`

**Cause:** The Xueqiu API requires a login cookie. It cannot be obtained anonymously.

**Fix:** Log in to xueqiu.com in Chrome, then run:

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

Run `agent-reach doctor` again and confirm it is back to ✅. When the cookie expires, run the same command again.

---

## Boss Zhipin: `boss status` says logged in, but search returns `AUTH_EXPIRED`

**Symptom:** `boss status` / `status --live` returns `logged_in: true` (sometimes with a username),
but `boss ... search` immediately returns `{"code": "AUTH_EXPIRED", "message": "用户未登录"}` (the upstream Boss CLI's Chinese for "user is not logged in").
The dedicated Chrome may also be sitting on a URL that contains `_security_check`, which looks like an anti-bot slider.

**Cause:** Boss has two login-state stores, and they authenticate different channels:

| Store | Who uses it |
|---|---|
| `~/.boss-agent/auth/session.enc` | `boss status` / `status --live`, and low-risk httpx operations (`detail` / `cities` / `job_card_httpx`). CDP search also reads it (if it cannot be read, search reports not logged in immediately), but when a real Chrome context is reused that cookie never actually takes effect |
| Browser cookies inside `~/.boss-chrome-profile` | The credentials that search / greet and other high-risk operations actually send in `existing-browser` strict CDP mode |

`boss status` only checks the local session.enc. If old credentials from a few days ago are stored locally and the dedicated Chrome
profile itself is not logged in, it still reports `logged_in: true` — that is not proof the login is valid.
The `_security_check` page is an anti-bot challenge. **It can appear even when you are logged in**, so it cannot be used to judge login state.
Together, the two are easy to misread: "the browser is not logged in" gets treated as "stuck on the slider".

> Do not delete either store. If session.enc is missing, CDP search fails before it connects to the browser.
> When you need to refresh it, run `login --cdp`. Do not delete the file by hand.

**How to decide:**

1. `AUTH_EXPIRED` is ground truth — if it appears, the browser is not logged in, no matter what `boss status` says;
2. The boss row in `agent-reach doctor` probes the browser directly for a `wt2` cookie. Trust that;
3. `boss status` is only a hint. The page URL is not evidence at all.

**Fix:** In the dedicated Chrome window, visually confirm and log in to zhipin.com manually, then sync the login state:

```bash
boss --cdp-url http://localhost:9222 login --cdp
agent-reach doctor    # the boss row message should show "login cookie (wt2) is present in the browser"
```

> After you launch the dedicated Chrome, the first step is always to have the user visually confirm the login state. Do not substitute `boss status`.

---

## Twitter/X: twitter-cli cannot connect

**Symptom:** `twitter search` or another command returns an error

**Cause:** twitter-cli needs the `TWITTER_AUTH_TOKEN` and `TWITTER_CT0`
environment variables to reach the Twitter API. Values saved by `agent-reach configure twitter-cookies`
are only for doctor to check that the configuration is complete. Doctor does not run upstream auth, and it does not set the current
shell. If your network needs a proxy to reach x.com, configure a proxy as well.

**Fix:**

### Option 1: Set a proxy with environment variables

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "test" -n 1
```

### Option 2: Use a system-wide proxy

Let the proxy tool take all network traffic, so twitter-cli requests go through it too:

```bash
# macOS — turn on Enhanced Mode in ClashX / Surge
# Linux — proxychains or tun2socks
proxychains twitter search "test" -n 1
```

### Option 3: Skip twitter-cli and search with Exa

When twitter-cli is unavailable, search Twitter content with Exa directly:

```bash
mcporter call exa.web_search_exa query="site:x.com keywords" numResults=5
```

### Option 4: Check authentication

```bash
twitter check
```

> If it returns "Missing credentials", set
> `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` in the environment of the process that runs the command.
>
> **Fallback:** If you already installed the bird CLI (`npm install -g @steipete/bird`), it works too. Agent Reach detects installed tools automatically.
