# -*- coding: utf-8 -*-
"""YouTube — check if yt-dlp is available with JS runtime."""

import re
import shutil

from agent_reach.probe import probe_command
from agent_reach.utils.paths import (
    PrivatePathError,
    get_ytdlp_config_path,
    read_small_text_no_follow,
    render_ytdlp_fix_command,
)

from .base import Channel

_JS_RUNTIMES_SUPPORTED_FROM = (2025, 11, 12)
_YTDLP_UPGRADE_COMMAND = 'python -m pip install -U "yt-dlp[default]"'


def _parse_ytdlp_version(version: str):
    """Return a comparable stable yt-dlp release tuple, if recognised."""
    match = re.fullmatch(r"\s*(\d{4})\.(\d{1,2})\.(\d{1,2})\s*", version)
    return tuple(map(int, match.groups())) if match else None


def _has_js_runtime_config(config_path) -> bool:
    """Return whether yt-dlp config explicitly enables a JS runtime."""
    try:
        payload = read_small_text_no_follow(
            config_path,
            max_bytes=1024 * 1024,
        )
        return payload is not None and "--js-runtimes" in payload
    except (OSError, UnicodeError, PrivatePathError):
        return False


class YouTubeChannel(Channel):
    name = "youtube"
    description = "YouTube videos and subtitles"
    backends = ["yt-dlp"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "youtube.com", "youtu.be")

    def check(self, config=None):
        # Actually run yt-dlp --version to probe liveness: not installed / broken venv / cannot run
        probe = probe_command("yt-dlp", ["--version"], timeout=10, package="yt-dlp")
        if probe.status == "missing":
            self.active_backend = None
            return "off", f"yt-dlp is not installed. Install: {_YTDLP_UPGRADE_COMMAND}"
        if probe.status == "broken":
            self.active_backend = None
            return "error", (
                "yt-dlp is installed but cannot execute. Reinstall (with JS support):\n"
                f"  {_YTDLP_UPGRADE_COMMAND}\n{probe.hint}"
            )
        if not probe.ok:  # timeout / error: installed but cannot run
            self.active_backend = None
            detail = probe.hint or probe.output or probe.status
            return "error", f"yt-dlp cannot run normally: {detail}"
        # yt-dlp itself is alive; later JS runtime/transcription checks only affect ok/warn, not which backend is active
        self.active_backend = "yt-dlp"
        # Check JS runtime
        has_js = shutil.which("deno") or shutil.which("node")
        if not has_js:
            return "warn", (
                "yt-dlp is installed but is missing a JS runtime (required for YouTube).\n"
                "  Install Node.js or deno, then run: agent-reach install --system"
            )
        # Check yt-dlp config for --js-runtimes
        # Deno works out of the box; Node.js requires explicit config
        has_deno = shutil.which("deno")
        if not has_deno:
            ytdlp_config = get_ytdlp_config_path()
            if not _has_js_runtime_config(ytdlp_config):
                version = _parse_ytdlp_version(probe.output)
                if version is None:
                    return "warn", (
                        "could not confirm whether this yt-dlp version supports JS runtime config. "
                        "Please upgrade first and rerun doctor:\n"
                        f"  {_YTDLP_UPGRADE_COMMAND}"
                    )
                if version < _JS_RUNTIMES_SUPPORTED_FROM:
                    return "warn", (
                        "yt-dlp is too old to support JS runtime config. Please upgrade first and rerun doctor:\n"
                        f"  {_YTDLP_UPGRADE_COMMAND}"
                    )
                return "warn", (
                    f"yt-dlp is installed but no JS runtime is configured. Run:\n  {render_ytdlp_fix_command()}"
                )
        # Surface transcription readiness so `doctor` reports it.
        msg = "can extract video info and subtitles"
        if config is not None:
            providers = []
            if config.is_configured("groq_whisper"):
                providers.append("groq")
            if config.is_configured("openai_whisper"):
                providers.append("openai")
            if providers:
                missing_media_tools = [
                    tool
                    for tool in ("ffmpeg", "ffprobe")
                    if not shutil.which(tool)
                ]
                if missing_media_tools:
                    msg += (
                        " (install "
                        + ", ".join(missing_media_tools)
                        + " for audio transcription)"
                    )
                else:
                    msg += f", can transcribe audio ({'/'.join(providers)})"
        return "ok", msg

    def transcribe(
        self,
        url: str,
        *,
        provider: str = "auto",
        config=None,
        allow_provider_fallback: bool = False,
    ) -> str:
        """Download a YouTube video's audio and return its transcript.

        Delegates to :func:`agent_reach.transcribe.transcribe`. Imported lazily
        so the channel module stays cheap to import for users who never
        transcribe.
        """
        from agent_reach.transcribe import transcribe as _transcribe

        return _transcribe(
            url,
            provider=provider,
            config=config,
            allow_provider_fallback=allow_provider_fallback,
        )
