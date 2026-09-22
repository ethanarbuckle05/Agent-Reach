---
name: agent-reach
description: >
  MUST USE when user wants to research/search/look up/find anything
  on the internet — e.g. research X across the web / research X for me /
  look up X / search for X / see what people think of X / what people are
  saying about X / research this topic.

  Also MUST USE when user mentions any platform or shares any URL/link:
  Xiaohongshu/xiaohongshu/xhs, Twitter/X, Bilibili/bilibili, Reddit, Facebook,
  Instagram, V2EX, LinkedIn/Boss Zhipin/recruiting/job hunting/jobs, YouTube,
  GitHub code search, Xiaoyuzhou podcasts, Xueqiu/stock quotes, RSS feeds,
  or any web URL.

  16 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: writing reports, data analysis, translation, or other content
  processing (this skill only fetches content from the internet); write
  operations such as posting, commenting, or liking; platforms that already
  have a dedicated skill (use that skill first).

  [Routing] SKILL.md contains the routing table and common commands. For
  complex cases, read the matching category under references/*.md as needed.
  Categories: search / social (Xiaohongshu/Twitter/Bilibili/V2EX/Reddit/Facebook/Instagram)
  / career (LinkedIn/Boss Zhipin) / dev (github) / web (pages/articles/RSS)
  / video (YouTube/Bilibili/podcasts) / finance (Xueqiu/stocks).
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — internet capability router

16 platforms, multiple backends. **When this skill exists, use it to reach
these platforms. Do not invent your own approach.**

## Standing rules (apply for the whole session)

1. **Health-check before acting**: for multi-backend or login-backed platforms
   (Xiaohongshu/Reddit/Bilibili/Twitter/Facebook/Instagram/Boss Zhipin), run
   `agent-reach doctor --json` first. When `active_backend` is populated, pick
   the command group from it. `active_backend: null` means Doctor skipped a
   live probe to avoid browser-cookie reads or remote writes. It does not mean
   no backend exists. Doctor results are a snapshot of one moment; the channel
   or login state may already have changed. If you suspect it is stale before
   a read-only command, reconfirm with that reference's health-check and
   recovery runbook (for example, the Boss Zhipin CDP troubleshooting in
   career.md).
2. **Announce what you use**: before you start, say "using agent-reach,
   platform X via backend Y".
3. **On failure, follow the retry chains in references.** Do not guess commands.
4. **For full-web research tasks**: combine platforms (Exa for search +
   Twitter/Reddit for discussion + Xiaohongshu/Bilibili for Chinese-language
   context), collect in parallel, then synthesize.
5. **Watch versions for the user**: after a substantial research or
   multi-platform task, run `agent-reach check-update` (fast, one API call).
   If a new version exists, add one line to the wrap-up: "Agent Reach has a
   new version vX.Y.Z. Paste this sentence to me to update: Update Agent Reach
   for me: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md".
   Do not interrupt the current task to update, and do not remind the user
   about the same version twice.

## Routing table

| User intent | Category | Details |
|---------|------|---------|
| Web search / code search | search | [references/search.md](references/search.md) |
| Xiaohongshu / Twitter / Bilibili / V2EX / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| Recruiting / jobs / LinkedIn / Boss Zhipin | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| Web pages / articles / RSS | web | [references/web.md](references/web.md) |
| YouTube / Bilibili / podcast transcripts | video | [references/video.md](references/video.md) |
| Xueqiu / stock quotes | finance | [references/finance.md](references/finance.md) |

## Zero-config quick commands

```bash
# Exa web search
mcporter call exa.web_search_exa query="query" numResults=5

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search
gh search repos "query" --sort stars --limit 10

# YouTube subtitles (never use yt-dlp for Bilibili; retry chain in video.md)
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# Bilibili search (bili-cli, no login needed)
bili search "query" --type video -n 5
```

## Login-backed platforms (pick the command group from doctor's active_backend)

Twitter note: cookies saved by `agent-reach configure twitter-cookies` are
only for `doctor` to check that the configuration is complete. `doctor` does
not run `twitter status`, and it does not configure the current shell. Before
running `twitter` directly, explicitly provide `TWITTER_AUTH_TOKEN` and
`TWITTER_CT0` in the child-process environment. Never print the values in
logs or command echo.

Xiaohongshu note: Agent Reach does not log the user in, and it does not read
browser cookies. OpenCLI may use only a Chrome session the user already has
and explicitly controls. If no such session exists, do not log in
automatically. Use a manual Cookie-Editor export, then configure
xiaohongshu-mcp or a legacy tool.

Boss Zhipin setup trigger: when the user says "Set up Boss Zhipin for me",
read the Boss section in `references/career.md` first. After you have install
approval, run `agent-reach install --env=local --system --channels=boss`. The
agent launches a dedicated Chrome for the user's OS, bound only to
`127.0.0.1:9222`. **The first step after launch is to pause and have the user
visually confirm** the window is logged in (avatar in the top-right). If it
is not, have the user log in or complete sign-in. After the user confirms,
verify with `boss --cdp-url http://localhost:9222 login --cdp` and
`agent-reach doctor`. Do not make the user figure out the port flags.
The dedicated Chrome profile must reuse long-term. Do not create a new one
every time, and do not switch to the daily primary Chrome by default.

**Do not trust `boss status` for CDP browser login state.** It only validates
the local session.enc file, which does not stand in for the browser login
state. Use the browser cookie probe (wt2) from `agent-reach doctor`, together
with the user's visual confirmation. Never judge login state from the current
page URL. `security-check` / `zhipin-security` / `_security_check` security
pages are Boss anti-bot challenges and are unrelated to login. They also
appear when the user is already logged in (almost certain on Chrome with a
CDP debugging port). If you see one, do not treat it as logged out. Run
`agent-reach doctor` and check the browser cookie first, then decide whether
the user needs to log in. `AUTH_EXPIRED` from a search is the ground truth
that the browser is logged out: go straight to the login flow plus
`login --cdp`. Do not explain it as a security check.

Searches must use
`boss --browser-source existing-browser --cdp-url http://localhost:9222 search ...`.
On `ENVIRONMENT_RISK`, stop immediately. Do not refresh, do not log in again,
and do not retry automatically.

```bash
# Twitter search (twitter-cli preferred; retry chain in social.md)
twitter search "query" -n 10

# Reddit (no zero-config path: OpenCLI or rdt-cli, login required)
opencli reddit search "query" -f yaml   # desktop
rdt search "query" --limit 10            # legacy/server

# Xiaohongshu (desktop prefers OpenCLI)
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram (desktop OpenCLI, reuse the browser login state)
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # search users
opencli instagram user USERNAME -f yaml        # recent posts from one user
```

## Environment check

> This machine's default Python environment is the conda env `dl`. If
> `agent-reach` is not on PATH, prefix commands with
> `conda run -n dl agent-reach ...`.

```bash
# Check available channels and the backend currently active for each platform
conda run -n dl agent-reach doctor --json
```

## Discovering OpenCLI adapters

When the routing table does not cover the platform or command the user needs,
run `opencli list` to see installed adapters, then `opencli <platform> --help`
for the public commands. Finding an adapter only proves the command exists.
It does not prove that login state or the target content is available. Run a
read-only command only when the user's task clearly needs that platform, and
accept it only when the content that comes back is non-empty.

## Workspace rules

**Do not create files in the agent workspace.** Use `/tmp/` for temporary
output and `~/.agent-reach/` for persistent data.

## Detailed references

Read the matching document for the user's request:

- [Search](references/search.md) — Exa AI search
- [Social](references/social.md) — Xiaohongshu, Twitter, Bilibili, V2EX, Reddit, Facebook, Instagram (multi-backend / login-backed command groups)
- [Career](references/career.md) — LinkedIn, Boss Zhipin
- [Dev](references/dev.md) — GitHub CLI
- [Web](references/web.md) — Jina Reader, RSS
- [Video](references/video.md) — YouTube, Bilibili, Xiaoyuzhou
- [Finance](references/finance.md) — Xueqiu stock quotes, search, and trending content

## Configure a channel

If a channel needs setup, fetch the install guide:
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

The user only needs to provide cookies. The agent does the rest of the configuration.
