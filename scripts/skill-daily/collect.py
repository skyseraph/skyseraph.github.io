"""collect.py — GitHub Skill 生态数据采集

映射 skill-weekly SKILL.md Step 2 搜索策略到 GitHub REST API。
采集 Skill 相关项目，分类为 trending / framework / eval / orchestration / new。
"""
import json
import time
from datetime import datetime, timezone, timedelta

import requests
import yaml
from bs4 import BeautifulSoup

import config


# ── 时间工具 ────────────────────────────────────────────────────

def _cutoff(target_date: str | None) -> datetime:
    """计算采集截止时间（默认 = 目标日期 00:00 UTC - 宽容小时数）"""
    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        d = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return d - timedelta(hours=config.COLLECT_GRACE_HOURS)


def _date_range_start(target_date: str | None) -> str:
    """日级别时间窗口起始日期（YYYY-MM-DD），过去 24h"""
    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        d = datetime.now(timezone.utc)
    start = d - timedelta(hours=config.TIME_WINDOW_HOURS)
    return start.strftime("%Y-%m-%d")


# ── GitHub Search API ────────────────────────────────────────────

def _gh_headers() -> dict:
    """构造 GitHub API请求头，有 token 时带上认证"""
    h = dict(config.HEADERS)
    if config.GH_TOKEN:
        h["Authorization"] = f"token {config.GH_TOKEN}"
    return h


