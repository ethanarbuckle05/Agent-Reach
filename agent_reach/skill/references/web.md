# Web reading

General web pages and RSS.

## General web pages (Jina Reader)

```bash
# Read any web page
curl -s "https://r.jina.ai/URL"

# Example
curl -s "https://r.jina.ai/https://example.com/article"
```

**Best for**: most pages can be read directly with Jina Reader.

## Web Reader (MCP)

```bash
# Read page content (Markdown)
mcporter call web-reader.webReader url="https://example.com"

# Keep images
mcporter call web-reader.webReader url="https://example.com" retain_images=true

# Plain text
mcporter call web-reader.webReader url="https://example.com" return_format="text"
```

**Best for**: when you need tighter control over the output format.

## RSS (feedparser)

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

**Best for**: subscribing to blogs, news sources, podcasts, and other RSS feeds.

## Choosing a tool

| Scenario | Recommended tool |
|-----|---------|
| General web pages | Jina Reader (`curl r.jina.ai`) |
| Images or format control | web-reader MCP |
| RSS subscriptions | feedparser |
