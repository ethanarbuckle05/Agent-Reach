# Twitter advanced features setup guide (twitter-cli)

Basic Twitter reading is free through Jina Reader and needs no setup.

Advanced features need twitter-cli (@public-clis/twitter-cli):

- Search tweets (`twitter search`)
- Read a full tweet and its conversation (`twitter tweet`, `twitter thread`)
- User timeline (`twitter timeline`)
- Long-form reading (`twitter article`)

twitter-cli is a free open-source tool (install with pipx), but it needs your Twitter account cookies.

## Quick setup

1. Check whether twitter-cli is installed:

```bash
which twitter && echo "installed" || echo "not installed"
```

2. Install twitter-cli:

```bash
pipx install twitter-cli
```

3. Confirm the command is installed (no auth request at this step):

```bash
twitter --help
```

## Get cookies (Cookie-Editor, recommended)

1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension
2. Log in to x.com
3. Click the Cookie-Editor icon → Export → Header String
4. Run the configure command:

```bash
agent-reach configure twitter-cookies
```

This extracts `auth_token` and `ct0` and stores them safely in
`~/.agent-reach/config.yaml` so `agent-reach doctor` can check that explicit
credentials are present. `doctor` does not run `twitter status`, does not
live-check whether the account works, and does not modify the current shell.

By default it writes only `~/.agent-reach/config.yaml`. It writes the extra
copies below only when the user explicitly agrees to copy credentials and
passes `--sync-legacy-twitter`:

- `~/.config/xfetch/session.json`
- `~/.config/bird/credentials.env`

```bash
agent-reach configure twitter-cookies --sync-legacy-twitter
```

`agent-reach uninstall` only reminds you about these legacy copies. It does
not delete them automatically. To clean them up, confirm with the user first,
then delete those two files by hand.

`twitter` is an independent upstream command and does not read Agent Reach's
config file. When you run `twitter status/search/read/...` directly, you must
explicitly set `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` in the current shell or
in the child-process environment, as the next section describes. Do not rely
on automatic browser-cookie reads.

## Set cookies manually

If you already know `auth_token` and `ct0`:

1. Install twitter-cli if it is missing: `pipx install twitter-cli`

2. Set the environment variables:

```bash
export TWITTER_AUTH_TOKEN="your_auth_token"
export TWITTER_CT0="your_ct0"
```

3. Test:

```bash
twitter search "test" -n 1
```

## Proxy setup

> twitter-cli can use a proxy through environment variables:

```bash
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "test" -n 1
```

You can also use a global proxy tool:

```bash
proxychains twitter search "test" -n 1
```

## Fallback: bird CLI

If you already have [bird CLI](https://www.npmjs.com/package/@steipete/bird) installed (`npm install -g @steipete/bird`), it still works. Agent Reach detects an installed bird and uses it. The two tools are similar. twitter-cli is the current recommendation.