def _fetch_github_search(query: str, sort: str = "stars", order: str = "desc",
                         cutoff_date: str | None = None) -> list[dict]:
    """通过 GitHub Search API 搜索 repositories

    Args:
        query: 搜索查询字符串
        sort: 排序字段 (stars / updated / created)
        order: 排序方向 (desc / asc)
        cutoff_date: pushed:>YYYY-MM-DD 过滤条件

    Returns: 项目列表，每个元素包含 full_name, url, stars, description, language,
             created_at, updated_at, topics, category_from_query
    """
    # 构造查询参数
    q = query
    if cutoff_date:
        q += f" pushed:>{cutoff_date}"

    url = "https://api.github.com/search/repositories"
    items = []

    for page in range(1, config.GH_SEARCH_MAX_PAGES + 1):
        params = {
            "q": q,
            "sort": sort,
            "order": order,
            "per_page": config.GH_SEARCH_PER_PAGE,
            "page": page,
        }
        try:
            resp = requests.get(url, headers=_gh_headers(), params=params,
                                timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 403:
                print(f"[WARN] GitHub API rate limit hit, waiting 60s...")
                time.sleep(60)
                resp = requests.get(url, headers=_gh_headers(), params=params,
                                    timeout=config.REQUEST_TIMEOUT)
            if resp.status_code != 200:
                print(f"[WARN] GitHub Search API error: {resp.status_code}")
                break

            data = resp.json()
            total_count = data.get("total_count", 0)
            page_items = data.get("items", [])

            for repo in page_items:
                items.append({
                    "full_name": repo.get("full_name", ""),
                    "url": repo.get("html_url", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "description": (repo.get("description") or "")[:200],
                    "language": repo.get("language", ""),
                    "created_at": repo.get("created_at", ""),
                    "updated_at": repo.get("pushed_at", ""),
                    "topics": repo.get("topics", []),
                    "fork": repo.get("fork", False),
                })

            # 如果结果不够下一页，提前退出
            if total_count <= page * config.GH_SEARCH_PER_PAGE:
                break

        except Exception as e:
            print(f"[WARN] GitHub search failed (page {page}): {e}")
            break

    return items


# ── GitHub Trending 抓取 ─────────────────────────────────────────

def _fetch_github_trending(since: str = "daily") -> list[dict]:
    """抓取 GitHub Trending 页面，提取当日热门 AI/Skill 项目

    Args:
        since: daily / weekly / monthly

    Returns: 项目列表
    """
    url = f"https://github.com/trending?since={since}"
    try:
        resp = requests.get(url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        articles = soup.select("article.Box-row")
        for article in articles:
            # 提取仓库名
            repo_link = article.select_one("h2 a")
            if not repo_link:
                continue
            href = repo_link.get("href", "").strip("/")
            full_name = href

            # 提取描述
            desc_el = article.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""

            # 提取语言
            lang_el = article.select_one("[itemprop='programmingLanguage']")
            language = lang_el.get_text(strip=True) if lang_el else ""

            # 提取 stars
            stars_el = article.select_one("a[href$='/stargazers']")
            stars_text = stars_el.get_text(strip=True) if stars_el else "0"
            # 处理 "1,234" 格式
            stars = int(stars_text.replace(",", "").replace(".", "").replace("k", "000")[:10]) if stars_text and stars_text[0].isdigit() else 0

            # 提取 today stars
            today_el = article.select_one(".d-inline-block.float-sm-right")
            today_stars = 0
            if today_el:
                t = today_el.get_text(strip=True)
                # "1,234 stars today"
                for part in t.split():
                    if part.replace(",", "").isdigit():
                        today_stars = int(part.replace(",", ""))
                        break

            items.append({
                "full_name": full_name,
                "url": f"https://github.com/{full_name}",
                "stars": stars,
                "description": description[:200],
                "language": language,
                "created_at": "",  # Trending 页面无创建日期
                "updated_at": "",  # Trending 页面无更新日期
                "topics": [],
                "fork": False,
                "today_stars": today_stars,
            })

        return items

    except Exception as e:
        print(f"[WARN] GitHub Trending scrape failed: {e}")
        return []


# ── 关键词过滤 ──────────────────────────────────────────────────

def _is_skill_related(item: dict, keywords: list[str]) -> bool:
    """检查项目是否与 Skill 生态相关"""
    text = (item.get("description", "") + " " +
            " ".join(item.get("topics", [])) + " " +
            item.get("full_name", "")).lower()

    # 排除 fork
    if item.get("fork"):
        return False

    return any(k.lower() in text for k in keywords)


# ── 去重 ─────────────────────────────────────────────────────────

def _dedup(items: list[dict]) -> list[dict]:
    """按 full_name 去重"""
    seen = set()
    result = []
    for item in items:
        name = item.get("full_name", "")
        if name and name not in seen:
            seen.add(name)
            result.append(item)
    return result


# ── 主入口 ──────────────────────────────────────────────────────

def collect_all(target_date: str | None = None) -> dict:
    """采集所有 Skill 生态数据，返回分类字典

    Returns: {
        "trending": [...],
        "framework": [...],
        "eval": [...],
        "orchestration": [...],
        "new": [...],
    }
    """
    # 读取 sources.yml 配置
    try:
        cfg = yaml.safe_load(open(config.SOURCES_YML, encoding="utf-8"))
    except FileNotFoundError:
        print(f"[WARN] sources.yml not found at {config.SOURCES_YML}, using defaults")
        cfg = None

    keywords = cfg.get("keywords", {}).get("skill_core", []) if cfg else [
        "SKILL.md", "skill-spec", "skill-agent", "skill",
    ]
    keywords += cfg.get("keywords", {}).get("agent_core", []) if cfg else [
        "agent", "LLM", "tool-use", "function-calling", "tool-calling",
    ]

    cutoff_date = _date_range_start(target_date)
    cutoff = _cutoff(target_date)

    results: dict[str, list] = {
        "trending": [],
        "framework": [],
        "eval": [],
        "orchestration": [],
        "new": [],
    }

    # ── 2A: GitHub Trending ─────────────────────────
    print("[INFO] Fetching GitHub Trending...")
    trending = _fetch_github_trending("daily")
    trending = [i for i in trending if _is_skill_related(i, keywords)]
    results["trending"] = trending
    print(f"[OK] trending: {len(trending)} items")

    # ── 2B: Skill 框架与规格 ─────────────────────────
    print("[INFO] Searching Skill frameworks...")
    queries_b = cfg.get("sources", []) if cfg else []
    framework_queries = [
        q for q in queries_b if q.get("category") == "framework"
    ] if cfg else [
        "SKILL.md OR skill-spec OR skill-agent OR tool-calling OR function-calling",
    ]

    framework_items = []
    for q in framework_queries:
        query_str = q.get("query", q) if isinstance(q, dict) else q
        items = _fetch_github_search(query_str, sort="stars", cutoff_date=cutoff_date)
        framework_items.extend(items)

    framework_items = _dedup(framework_items)
    framework_items = [i for i in framework_items if _is_skill_related(i, keywords)]
    results["framework"] = framework_items
    print(f"[OK] framework: {len(framework_items)} items")

    # ── 2C: Skill 评测与进化 ──────────────────────────
    print("[INFO] Searching Skill evaluation...")
    eval_queries = [
        q for q in queries_b if q.get("category") == "eval"
    ] if cfg else [
        "skill-evaluation OR skill-eval OR skill-optimization OR skill-learning OR skill-evolution",
    ]

    eval_items = []
    for q in eval_queries:
        query_str = q.get("query", q) if isinstance(q, dict) else q
        items = _fetch_github_search(query_str, sort="stars", cutoff_date=cutoff_date)
        eval_items.extend(items)

    eval_items = _dedup(eval_items)
    eval_items = [i for i in eval_items if _is_skill_related(i, keywords)]
    results["eval"] = eval_items
    print(f"[OK] eval: {len(eval_items)} items")

    # ── 2D: 编排与调度 ────────────────────────────────
    print("[INFO] Searching Skill orchestration...")
    orch_queries = [
        q for q in queries_b if q.get("category") == "orchestration"
    ] if cfg else [
        "skill-orchestration OR skill-chain OR skill-registry OR skill-routing OR skill-store",
    ]

    orch_items = []
    for q in orch_queries:
        query_str = q.get("query", q) if isinstance(q, dict) else q
        items = _fetch_github_search(query_str, sort="stars", cutoff_date=cutoff_date)
        orch_items.extend(items)

    orch_items = _dedup(orch_items)
    orch_items = [i for i in orch_items if _is_skill_related(i, keywords)]
    results["orchestration"] = orch_items
    print(f"[OK] orchestration: {len(orch_items)} items")

    # ── 2E: 新项目专项搜索 ─────────────────────────────
    print("[INFO] Searching new Skill repos (24h window)...")
    target = target_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # 搜索过去 24h 新创建的项目
    new_queries = [
        q for q in queries_b if q.get("category") == "new"
    ] if cfg else []

    new_items = []
    if new_queries:
        for q in new_queries:
            query_str = q.get("query", q) if isinstance(q, dict) else q
            created_after = (datetime.strptime(target, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                            - timedelta(hours=config.TIME_WINDOW_HOURS)).strftime("%Y-%m-%d")
            items = _fetch_github_search(query_str, sort="created",
                                        cutoff_date=cutoff_date)
            # 仅保留创建日期在窗口内的
            for item in items:
                ca = item.get("created_at", "")
                if ca and ca[:10] >= created_after:
                    new_items.append(item)
    else:
        # 默认搜索：skill agent LLM created:过去24h
        created_after = (datetime.strptime(target, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                        - timedelta(hours=config.TIME_WINDOW_HOURS)).strftime("%Y-%m-%d")
        items = _fetch_github_search(
            f"skill agent LLM created:>{created_after}",
            sort="created",
        )
        new_items.extend(items)

    new_items = _dedup(new_items)
    new_items = [i for i in new_items if _is_skill_related(i, keywords)]
    results["new"] = new_items
    print(f"[OK] new: {len(new_items)} items")

    # ── 总计 ──────────────────────────────────────────
    total = sum(len(v) for v in results.values())
    print(f"[INFO] 采集总条目: {total}")

    return results


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    result = collect_all(date)
    for cat, items in result.items():
        print(f"\n── {cat} ({len(items)}) ──")
        for it in items[:3]:
            print(f"  {it['full_name']} ⭐{it['stars']} · {it['description'][:50]}")
