# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

### 🐛 Bug Fixes

#### 🔐 Boss Zhipin — login-state misread (two credential stores)

- **Root cause:** Boss has two login-state stores that do not stand in for each other — the local `~/.boss-agent/auth/session.enc`
  and the browser cookies inside the dedicated Chrome profile. `boss status` / `status --live` **only check the former**
  (a leftover credential store from the Bridge/httpx era), while search in `existing-browser` strict CDP mode uses the browser cookies.
  When old local credentials exist and the browser is not logged in, `boss status` reports `logged_in: true`, which leads the Agent
  to skip login and search, then hit `AUTH_EXPIRED`. The old runbook also forbade treating `_security_check`
  as not-logged-in, and the two rules together pushed the Agent into the wrong "anti-bot slider" branch.
- **Fix:** `check()` adds a 4th read-only probe, `_cdp_zhipin_login_cookie()`, implemented as a minimal WebSocket
  client using only the standard library. It asks the CDP browser itself (`Storage.getCookies`) whether a zhipin
  `wt2` cookie is present, and **trusts the browser**. It adds no dependency, does not launch a browser, and does not run a search.
  No wt2 → it explicitly reports that the browser is not logged in and search will return `AUTH_EXPIRED`, and points to user login plus
  `login --cdp`. If the probe fails → it reports that the login state is unknown. The security-check page hint also includes the browser cookie status.
- **Runbook correction:** removed the misleading rule "trust only `boss status` to judge login state", and use doctor's
  browser-cookie probe instead. After launching the dedicated Chrome, **force a pause so the user can visually confirm** the login state.
  `AUTH_EXPIRED` is ground truth (go straight through the login flow; do not explain it as a security check).
  Treat `_security_check` as a slider only when there is no `AUTH_EXPIRED`.

### ✨ Features

#### 🎯 Boss Zhipin channel

- Added a `boss` channel: search jobs and fetch full JD text through boss-agent-cli plus CDP on a real Chrome.
- `check()` runs four read-only probes (is boss-agent-cli installed → is port 9222 open → is there a zhipin tab
  → is there a `wt2` login cookie in the browser).
- Fetching uses the public API (`search_jobs` + `job_card_browser` + `browser_source="existing-browser"`).
- `agent-reach install --system --channels=boss` can install the backend pinned to a fixed upstream boss-agent-cli
  commit (#403–#407 are merged into master). Switch back to a version constraint after upstream publishes a release.
- The skill and install guide support "Set up Boss Zhipin for me": the Agent starts a dedicated Chrome that listens only on the loopback address,
  the user logs in manually, and the Agent then verifies the login state and the CDP path.
- The pinned dependency moved from fork snapshot `8ff6bd3` to upstream commit `4c991b7` (#403–#407 are merged into
  master): a logged-in CDP session can be reused directly, and search can pass `--browser-source existing-browser`
  to forbid a headless fallback.
- code 37 is classified from the original wording: an environment anomaly is `ENVIRONMENT_RISK` and stops immediately; a refresh is allowed only once, and only when token/stoken expiry is explicit. Reuse the dedicated Chrome profile long-term and call it less often.

## [1.3.1] - 2026-03-27

### 🐛 Bug Fixes

#### 📈 Xueqiu — full fix

- **Fixed the root cause of 400 errors:** `_ensure_cookies()` visiting the homepage only obtained `acw_tc` (the anti-DDoS token). `xq_a_token` is generated dynamically by Xueqiu's frontend JavaScript and cannot be obtained with a plain HTTP request. Added a three-level cookie load strategy: (1) read the config file (saved by `--from-browser`) → (2) extract automatically from the local Chrome browser (requires browser-cookie3) → (3) homepage fallback
- **Fixed User-Agent:** `"agent-reach/1.0"` was rejected by Xueqiu's anti-bot system. Switched to a real Chrome UA
- **Fixed the missing `Referer` header:** every API request now sends `Referer: https://xueqiu.com/`
- **Fixed the `get_hot_posts()` endpoint:** the old endpoint `/statuses/hot/listV3.json` is deprecated (it returns an empty body). Switched to `/v4/statuses/public_timeline_by_category.json`, and parse the `item.data` JSON string for author/likes/text
- **Fixed `urllib.request.quote` → `urllib.parse.quote`:** use the correct module explicitly
- **Fixed `configure --from-browser` not extracting Xueqiu cookies:** added Xueqiu to `PLATFORM_SPECS`, and save only when `xq_a_token` is present
- **Corrected misleading docs:** "no configuration needed" / "public API, no login required" in README/SKILL.md now say a browser cookie is required
- **Clearer errors:** when `check()` fails, it suggests `configure --from-browser chrome` instead of saying a proxy might be needed

---

## [1.3.0] - 2026-03-12

### 🆕 New Channels

#### 💻 V2EX
- Hot topics, node topics, topic detail + replies, user profile via public JSON API
- Zero config — no auth, no proxy, no API key required
- `get_hot_topics(limit)`, `get_node_topics(node_name, limit)`, `get_topic(id)`, `get_user(username)`

### 📈 Improvements

- Channel count: 14 → 15

---

## [1.1.0] - 2025-02-25

### 🆕 New Channels

#### ~~📷 Instagram~~ (removed — upstream blocked)
- ~~Read public posts and profiles via [instaloader](https://github.com/instaloader/instaloader)~~
- **Removed:** Instagram's aggressive anti-scraping measures broke all available open-source tools (instaloader, etc.). See [instaloader#2585](https://github.com/instaloader/instaloader/issues/2585). Will re-add when upstream recovers.

#### 💼 LinkedIn
- Read person profiles, company pages, and job details via [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server)
- Search people and jobs via MCP, with Exa fallback
- Fallback to Jina Reader when MCP is not configured

#### 🏢 Boss Zhipin
- QR code login via [mcp-bosszp](https://github.com/mucsbr/mcp-bosszp)
- Job search and recruiter greeting via MCP
- Fallback to Jina Reader for reading job pages

### 📈 Improvements

- Channel count: 9 → 12
- `agent-reach doctor` now detects all 12 channels
- CLI: added `search-linkedin`, `search-bosszhipin` subcommands
- Updated install guide with setup instructions for new channels

---

## [1.0.0] - 2025-02-24

### 🎉 Initial Release

- 9 channels: Web, Twitter/X, YouTube, Bilibili, GitHub, Reddit, XiaoHongShu, RSS, Exa Search
- CLI with `read`, `search`, `doctor`, `install` commands
- Unified channel interface — each platform is a single pluggable Python file
- Auto-detection of local vs server environments
- Built-in diagnostics via `agent-reach doctor`
- Skill registration for Claude Code / OpenClaw / Cursor
