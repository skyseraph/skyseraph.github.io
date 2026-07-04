"""config.py — Skill 日报配置常量"""
import os

# ── API ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
GH_TOKEN          = os.environ.get("GH_TOKEN", "")  # GitHub API auth (GH_PAT)

# ── 路径 ─────────────────────────────────────────────────────────
SOURCES_YML   = ".claude/skills/skill.daily/sources.yml"
TEMPLATE_PATH = ".claude/skills/skill.daily/templates.md"
SERIES_DIR    = "content/series/skill-daily"

# ── 采集 ─────────────────────────────────────────────────────────
TIME_WINDOW_HOURS    = 24       # 日级别：过去 24h
COLLECT_GRACE_HOURS  = 4        # 宽容窗口
REQUEST_TIMEOUT      = 15       # HTTP 超时 (秒)
GH_SEARCH_PER_PAGE   = 30       # GitHub Search API 每页条数
GH_SEARCH_MAX_PAGES  = 2        # 最大翻页数

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Skill-Daily-Bot/1.0; +https://github.com/skyseraph)",
    "Accept": "application/vnd.github.v3+json",
}
