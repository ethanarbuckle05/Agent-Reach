# Jobs and recruiting

LinkedIn and Boss Zhipin.

## LinkedIn

```bash
# Fetch a person profile
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"

# Search people
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"

# Fetch a company profile
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"

# Search jobs
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

> **Login required**: before the first use, run `uvx mcp-server-linkedin@latest --login` and save a valid login session.

### Fallback

If MCP is unavailable, use Jina Reader:

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```

## Boss Zhipin

When the user says "Set up Boss Zhipin for me", follow this section to install, launch the dedicated Chrome, wait for the user to log in manually, and finish verification. Do not dump implementation details such as port 9222 on the user first, and do not type credentials, complete sign-in, or solve slider challenges for the user.

> **Key distinction: the login gate is separate from the anti-bot security check.** After landing on zhipin.com, the page may stop in one of three places: the logged-in `web/geek/job`, the logged-out `web/user/` (QR sign-in / phone-number sign-in), or the anti-bot **security-check page** (URL contains `security-check` / `zhipin-security` / `_security_check`). The security-check page is unrelated to login: **it also appears when already logged in** (almost certain on Chrome with a CDP debugging port). Never judge login state from the current page URL.

> **Two login-state stores (in existing-browser strict CDP mode, the browser is the source of truth).** There are two credential stores. **Delete neither.** They authenticate different channels:
>
> | Store | Role |
> |---|---|
> | `~/.boss-agent/auth/session.enc` | (1) Hard gate: `_get_browser()` unconditionally calls `get_token()`. If it cannot read a token it raises `AuthRequired`, so a CDP search fails before it connects to the browser. (2) This is **not** the search credential: when CDP reuses real Chrome `contexts[0]`, its cookies are injected only on the "no context" branch and never actually take effect. (3) The httpx channel (low-risk ops: `status` / `detail` / `cities` / `job_card_httpx`) really uses its cookies plus stoken, and `force_refresh()` on code 37 writes back to this store. |
> | Browser cookies inside the dedicated Chrome profile | The credentials that high-risk CDP ops such as search and greet actually send |
>
> **`boss status` / `status --live` only validate session.enc.** Even if they report `logged_in: true`, that does not mean the CDP browser is logged in. Therefore:
> 1. After launching the dedicated Chrome, the first step must **pause and have the user visually confirm** the window is logged in (avatar in the top-right). Search only after that confirmation.
> 2. The boss row in doctor probes the browser directly for a wt2 cookie. Treat that as the source of truth.
> 3. **`AUTH_EXPIRED` is ground truth.** If a search reports it, go straight to the login runbook (the user logs in in the dedicated window, then `login --cdp`). Do not explain it as a security check. Treat a `_security_check` page as a slider challenge only when `AUTH_EXPIRED` is absent.
> 4. Do not delete session.enc to clear old credentials. To refresh it, run `login --cdp`.

> **Dependency status**: the public strict-CDP API comes from the follow-up split PRs #403–#407 of boss-agent-cli (#402 and #382 were split per maintainer feedback). All of them are merged into upstream master. The Agent Reach installer pins the fixed upstream commit `4c991b77086a203173bf08a4cb64a23af6514fe6`, not a moving branch. After upstream publishes a release, switch the installer back to a version constraint.

Health check (no side effects, does not search):

```bash
agent-reach doctor          # boss row: off = not installed or CDP unreachable; warn = the path is ready.
                            # message notes whether the browser has a wt2 login cookie (browser is source of truth)
```

Search and job descriptions use the public API (`browser_source` / `job_card_browser` / `JobItem.lid`).
pipx and uv tool installs are isolated environments, so a plain `python` may be unable to import the installed tool.
Use `uv run --with` so the script and the pinned dependency share one interpreter:

