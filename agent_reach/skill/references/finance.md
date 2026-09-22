# Market data

Xueqiu stock quotes, search, and trending content. Quotes may be delayed and are not investment advice.

## Check status first

```bash
agent-reach doctor --json
```

When `xueqiu.active_backend` is populated, use that backend. A value of `null` only means Doctor did not finish a live content check. Xueqiu needs a logged-in session or a minimal cookie set. Do not treat HTTP 400 as "this stock does not exist".

## OpenCLI (prefer this when desktop Chrome already has a login session)

```bash
# Verify the current login state
opencli xueqiu whoami -f yaml

# Stock search and live quotes
opencli xueqiu search "NVIDIA" -f yaml
opencli xueqiu stock NVDA -f yaml

# Trending posts and trending stocks
opencli xueqiu hot -f yaml
opencli xueqiu hot-stock -f yaml

# List every read-only command
opencli xueqiu --help
```

OpenCLI only reuses a browser session the user already has and explicitly controls. Do not run `opencli xueqiu login` automatically. If there is no existing login session, have the user log in with Chrome first, or explicitly import the minimal cookies Xueqiu needs:

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

That configuration reads and saves only `xq_a_token`. It does not collect cookies for other platforms along the way.

## Acceptance and failure handling

- Success means the response includes a stock name, symbol, price, or a non-empty content list. Exit code 0 with empty fields is not success.
- HTTP 400 is usually a session or cookie problem. It does not mean the ticker is missing.
- If `whoami` succeeds and `stock` or `hot` fails, report it as an adapter parse issue or a platform API issue. Do not misdiagnose it as logged out.
