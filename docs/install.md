# Agent Reach — Installation Guide

## For Humans

Copy this to your AI Agent:

```
Install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

> 🛡️ **Safe by default:** `agent-reach install` only checks the machine and lists missing dependencies:
> ```
> Safely check and install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> ```
> Only use `--system` after the user explicitly approves system-level installs and configuration writes.

---

## For AI Agents

### Goal

Install Agent Reach and all upstream tools so your user's agent has full internet access. After installation, you'll use the upstream tools directly (OpenCLI, twitter-cli, bili-cli, rdt-cli, yt-dlp, mcporter, gh CLI, etc.) — Agent Reach is the selector, installer, health checker and router, never a wrapper.

### ⚠️ Boundaries

When fixing issues, stay within these limits:

- **DO NOT** run commands with `sudo` unless the user explicitly approved
- **DO NOT** modify system files outside `~/.agent-reach/`
- **DO NOT** install packages not listed in this guide
- **DO NOT** disable firewalls, security settings, or system protections
- **DO NOT** clone repos, create files, or run commands inside the agent workspace / working directory
- If something requires elevated permissions, **tell the user** what's needed and let them decide

### 📁 Directory Rules

All Agent Reach files go in dedicated directories — **never in the agent workspace**:

| Purpose | Directory | Example |
|---------|-----------|---------|
| Config & tokens | `~/.agent-reach/` | `~/.agent-reach/config.json` |
| Upstream tool repos | `~/.agent-reach/tools/` | `~/.agent-reach/tools/xiaoyuzhou/` |
| Temporary files | `/tmp/` | `/tmp/yt-dlp-output/` |
| Skills | `~/.openclaw/skills/agent-reach/` | SKILL.md |

**Why?** If you clone repos or create files in the workspace, it pollutes the user's project directory and can break their agent over time. Keep the workspace clean.

### Step 1: Install the basics

```bash
# Recommended: pipx (least hassle)
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto               # Read-only check (default)
# After the user explicitly approves system changes:
agent-reach install --env=auto --system

