"""collect.py — 多源信息采集 + 过滤"""
import json
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

import feedparser
import requests
import yaml

import config


def _cutoff(target_date: str | None) -> datetime:
    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        d = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return d - timedelta(hours=config.COLLECT_GRACE_HOURS)


def _is_ai_related(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in keywords)


def _normalize(title: str, url: str, summary: str, source: str, ts: str, category: str) -> dict:
    return {"title": title, "url": url, "summary": summary[:300],
            "source": source, "time": ts, "category": category}


def _parse_ts(value, fmt: str) -> datetime | None:
    try:
        if fmt == "pubDate":
            return parsedate_to_datetime(value).astimezone(timezone.utc)
        if fmt in ("time", "created_utc"):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        if fmt == "html":
            return datetime.now(timezone.utc)  # HTML 源无精确时间，视为当前
    except Exception:
        return None


# ── 各类型 fetcher ────────────────────────────────────────────

def _fetch_rss(src: dict, cutoff: datetime, keywords: list[str]) -> list[dict]:
    resp = requests.get(src["url"], headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
    feed = feedparser.parse(resp.text)
    items = []
    for entry in feed.entries:
        ts = _parse_ts(entry.get("published", ""), src["time_field"])
        if ts and ts < cutoff:
            continue
        title = entry.get("title", "")
        if src.get("filter_keywords") and not _is_ai_related(title, keywords):
            continue
        items.append(_normalize(
            title=title,
            url=entry.get("link", ""),
            summary=entry.get("summary", "")[:300],
            source=src["label"],
            ts=ts.strftime("%Y-%m-%d %H:%M UTC") if ts else "",
            category=src["category"],
        ))
    return items


def _fetch_hn(src: dict, cutoff: datetime, keywords: list[str]) -> list[dict]:
    ids = requests.get(src["url"], headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT).json()
    items = []
    for id_ in ids[:src.get("limit", 30)]:
        try:
            item = requests.get(
                src["item_url"].format(id=id_),
                headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT
            ).json()
            ts = _parse_ts(item.get("time", 0), "time")
            if ts and ts < cutoff:
                continue
            title = item.get("title", "")
            if not _is_ai_related(title, keywords):
                continue
            items.append(_normalize(
                title=title,
                url=item.get("url", f"https://news.ycombinator.com/item?id={id_}"),
                summary="",
                source=src["label"],
                ts=ts.strftime("%Y-%m-%d %H:%M UTC") if ts else "",
                category=src["category"],
            ))
        except Exception:
            continue
    return items


def _fetch_reddit(src: dict, cutoff: datetime, keywords: list[str]) -> list[dict]:
    headers = {**config.HEADERS, "Accept": "application/json"}
    data = requests.get(src["url"], headers=headers, timeout=config.REQUEST_TIMEOUT).json()
    items = []
    for child in data.get("data", {}).get("children", []):
        post = child["data"]
        ts = _parse_ts(post.get("created_utc", 0), "created_utc")
        if ts and ts < cutoff:
            continue
        title = post.get("title", "")
        if src.get("filter_keywords") and not _is_ai_related(title, keywords):
            continue
        items.append(_normalize(
            title=title,
            url=post.get("url", ""),
            summary=post.get("selftext", "")[:300],
            source=src["label"],
            ts=ts.strftime("%Y-%m-%d %H:%M UTC") if ts else "",
            category=src["category"],
        ))
    return items


def _dispatch(src: dict, cutoff: datetime, keywords: list[str]) -> list[dict]:
    key = src["key"]
    if key == "hackernews":
        return _fetch_hn(src, cutoff, keywords)
    if key.startswith("reddit"):
        return _fetch_reddit(src, cutoff, keywords)
    return _fetch_rss(src, cutoff, keywords)


# ── 主入口 ────────────────────────────────────────────────────

def collect_all(target_date: str | None = None) -> dict:
    cfg = yaml.safe_load(open(config.SOURCES_YML, encoding="utf-8"))
    keywords = cfg["keywords"]["must_include"]
    cutoff = _cutoff(target_date)
    results: dict[str, list] = {"paper": [], "news": [], "tool": [], "newsletter": []}

    for src in cfg["sources"]:
        if src.get("enabled") is False:
            continue
        try:
            items = _dispatch(src, cutoff, keywords)
            results[src["category"]].extend(items)
            print(f"[OK] {src['key']}: {len(items)} items")
        except Exception as e:
            print(f"[WARN] {src['key']} failed: {e}")

    return results


if __name__ == "__main__":
    import json, sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    result = collect_all(date)
    for cat, items in result.items():
        print(f"\n── {cat} ({len(items)}) ──")
        for it in items[:2]:
            print(f"  {it['title'][:60]}")
