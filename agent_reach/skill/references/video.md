# Video and podcasts

Subtitles and transcripts for YouTube, Bilibili, and Xiaoyuzhou podcasts.

## YouTube (yt-dlp)

### Video metadata

```bash
yt-dlp --dump-json "URL"
```

### Download subtitles

```bash
# Download subtitles (do not download the video)
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# Then read the .vtt file
cat /tmp/VIDEO_ID.*.vtt
```

### Fetch comments

```bash
# Extract comments (best-effort, completeness is not guaranteed)
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# Comments are in the comments field of .info.json
```

### Search videos

```bash
yt-dlp --dump-json "ytsearch5:query"
```

> **Subtitles**: manually uploaded subtitles extract reliably. Auto-generated subtitles can repeat lines and need cleanup.
> **Comments**: `--write-comments` scrapes the web page (it is not the YouTube Data API), so some comments may be missing.

### Retry chain when subtitles fail (run in order; stop when you have real content)

`doctor` only checks that the yt-dlp binary and the JS runtime can run. It does not request a specific video, so `active_backend: yt-dlp` does not mean that video's subtitles have passed a live check.

1. Start with the `yt-dlp --write-sub --write-auto-sub` command above.
2. If you hit a bot check, an empty subtitle response, or no subtitle file, and OpenCLI is connected: `opencli youtube transcript "URL" -f yaml`.
3. If OpenCLI returns `Caption URL returned empty response`, retry at most 3 times. That caption URL expires and sometimes fails. An empty response does not mean the video has no subtitles.
4. If it still fails, or the video never had subtitles: `agent-reach transcribe "URL"` downloads the audio and transcribes it.

Success means you actually received non-empty subtitle or transcript text. A command exit code or `doctor`'s version probe is not success.

### No-subtitle fallback: Whisper audio transcription

```bash
# Fallback when the video has no subtitles: download audio and transcribe with Whisper (a free Groq key is enough)
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> `agent-reach transcribe` accepts only a public http(s) URL or a local audio file. When you search with `ytsearch5:`, pick a concrete video URL from the yt-dlp results, then transcribe that.
> Configure a key first: `agent-reach configure groq-key` (hidden prompt; free, console.groq.com) or `agent-reach configure openai-key`. Default auto mode uses only the first configured provider (Groq first, otherwise OpenAI) and stops on failure. It will not send the audio to the other provider automatically.
> `--allow-provider-fallback` explicitly allows falling back across providers. The same audio may be processed by both Groq and OpenAI, and OpenAI may charge for it. Use it only after confirming the content may be shared with both.

## Bilibili (bili-cli first, OpenCLI for subtitles)

> ⚠️ **Do not use yt-dlp to read Bilibili.** Bilibili risk controls now return 412 for yt-dlp across the board (verified on the latest version, direct connection, proxy, and with cookies; all fail). yt-dlp is for YouTube only.

### Video details / search / trending / rankings (bili-cli, read-only, no login)

```bash
# Video details (title / uploader / duration / view and engagement stats / subtitle availability)
bili video BVxxx

# Search videos
bili search "query" --type video -n 5

# Trending videos / rankings
bili hot -n 10
bili rank -n 10

# Download audio and split it into ASR-ready WAV (pair with agent-reach transcribe when there are no subtitles)
bili audio BVxxx
```

### Subtitles (OpenCLI, needs desktop Chrome)

```bash
# Subtitles, line by line, with timestamps
opencli bilibili subtitle BVxxx

# OpenCLI can also search and read video metadata (fallback)
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### Zero-config fallback: call the search API directly

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

> **Install bili-cli**: `pipx install bilibili-cli` (upstream stopped updating in 2026-03, but it still works in practice; read-only use needs no login. `bili login` with a sign-in scan unlocks personal features such as the feed and favorites).

## Xiaoyuzhou podcasts

### Transcribe one episode (optional --polish for punctuation)

```bash
# Write a Markdown file to /tmp/. --polish asks Llama 3.3 70B to add Chinese punctuation and sensible paragraph breaks
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> The transcription prompt already asks Whisper to output Chinese punctuation. If punctuation is still weak, add `--polish` and use the free Llama 3.3 70B on Groq to restore punctuation and sensible paragraph breaks (about 7 extra seconds for a 9-minute podcast). Each transcription adds one more LLM call. Use it when you need it.

### Prerequisites

1. **ffmpeg**: `brew install ffmpeg`
2. **Groq API key** (free): https://console.groq.com/keys
3. **Configure the key**: `agent-reach configure groq-key` (hidden prompt)
4. **First run**: `agent-reach install --env=auto --system --channels=xiaoyuzhou` (needs explicit user approval)

### Check status

```bash
agent-reach doctor
```

> Markdown output is saved to `/tmp/` by default.

## Choosing a tool

| Scenario | Recommended tool |
|-----|---------|
| YouTube subtitles | yt-dlp; on failure, OpenCLI (at most 3 tries) → agent-reach transcribe |
| Bilibili video details / search | bili-cli |
| Bilibili subtitles | opencli bilibili subtitle |
| Podcast transcription | Xiaoyuzhou transcribe.sh |
| Audio or video with no subtitles | agent-reach transcribe (for Bilibili audio, run `bili audio` first) |