# If your Python comes from Homebrew, or you hit PEP 668 (externally-managed-environment),
# install into a virtual environment:
python3 -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/bin/activate
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto               # Read-only check (default)
# After the user explicitly approves system changes:
agent-reach install --env=auto --system
```

> 💡 **Windows / Microsoft Store Python alias?**
> If `python3 --version` opens the Microsoft Store, or `where python3` points to
> `...\AppData\Local\Microsoft\WindowsApps\python3.exe`, then `python3` is the Windows
> Store alias, not a usable Python install. Use the Python Launcher `py -3`, or `python.exe` from the actual install directory.
>
> PowerShell example:
> ```powershell
> py -3 -m venv $env:USERPROFILE\.agent-reach-venv
> $env:USERPROFILE\.agent-reach-venv\Scripts\Activate.ps1
> python -m pip install https://github.com/Panniantong/agent-reach/archive/main.zip
> agent-reach install --env=auto
> ```

The default command checks core infrastructure (gh CLI, Node.js, mcporter, Exa search, yt-dlp config) without changing the host. With explicit `--system` approval it installs/configures the missing pieces and activates these zero-config channels:

- Web (Jina Reader), YouTube, GitHub, RSS, Exa Search, V2EX, Bilibili (basic)

> 💡 **macOS / Homebrew Python reports `externally-managed-environment`?**
> That is PEP 668 protection, not a problem with Agent Reach itself. Prefer `pipx install ...`, or create a `venv` first and then install.

**Install modes:**

```bash
agent-reach install --env=auto             # Check only; safe default
agent-reach install --env=auto --safe      # Same check-only behavior (compatibility)
agent-reach install --env=auto --system    # Explicitly allow external/system installs
agent-reach install --env=auto --dry-run   # Preview what --system would do
```

### Step 2: Ask the user which optional channels they want

After installing the basics, **ask the user** which additional channels they need. Present this list:

> The basic channels are installed. You can now have me search the web, watch YouTube, read GitHub, and more.
>
> These optional channels are also available. Which ones do you need?
>
> - 🌟 **OpenCLI** (recommended on desktop) — one install covers Reddit/Facebook/Instagram/Bilibili subtitles/a Twitter fallback, and it is the Xiaohongshu desktop backend. Xiaohongshu uses only a Chrome session the user already has and explicitly controls
> - 🐦 **Twitter/X** — search tweets and read the timeline (login cookie required)
> - 📈 **Xueqiu** — stock quotes and hot posts (login cookie required)
> - 🎙️ **Xiaoyuzhou Podcast** — audio to text (free Groq key required)
> - 📕 **Xiaohongshu** — search, reading, and comments (OpenCLI uses an existing session; MCP/legacy tools use Cookie-Editor)
> - 📖 **Reddit** — search and read posts (login required: desktop OpenCLI, or rdt-cli + cookie)
> - 📘 **Facebook** — search, profiles, Feed, and group lists (desktop via OpenCLI, reusing the Chrome login session)
> - 📷 **Instagram** — user search, profiles, a user's recent posts, and Explore (desktop via OpenCLI, reusing the Chrome login session)
> - 📺 **Bilibili (full)** — hot, rankings, search, and video details (bili-cli, no login)
> - 💼 **LinkedIn** — profiles and job search
> - 🎯 **Boss Zhipin** — job search + full JD text (local dedicated Chrome; the user logs in manually)
>
> Tell me which ones you want, for example "install Xiaohongshu and Twitter for me" or "install Facebook and Instagram for me". Or say "install everything".

Based on the user's choice, run:

```bash
agent-reach install --env=auto --system --channels=opencli,xiaohongshu   # Desktop user chose XHS
agent-reach install --env=auto --system --channels=facebook,instagram    # Desktop Meta channels
agent-reach install --env=local --system --channels=boss                # Desktop Boss Zhipin
agent-reach install --env=auto --system --channels=all                   # User approved everything
```

Supported channel names: `opencli`, `twitter`, `xiaoyuzhou`, `xueqiu`, `xiaohongshu`, `reddit`, `facebook`, `instagram`, `bilibili`, `linkedin`, `boss`, `all`

### Step 3: Fix what's broken

Run `agent-reach doctor` and check the output.

Try to get as many channels to ✅ as possible. If something failed during install or shows as ❌/⚠️ in doctor, diagnose the problem and try to fix it — but stay within the boundaries above. If a fix requires elevated permissions or system changes, ask the user first.

Only ask the user when you genuinely need their input (credentials, permissions, etc.).

### Step 3: Configure things that need user input

Some channels need credentials only the user can provide. Based on the doctor output, ask for what's missing:

> 🔒 **Security tip:** For platforms that need cookies or browser sessions (Twitter, XiaoHongShu, Reddit, Facebook, Instagram, Boss Zhipin), we recommend using a **dedicated/secondary account** rather than your main account. Cookie/browser-session auth carries two risks:
> 1. **Account ban** — platforms may detect non-browser API calls and restrict or ban the account
> 2. **Credential exposure** — cookies grant full account access; using a secondary account limits the blast radius if credentials are ever compromised

> 🍪 **Cookies / login session:**
>
> For traditional CLIs that need cookies (Twitter, Xueqiu, and similar), **prefer importing with Cookie-Editor**. It is the simplest and most reliable method:
> 1. The user logs in to the platform in their own browser
> 2. Install the [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension
> 3. Click the extension → Export → Header String
> 4. Send the exported string to the Agent
>
> Twitter accepts only what the user explicitly exported with Cookie-Editor. Agent Reach does not log the user in to Xiaohongshu, and it does not read Xiaohongshu browser cookies. Xiaohongshu OpenCLI uses only a Chrome session the user already has and explicitly controls. If there is no existing session, export with Cookie-Editor and configure xiaohongshu-mcp / legacy tools instead. Xueqiu and Bilibili can be imported explicitly per platform, for example `agent-reach configure --from-browser chrome --platform xueqiu`. The command does not scan or save other platforms.

**Twitter search & posting:**
> "To unlock Twitter search, I need your Twitter cookies. Install the Cookie-Editor Chrome extension, go to x.com/twitter.com, click the extension → Export → Header String, and paste it to me."

```bash
agent-reach configure twitter-cookies
```

This saves `twitter_auth_token` and `twitter_ct0` for Agent Reach's own
`doctor` configuration check. `doctor` does not run the upstream `twitter status`
live, and it does not change the current shell. Before running `twitter search/read/...`
directly, set these explicitly in that process environment:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
twitter search "query" -n 10
```

