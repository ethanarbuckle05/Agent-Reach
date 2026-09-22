# Xiaohongshu setup guide

## What it does
Read and search Xiaohongshu notes. Desktop prefers OpenCLI. Servers use
[xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp).
xhs-cli is only a legacy fallback for users who already have it installed.

## Prerequisites
- OpenCLI: a Xiaohongshu Chrome session the user already has and explicitly controls
- xiaohongshu-mcp / legacy tools: the Cookie-Editor browser extension

## Auth boundary

Agent Reach does not perform Xiaohongshu login for the user, and it does not read browser cookies.

OpenCLI uses only a Chrome session the user already has and explicitly controls.
`agent-reach configure xhs-cookies` does not inject cookies into OpenCLI or Chrome.
If there is no existing session, do not log in automatically. Use a manual
Cookie-Editor export, then configure xiaohongshu-mcp or a legacy tool:

1. Install the [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension in Chrome
2. The user prepares the session to export on xiaohongshu.com themselves
3. Click the Cookie-Editor icon → Export → Header String
4. Send the exported string to the agent and run:

```bash
agent-reach configure xhs-cookies
agent-reach doctor
```

That explicit command saves and imports the user-provided same-site cookie set
for xiaohongshu.com. Confirm the cookie names and scope before you run it.
Cookies outside the xiaohongshu.com domain are ignored.

If the xiaohongshu-mcp container is already running, the configure command
imports the cookies into the container. Otherwise it writes an owner-only
local file and prints the later manual import path.

## Examples

Pick the command from `active_backend` in `agent-reach doctor --json`. Legacy xhs-cli examples:

Search notes:
```bash
xhs search "keyword"
```

Read a note:
```bash
xhs read NOTE_ID
```

Read comments:
```bash
xhs comments NOTE_ID
```

## FAQ

**Q: The cookie expired?**
A: Export again manually with Cookie-Editor, run
`agent-reach configure xhs-cookies`, and paste into the hidden prompt.

**Q: Xiaohongshu warns about IP risk?**
A: Use a residential proxy: `export HTTP_PROXY="http://user:pass@ip:port"`.

**Q: xhs-cli does not support my system?**
A: Make sure Python 3.10+ and pipx are installed. Then run `pipx install xiaohongshu-cli`.

## Server option: Docker MCP

If you already use the [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) Docker setup, it still works:

```bash
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  xpzouying/xiaohongshu-mcp

mcporter config add xiaohongshu http://localhost:18060/mcp --scope home
```

That server backend uses the manual Cookie-Editor export flow above.
