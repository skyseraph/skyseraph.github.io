import os

ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL    = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

WECHAT_APP_ID          = os.environ.get("WECHAT_APP_ID", "")
WECHAT_APP_SECRET      = os.environ.get("WECHAT_APP_SECRET", "")
WECHAT_THUMB_MEDIA_ID  = os.environ.get("WECHAT_THUMB_MEDIA_ID", "")

SOURCES_YML   = ".claude/skills/ai.daily/sources.yml"
TEMPLATE_PATH = ".claude/skills/ai.daily/templates.md"
SERIES_DIR    = "content/series/ai-daily"

COLLECT_GRACE_HOURS = 4
REQUEST_TIMEOUT     = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Daily-Bot/1.0; +https://github.com/skyseraph)"}