> **Proxy notes (networks that need a proxy, such as mainland China):**
>
> twitter-cli and rdt-cli use Python. On a network that needs a proxy, configure it with environment variables.
>
> **What you (the Agent) need to do:**
> 1. Confirm the user configured a proxy: `agent-reach configure proxy` (hidden input)
> 2. Set the environment variables: `export HTTP_PROXY="..." HTTPS_PROXY="..."`
> 3. Agent Reach handles the rest. The user does not need to do anything else
>
> If the user reports "fetch failed", see [troubleshooting.md](troubleshooting.md)

**Reddit (login is mandatory — no zero-config path):**
> Reddit's anonymous endpoints are blocked, and the official API requires manual approval. Desktop users should prefer OpenCLI (it works once reddit.com has been logged in to in the browser). Server and existing users use rdt-cli:

```bash
# PyPI lags upstream; install from GitHub (same pin as _RDT_GIT_SOURCE in the code)
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'
rdt login   # Extracts browser cookies automatically; on a server with no browser, write the cookie manually as doctor instructs
```

> Reaching Reddit from mainland China requires a proxy. If a server IP is blocked, configure a residential proxy (for example https://webshare.io, about $1/month):
> ```bash
> agent-reach configure proxy
> ```

**Xiaohongshu (multiple backends; choose by environment):**

> **Auth boundary:** Agent Reach does not log the user in to Xiaohongshu, and it does not read browser
> cookies. OpenCLI uses only a Chrome session that already exists and that the user explicitly controls.
> `agent-reach configure xhs-cookies` does not inject cookies into OpenCLI or Chrome.
> If there is no existing session, do not log in automatically. Use a manual Cookie-Editor export to configure
> xiaohongshu-mcp or a legacy tool:
>
> ```bash
> agent-reach configure xhs-cookies
> ```
>
> This explicit command saves or imports the user-provided cookie set for the xiaohongshu.com domain. Confirm
> the cookie names and scope first. Cookies outside the xiaohongshu.com domain are ignored.
>
> **Desktop (OpenCLI recommended):**

```bash
agent-reach install --system --channels opencli
```

> After install, guide the user through the one manual step (a Chrome security restriction; you cannot do it for them):
> 1. Open https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk
> 2. Click "Add to Chrome"
> 3. Run `opencli doctor` to verify (success means it shows Extension: connected)
>
> If the result is AUTH_REQUIRED and the user has no existing session, do not log in for them. Use the
> xiaohongshu-mcp / legacy-tool Cookie-Editor path below.
>
> **Server / headless (xiaohongshu-mcp):**
> 1. Download the binary for the platform from https://github.com/xpzouying/xiaohongshu-mcp/releases into `~/.agent-reach/tools/`
> 2. Start the service (the first run downloads about 150MB of headless browser; wait until it finishes)
> 3. Import cookies manually with the Cookie-Editor flow above
> 4. Connect: `mcporter config add xiaohongshu http://localhost:18060/mcp --scope home`
> 5. Always pass `--timeout 120000` when calling it
>
> **Existing users (xhs-cli):** an xhs-cli that is already installed keeps working as a fallback backend
> (upstream stopped updating in March 2026; not recommended for new installs). Auth still uses the Cookie-Editor
> manual export flow above.

**Facebook / Instagram (desktop OpenCLI):**
> These two platforms go through OpenCLI: they reuse the user's own Chrome login session, do not store the account password, and do not go through Meta Graph API review. Server / headless environments are not a recommended setup.

```bash
agent-reach install --system --channels facebook,instagram
```

> After install:
> 1. Confirm Chrome has the OpenCLI extension installed and that `opencli doctor` passes
> 2. Log in to facebook.com / instagram.com in Chrome
> 3. The Agent calls them directly:
>    ```bash
>    opencli facebook search "query" -f yaml
>    opencli facebook profile zuck -f yaml
>    opencli facebook groups -f yaml
>    opencli instagram search "query" -f yaml     # user search
>    opencli instagram profile nasa -f yaml
>    opencli instagram user nasa -f yaml          # recent posts by that user
>    ```
>
> Facebook Groups currently only promises the group list and recent activity visible after the user logs in. It does not promise an API for arbitrary group posts and comments. Instagram search is user search, not a site-wide keyword search over posts. If you see a 429 or a login error, have the user log in again in Chrome and lower the request rate.

**Xueqiu (stock quotes + hot posts):**
> "Xueqiu needs a cookie from a logged-in session. Log in to xueqiu.com in Chrome first, then run:"

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

> This reads and saves only the minimum cookies Xueqiu needs. It does not also read other platforms.

**Xiaoyuzhou Podcast (Groq Whisper):**
> "Xiaoyuzhou podcast transcription is installed by default. You only need a free Groq API key."

The script is installed automatically with Agent Reach. The user only needs to provide a key:

```bash
agent-reach configure groq-key
```

> **Get a Groq API key (free, no credit card, about 30 seconds):**
> 1. Open https://console.groq.com
> 2. Sign in with a Google or GitHub account (or sign up)
> 3. Left menu → API Keys → Create API Key
> 4. Copy the key (it starts with `gsk_`) and send it to the Agent
>
> **How to use it:**
> The user sends a Xiaoyuzhou link to the Agent, and the Agent runs:
> ```bash
> bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh https://www.xiaoyuzhoufm.com/episode/xxxxx
> ```
>
> It downloads the audio, transcodes and splits it, transcribes it with Groq Whisper, and prints a full Chinese transcript.
>
> **Free quota and limits:**
> - About 2 hours of audio per hour (7200 seconds). After you exceed that, wait 15 minutes and it recovers on its own
> - Enough for listening to a few episodes a day
> - Transcription quality is high (Whisper large-v3), but it does not separate speakers
> - For podcasts longer than 2 hours, process them in batches

**LinkedIn (optional — mcp-server-linkedin):**
> "Basic LinkedIn content can be read with Jina Reader. Full features (profile details, people search, and job search) need mcp-server-linkedin."

> **Setup (stdio recommended):**
> Install `uv` first by following the official instructions (this also provides `uvx`):
> https://docs.astral.sh/uv/getting-started/installation/
>
> ```bash
> mcporter config add linkedin --command uvx --arg mcp-server-linkedin@latest --env UV_HTTP_TIMEOUT=300 --scope home
> ```
>
> `uvx` fetches and starts the latest service on demand. You do not need a separate Python package or a long-running HTTP service.
>
> **First login (needs a browser UI):**
> ```bash
> uvx mcp-server-linkedin@latest --login
> ```
> After the browser opens, log in to LinkedIn manually. The session is saved to `~/.linkedin-mcp/profile/`. A headless server must run the same login command on a visible desktop such as VNC.
>
> See https://github.com/stickerdaniel/linkedin-mcp-server

**Boss Zhipin (desktop only — boss-agent-cli + CDP):**

When the user says "Set up Boss Zhipin for me", the Agent finishes whatever it can automate and leaves the site login to the user:

1. First explain that you will install an upstream CLI, start a separate Chrome profile directory, and ask for permission to install on the system.
2. After the user agrees, run:
   ```bash
   agent-reach install --env=local --system --channels=boss
   ```
3. Start a dedicated Chrome bound only to the local loopback address, for the current operating system:
   ```bash
   # macOS
   open -na "Google Chrome" --args --remote-debugging-address=127.0.0.1 \
     --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
     "https://www.zhipin.com/web/geek/job"

   # Linux
   google-chrome --remote-debugging-address=127.0.0.1 \
     --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
     "https://www.zhipin.com/web/geek/job"
   ```
   Windows PowerShell:
   ```powershell
   Start-Process chrome.exe -ArgumentList '--remote-debugging-address=127.0.0.1','--remote-debugging-port=9222',"--user-data-dir=$env:USERPROFILE\.boss-chrome-profile",'https://www.zhipin.com/web/geek/job'
   ```
4. Pause and have the **user visually confirm** the login state in the window (an avatar in the top right). If they are not logged in, **the user logs in manually**, scans a QR code, or handles the slider. The Agent does not ask for the account password, does not log in on their behalf, and must not use `boss status`
   in place of this step — it only checks the local `session.enc`, which does not mean this Chrome is logged in.
5. After the user confirms login is complete, run:
   ```bash
   boss --cdp-url http://localhost:9222 login --cdp
   agent-reach doctor    # Check the browser wt2 cookie probe in the boss row message
   ```

> Security boundary: any local process that can reach debug port 9222 has full control of this Chrome.
> You must use `--remote-debugging-address=127.0.0.1`. Do not expose it to the LAN or the public internet. Use
> a separate profile and keep reusing it. Do not delete or recreate it each time, and do not switch to the everyday main Chrome by default.
> Close the dedicated Chrome when it is not in use. Boss does not support server or headless environments. Search commands must include
> `--browser-source existing-browser --cdp-url http://localhost:9222`.
>
> Dependency: the follow-up split PRs #403–#407 for boss-agent-cli are merged into upstream master. The installer pins the upstream
> commit
> `4c991b77086a203173bf08a4cb64a23af6514fe6` and does not follow a branch that moves. That commit includes
> `browser_source="existing-browser"` (strict CDP), `JobItem.lid`, and `job_card_browser()`. After upstream publishes a release,
> Agent Reach should switch to a version constraint.

### Step 4: Final check

Run `agent-reach doctor` one final time and report the results to your user.

### Step 5: Set up daily monitoring (OpenClaw only)

If you are running inside **OpenClaw**, ask your user:

> "Agent Reach is installed. Want me to set up a daily check? It watches whether these channels are healthy and whether a new version is available. It notifies you only when something is wrong."

If the user agrees, create a **cron job** (daily, `sessionTarget: "isolated"`, `delivery: "announce"`) with this task:

```
Run the agent-reach watch command.
If the output contains "all healthy", do not notify the user; finish silently.
If the output contains problems (❌ ⚠️) or a new version (🆕), send the full report to the user and suggest a fix.
If a new version is available, ask the user whether to upgrade (sending this to the user's Agent performs a full update: Update Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md).
```

If the user wants a different agent to handle it, let them choose.

---

## Quick Reference

| Command | What it does |
|---------|-------------|
| `agent-reach install --env=auto` | Read-only dependency and channel check (default) |
| `agent-reach install --env=auto --system` | Explicitly install/configure core external tools |
| `agent-reach install --env=auto --system --channels=twitter,xiaohongshu` | Install approved optional channels |
| `agent-reach install --env=local --system --channels=boss` | Install the desktop Boss Zhipin strict-CDP backend |
| `agent-reach install --env=auto --system --channels=all` | Install everything after explicit approval |
| `agent-reach install --env=auto --safe` | Compatibility alias for the safe default |
| `agent-reach install --env=auto --dry-run` | Preview what would be done |
| `agent-reach doctor` | Show channel status |
| `agent-reach watch` | Quick health + update check (for scheduled tasks) |
| `agent-reach check-update` | Check for new versions |
| `agent-reach configure twitter-cookies` | Save Twitter cookies via hidden input; direct calls still need explicit environment variables |
| `agent-reach configure proxy` | Save a proxy address via hidden input; this is not an automatic unlock switch |
| `agent-reach configure groq-key` | Configure the Xiaoyuzhou transcription key via hidden input |

After installation, use upstream tools directly. See SKILL.md for the full command reference:

| Platform | Upstream Tool | Example |
|----------|--------------|---------|
| Twitter/X | `twitter` (fallback `opencli`) | After setting `TWITTER_AUTH_TOKEN` / `TWITTER_CT0`, run `twitter search "query" -n 10` |
| YouTube | `yt-dlp` | `yt-dlp --dump-json URL` |
| Bilibili | `bili` (subtitles via `opencli`) | `bili search "query" --type video` / `opencli bilibili subtitle BVxxx` |
| Reddit | `opencli` (fallback `rdt`) | `opencli reddit search "query" -f yaml` / `rdt read POST_ID` |
| Facebook | `opencli` | `opencli facebook search "query" -f yaml` |
| Instagram | `opencli` | `opencli instagram user nasa -f yaml` |
| GitHub | `gh` | `gh search repos "query"` |
| Web | `curl` + Jina | `curl -s "https://r.jina.ai/URL"` |
| Exa Search | `mcporter` | `mcporter call exa.web_search_exa query="..." numResults=5` |
| Xiaohongshu | `opencli` (server: `mcporter`) | `opencli xiaohongshu search "query" -f yaml` |
| Xiaoyuzhou Podcast | `transcribe.sh` | `bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh <URL>` |
| LinkedIn | `mcporter` | `mcporter call linkedin.get_person_profile linkedin_username="..."` |
| Boss Zhipin | `boss` / Python public API | `agent-reach doctor` (browser wt2 probe; `boss status` only reflects the local session.enc); for search and JD see `references/career.md` |
| RSS | `feedparser` | `python3 -c "import feedparser; ..."` |

> For multi-backend platforms, use `active_backend` from `agent-reach doctor --json`.
