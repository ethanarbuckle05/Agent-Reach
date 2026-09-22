# Reddit setup guide

## What it does

Reddit blocks almost all direct non-browser access (including datacenter and ISP proxy IPs). The JSON API returns 403.

Agent Reach searches and reads Reddit through **rdt-cli**:
- **Search**: `rdt search "query"`
- **Read a full post plus comments**: `rdt read POST_ID`

Free. No proxy and no API key. Login is required (`rdt login`, which extracts cookies from the browser automatically).

## Steps the agent can do

1. Check whether rdt-cli is available:
```bash
which rdt && echo "installed" || echo "not installed"
```

2. If it is missing, install it (the PyPI release is behind for now; install the latest from GitHub):
```bash
pipx install 'git+https://github.com/public-clis/rdt-cli.git'
```

Or install in one step:
```bash
agent-reach install --env=auto --system --channels=reddit
```

## Examples

Search Reddit:
```bash
rdt search "python best practices" -n 5
```

Read a full post and its comments:
```bash
rdt read POST_ID
```

## Steps the user must do by hand

None. After the user explicitly approves, rdt-cli is installed with
`agent-reach install --env=auto --system --channels=reddit`.

## Fallback: Exa search

If Exa is already configured (through mcporter), you can also search Reddit through Exa:

```bash
mcporter call exa.web_search_exa query="site:reddit.com python best practices" numResults=5
```

rdt-cli is the current recommendation and works without extra setup.
