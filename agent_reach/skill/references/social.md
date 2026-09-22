# Social media and communities

Xiaohongshu, Twitter/X, Bilibili, V2EX, Reddit, Facebook, Instagram.

## Xiaohongshu (multiple backends)

Xiaohongshu has three backends. **Run `agent-reach doctor --json` first and see which `active_backend` xiaohongshu is using**, then use that command group.

### Backend A: OpenCLI (preferred on desktop)

```bash
# Search notes
opencli xiaohongshu search "query" -f yaml

# Read note body plus engagement (use the full URL from search results, including xsec_token)
opencli xiaohongshu note "NOTE_URL" -f yaml

# Comments (nested replies included)
opencli xiaohongshu comments NOTE_ID -f yaml

# Home recommendation feed
opencli xiaohongshu feed -f yaml

# Public notes on a user profile
opencli xiaohongshu user USER_ID -f yaml
```

> Chrome must be open with the OpenCLI extension installed. OpenCLI uses only a
> Chrome session the user already has and explicitly controls. Agent Reach does
> not log the user in, and it does not read browser cookies.
> `agent-reach configure xhs-cookies` does not inject cookies into OpenCLI.
> If there is no existing session, do not log in automatically. Use backend B
> or C, and configure it with that backend's manual Cookie-Editor export flow.

### Backend B: xiaohongshu-mcp (server deployments)

```bash
# Before authenticating, have the user export cookies manually with Cookie-Editor, then import them explicitly
agent-reach configure xhs-cookies

# Read-only check of the current status
mcporter call xiaohongshu.check_login_status --timeout 120000

# Search
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000

# Note detail plus comments (take feed_id and xsec_token from search results)
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

> The first call downloads about 150MB of headless browser. Always pass `--timeout 120000`.
> Authentication is only the manual Cookie-Editor export. After import, run `check_login_status` first.
> That explicit command saves and imports the user-provided same-site cookie set for xiaohongshu.com.
> The user should confirm the scope. Cookies outside the xiaohongshu.com domain are ignored.

### Backend C: xhs-cli (legacy fallback; upstream stopped updating in 2026-03)

```bash
xhs search "query"          # search
xhs read NOTE_ID_OR_URL     # read a note (must use the URL/ID from search results, not a bare note_id)
xhs comments NOTE_ID_OR_URL # comments
xhs hot                     # trending
xhs feed                    # recommendations
```

> Known to be unstable: `xhs user` / `xhs user-posts` / `xhs favorites` may return an API error (upstream stopped updating and nobody is fixing it). New installs should use backend A or B directly.

### Shared caveats

> **Auth boundary**: Agent Reach must not perform Xiaohongshu login for the user, and must not read browser cookies. OpenCLI may use only a Chrome session the user already has and explicitly controls. xiaohongshu-mcp and legacy tools use a manual Cookie-Editor export.
>
> **xsec_token limit**: Xiaohongshu requires the xsec_token mechanism. **You cannot read a note from a bare note_id.** The correct flow is: search or load the feed first, then read with the full URL or ID from those results. All three backends work this way.
>
> **Rate limits**: high-frequency requests (batch search, deep comment paging) trigger captchas, and the platform limit cannot be bypassed. Wait 2–3 seconds between operations.
>
> **Write operations (post / comment / like)**: stay read-only. xhs-cli v0.6.x write operations can return 406 because of signature issues.

## Twitter/X (twitter-cli)

### Auth prerequisites

Cookies saved through the hidden prompt of `agent-reach configure twitter-cookies` are only for `agent-reach doctor` to check that explicit credentials are present. `doctor` does not run the upstream `twitter status`, and it does not configure the current shell. Before any `twitter` command below, explicitly provide these in the same shell or in the child-process environment:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

### Stable commands

```bash
# Home timeline (most stable)
twitter feed -n 20

# Read a single tweet (including replies)
twitter tweet URL_OR_ID

# Read a long-form post / X Article
twitter article URL_OR_ID

# User timeline
twitter user-posts @username -n 20

# User profile
twitter user @username
```

### Commands that may be unstable

```bash
# Search tweets (Twitter changes GraphQL endpoints often; may 404)
twitter search "query" -n 10

