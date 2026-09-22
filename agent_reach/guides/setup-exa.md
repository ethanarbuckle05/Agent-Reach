# Exa Search setup guide

## What it does
Exa is an AI semantic search engine. It connects through MCP, **free, with no API key**. After setup you get:
- Semantic search across the web
- Reddit search (via site:reddit.com)
- Twitter search (via site:x.com)

## Steps the agent can do

After the user explicitly approves, `agent-reach install --env=auto --system` does the following.
The default command without `--system` only runs a read-only check.

### 1. Install mcporter
```bash
npm install -g mcporter
```

### 2. Register the Exa MCP server
```bash
mcporter config add exa https://mcp.exa.ai/mcp --scope home
```

### 3. Verify
```bash
agent-reach doctor | grep "Search"
mcporter call exa.web_search_exa query="test" numResults=1
```

## Steps the user must do by hand

**None.** Exa connects through MCP. It is free, needs no signup, and needs no API key.

If `agent-reach install --system` did not configure Exa because of a network problem, run the two commands above by hand.

## FAQ

**Q: Is there a search quota?**
A: The MCP endpoint is provided by Exa (mcp.exa.ai) and is currently free with no limit. If that changes, agent-reach updates will adapt.

**Q: What is mcporter?**
A: A command-line bridge for the MCP protocol, used to call MCP servers. Agent Reach uses it to connect to Exa and Xiaohongshu.
