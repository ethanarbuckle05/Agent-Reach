# Search tools

Exa AI search engine.

## Exa AI search

A high-quality AI search engine, suited to technical docs, official examples, and related web pages.

```bash
mcporter call exa.web_search_exa query="query" numResults=5
mcporter call exa.web_search_exa query="library API code example" numResults=5
```

### When to use it

| Scenario | Parameters |
|-----|------|
| Web search | `web_search_exa` with `query` and `numResults: 5` |
| Technical / code material | `web_search_exa` with `query` such as "framework API example" and `numResults: 5` |

> Exa MCP's `get_code_context_exa` is deprecated and is not registered by default.
> Use `web_search_exa` for code questions too. When you need an exact search of
> repository contents, use the GitHub search in `dev.md`.

### Traits

- Strong on English content and technical documentation
- Query wording can locate official docs and code examples
- High result quality

## Compared with other search tools

| Tool | Source | Best for |
|-----|------|---------|
| Exa | agent-reach | English / technical / code search |
| Zhipu search | my-mcp-tools | Chinese-language search |
| GitHub search | agent-reach (dev.md) | Repository / code search |