# likes (after 2024 you can only see your own; platform limit)
twitter likes
```

### Retry chain when search fails (run in order; stop at the first success)

1. Retry once directly (transient failures are common): `twitter search "query" -n 10`
2. Upgrade and try again: `pipx upgrade twitter-cli && twitter search "query" -n 10`
3. Switch to the OpenCLI fallback (desktop, reuse the browser login state): `opencli twitter search "query" -f yaml`
4. If none of those work, route around the failure with stable commands such as `twitter feed` or `twitter user-posts @somebody`

### Important caveats

> **Install**: `pipx install twitter-cli` (make sure it is v0.8.5+)
>
> **Auth**: use only a manual Cookie-Editor export, then set `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` explicitly. Do not rely on automatic browser reads.
>
> **IP risk controls**: do not call frequently from a VPS or datacenter IP, especially followers/following, because of account-ban risk. Use a residential proxy or a local environment.
>
> **OpenCLI fallback**: if OpenCLI is installed on the desktop, the full set `opencli twitter search/article/user-posts -f yaml` works (browser login state, no cookie environment variables).
>
> **Output format**: prefer `--yaml` or `--json` for structured output. That is easier for an AI agent.

## Bilibili

> ⚠️ **Do not use yt-dlp to read Bilibili** (risk controls now return 412 across the board; verified, no workaround). Use bili-cli / OpenCLI.

```bash
# Search / trending / video details (bili-cli, read-only, no login)
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx

# Subtitles (OpenCLI, needs desktop Chrome)
opencli bilibili subtitle BVxxx
```

> Full commands (audio transcription, direct API fallback) are in [references/video.md](video.md).

## V2EX (public API)

No authentication. Call the public API directly.

### Hot topics

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### Node topics

```bash
# node_name examples: python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### Topic detail

```bash
# topic_id comes from the URL, e.g. https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### Topic replies

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### User info

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python example

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# Fetch hot topics
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} replies)")

# Fetch node topics
node_topics = ch.get_node_topics("python", limit=5)

# Fetch topic detail plus replies
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])

# Fetch user info
user = ch.get_user("Livid")
```

> **Node list**: https://www.v2ex.com/planes

## Reddit (multiple backends, login required)

**Reddit has no zero-config path.** Anonymous `.json` endpoints are blocked (403), and since 2025-11 the official API's manual review almost never approves new apps. Both backends depend on a login session. Run `agent-reach doctor --json` first and check reddit's `active_backend`. Access from mainland China needs a proxy.

### Backend A: OpenCLI (preferred on desktop, reuse the browser login state)

```bash
# Search posts
opencli reddit search "query" -f yaml

# Read the full post plus comments
opencli reddit read POST_ID -f yaml

# Browse a subreddit / hot / Popular
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml

# Subreddit metadata (subscriber count, description)
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> Chrome must be open and already logged in to reddit.com in that browser.

### Backend B: rdt-cli (legacy / server fallback; upstream stopped updating in 2026-03)

```bash
rdt search "query" --limit 10   # search posts
rdt read POST_ID                # read the full post plus comments
rdt sub python --limit 20       # browse a subreddit
rdt popular --limit 10          # browse hot posts
rdt all --limit 10              # browse /r/all
```

> **Install**: `pipx install 'git+https://github.com/public-clis/rdt-cli.git'` (the PyPI release is behind; install v0.4.2+ from GitHub). Run `rdt login` before search and read (on a server with no browser, write the cookie manually; see the doctor hint).
> Prefer `--yaml` output. It is easier for an AI agent.

### Advanced option: official API + PRAW (only for users who already have credentials)

Users who registered a Reddit script app before 2025-11 (and still hold client_id/client_secret) can use PRAW against the official API (100 QPM free). New applications need manual review, and personal projects are almost never approved. **Do not recommend this path to new users.**

## Facebook (OpenCLI, login required)

Facebook goes through OpenCLI and reuses the facebook.com login session in the user's Chrome. Run `agent-reach doctor --json` first and check facebook's `active_backend`. It should normally be `OpenCLI`. Do not recommend Jina, Exa, or the Graph API as the default path.

```bash
# Search users / pages / posts
opencli facebook search "query" -f yaml

# User or page info
opencli facebook profile zuck -f yaml

# News Feed for the current account
opencli facebook feed --limit 10 -f yaml

# Groups visible to the current account, and their recent activity
opencli facebook groups --limit 20 -f yaml
```

> Chrome must be open with the OpenCLI extension installed, and facebook.com must already be logged in. Facebook Groups currently only promises the group list and recent activity visible to the current account. It does not promise an API for arbitrary group posts and comments.

## Instagram (OpenCLI, login required)

Instagram goes through OpenCLI and reuses the instagram.com login session in the user's Chrome. Run `agent-reach doctor --json` first and check instagram's `active_backend`. It should normally be `OpenCLI`. Do not restore instaloader by default. Historically its cookies, 401s, and 429s were unstable.

```bash
# Search users (this is not a site-wide post keyword search)
opencli instagram search "query" -f yaml

# User profile
opencli instagram profile nasa -f yaml

# A user's recent posts
opencli instagram user nasa --limit 12 -f yaml

# Explore / Discover
opencli instagram explore --limit 20 -f yaml

# Saved items for the current account
opencli instagram saved --limit 20 -f yaml
```

> Chrome must be open with the OpenCLI extension installed, and instagram.com must already be logged in. `instagram search` searches users. To read posts, resolve a username first, then use `instagram user USERNAME`. If you see 429 or login required, have the user log in again in Chrome and lower the request rate.
