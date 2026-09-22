# Groq Whisper setup guide

## What it does
When a YouTube or Bilibili video has no subtitles, use Groq's Whisper API for speech-to-text. Groq includes a free quota.

## Steps the agent can do

1. Check whether it is already configured:
```bash
agent-reach doctor | grep -i "groq\|whisper"
```

2. If the user provided a key, write it into config:
```python
from agent_reach.config import Config
c = Config()
c.set("groq_api_key", "USER_PROVIDED_KEY")
```

3. Optional test:
```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer USER_PROVIDED_KEY" \
  -o /dev/null -w "%{http_code}"
```
A 200 response means it works.

## Steps the user must do by hand

Tell the user:

> Speech-to-text for videos needs a Groq API key (free).
>
> Steps:
> 1. Open https://console.groq.com
> 2. Sign up with a Google account or email
> 3. Click "API Keys" on the left
> 4. Click "Create API Key"
> 5. Copy the generated key and send it to me
>
> Groq includes a free quota, which is enough for everyday use.

## After the agent receives the key

1. Write it into config: `config.set("groq_api_key", key)`
2. Test that the API is usable
3. Reply: "Speech-to-text is on. When a video has no subtitles, I can still extract the content for you."
