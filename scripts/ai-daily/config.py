"""config.py — AI 日报配置常量

API key 从 inner/api_keys.yml 读取（gitignore 目录，不会推送到 GitHub）
也可通过环境变量覆盖（ANTHROPIC_API_KEY / GH_TOKEN）
"""
import os
import yaml

# ── 读取密钥配置 ──────────────────────────────────────────────────
_KEYS_PATH = "inner/api_keys.yml"

def _load_keys():
    try:
        with open(_KEYS_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[WARN] {_KEYS_PATH} 不存在，请创建并填写 API key")
        return {}

_keys = _load_keys()

# ── API（环境变量优先，否则读配置文件）───────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or (_keys.get("anthropic", {}) or {}).get("api_key", "")
ANTHROPIC_MODEL   = os.environ.get("ANTHROPIC_MODEL")  or (_keys.get("anthropic", {}) or {}).get("model", "claude-haiku-4-5")
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL") or (_keys.get("anthropic", {}) or {}).get("base_url", "")
GH_TOKEN          = os.environ.get("GH_TOKEN")          or (_keys.get("github", {}) or {}).get("token", "")

# ── 微信（仅 ai-daily 使用）─────────────────────────────────────
WECHAT_APP_ID          = os.environ.get("WECHAT_APP_ID", "")
WECHAT_APP_SECRET      = os.environ.get("WECHAT_APP_SECRET", "")
WECHAT_THUMB_MEDIA_ID  = os.environ.get("WECHAT_THUMB_MEDIA_ID", "")

# ── 路径 ─────────────────────────────────────────────────────────
SOURCES_YML   = ".claude/skills/ai.daily/sources.yml"
TEMPLATE_PATH = ".claude/skills/ai.daily/templates.md"
SERIES_DIR    = "content/series/ai-daily"

# ── 采集 ─────────────────────────────────────────────────────────
COLLECT_GRACE_HOURS = 4
REQUEST_TIMEOUT     = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Daily-Bot/1.0; +https://github.com/skyseraph)"}