```bash
uv run --isolated --no-project \
  --with 'git+https://github.com/can4hou6joeng4/boss-agent-cli.git@4c991b77086a203173bf08a4cb64a23af6514fe6' \
  python - <<'PY'
from pathlib import Path

from boss_agent_cli.api.client import AccountRiskError, BossClient, EnvironmentRiskError
from boss_agent_cli.auth.manager import AuthManager
from boss_agent_cli.platforms.zhipin import BossPlatform

auth = AuthManager(Path.home() / ".boss-agent")

# Strict CDP mode: reuse a logged-in browser, raise immediately if CDP fails, never headless
with BossClient(
    auth,
    cdp_url="http://localhost:9222",
    browser_source="existing-browser",
) as boss:
    raw = boss.search_jobs("LLM", city="Shenzhen", page=1)
    if raw.get("code") != 0:
        code, message = BossPlatform(boss).parse_error(raw)
        raise RuntimeError(f"{code}: {message}")
    items = raw.get("zpData", {}).get("jobList", [])
    for item in items:
        card = boss.job_card_browser(item["securityId"], item["lid"])
        post_desc = card.get("zpData", {}).get("jobCard", {}).get(
            "postDescription", ""
        )
        print(item.get("jobName"), post_desc)

# AccountRiskError / EnvironmentRiskError → stop immediately, do not retry automatically.
# A code 37 that clearly means an expired token or stoken is refreshed and retried at most once by BossClient.
PY
```

### Environment health check and recovery (required before scraping)

If `agent-reach doctor` reports boss as `off` or `warn` before a search, follow this runbook. Do not read the source and guess.

1. **Is the CDP port open**:
   ```bash
   curl -s http://localhost:9222/json/version   # a Browser field means the port is open
   ```

2. **Debug Chrome is not running, or it was closed**: launch the dedicated Chrome for the OS (its login state is separate and does not touch the daily browser):
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

   Bind the loopback address only. Any process that can reach 9222 has full control of that Chrome. Do not listen on the public internet.
   This dedicated profile should reuse long-term so the login state stays stable. Do not delete or recreate it on every run, and do not switch to the daily primary Chrome by default. Close the dedicated window when you are not using it.

   **First step after launch: pause and have the user visually confirm the window is logged in (avatar in the top-right).**
   Do not replace this step with `boss status`. It only validates the local session.enc and does not represent the browser.

3. **User logs in manually (when the browser is logged out)**: decide from doctor's browser cookie probe (no wt2 means the browser is logged out), then from the user's visual confirmation. `boss status` is only a hint.
   Have the user log in or complete sign-in in this dedicated window. After the user confirms, save the CDP login state:
   ```bash
   boss --cdp-url http://localhost:9222 login --cdp
   ```

   If the window is stuck on a security-check page (`security-check` / `zhipin-security`), that is an anti-bot challenge, not a login page. Wait for it to pass on its own, or have the user complete the slider once. Do not treat it as logged out and start sign-in over again.

4. **Whether the login state is valid** (browser cookie probe, and whether stoken has expired):
   ```bash
   agent-reach doctor     # read the browser wt2 cookie probe in the boss row message
   boss status            # reflects only the local session.enc; a hint, nothing more
   ```

5. **Error-code handling** (during search or JD fetch):
   - `AUTH_EXPIRED` (user not logged in) → **ground truth**: the CDP browser is logged out, whatever `boss status` says. Go straight to the step 3 login flow plus `login --cdp`. Do not explain it as a security check.
   - code 36 (`ACCOUNT_RISK`) → stop immediately, handle it manually on the Boss Zhipin page, and do not retry automatically;
   - code 9 (`RATE_LIMITED`) → retry after a cooldown;
   - code 37 plus an environment-anomaly message → `ENVIRONMENT_RISK`: stop immediately. Do not refresh the token, do not log in again, and do not retry automatically;
   - Only a code 37 whose wording explicitly says the token or stoken has expired is `TOKEN_REFRESH_FAILED`. The client refreshes and retries at most once. If it still fails, log in again.

When the user asks to start searching, the agent must select strict CDP mode (global options go before the subcommand):

```bash
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "LLM" --city Guangzhou --page 1
```

Do not page through results continuously without saying so. boss-agent-cli PR #383 adds a persistent 5–10 second list budget for ordinary searches that span CLI processes. Until that PR is merged and released, the agent should still call serially and at a lower rate.

> **Waiting is expected. It is not a hang.** When consecutive searches hit throttling, boss-agent-cli waits silently for 5–10 seconds (on a TTY it shows a throttle-wait hint for N seconds; Agent Reach calls with `--json` and will not see that hint). During the wait window, do not retry, do not launch a new browser, and do not switch profiles.
