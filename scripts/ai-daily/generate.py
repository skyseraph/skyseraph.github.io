"""generate.py — 调用 Claude API 生成日报草稿"""
import glob
import json
import os
import re
from datetime import datetime, timezone, timedelta

import anthropic

import config


def _next_issue() -> int:
    files = glob.glob(f"{config.SERIES_DIR}/**/*.md", recursive=True)
    return len([f for f in files if "_index" not in f]) + 1


def _extract_template() -> str:
    text = open(config.TEMPLATE_PATH, encoding="utf-8").read()
    m = re.search(r"```markdown\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def _today_cst() -> str:
    cst = timezone(timedelta(hours=8))
    return datetime.now(cst).strftime("%Y-%m-%d")


def _extract_headline(content: str) -> str:
    m = re.search(r'^title:\s*".*?·\s*(.+?)"', content, re.MULTILINE)
    return m.group(1).strip()[:40] if m else "AI日报"


def _fix_frontmatter(content: str, issue: int, date_str: str) -> str:
    content = re.sub(r"(issue:\s*)\d+", f"\\g<1>{issue}", content)
    content = re.sub(r"(date:\s*)\S+", f"\\g<1>{date_str}T08:00:00+08:00", content)
    content = re.sub(r"draft:\s*false", "draft: true", content)
    if "draft:" not in content:
        content = content.replace("toc: false", "toc: false\ndraft: true", 1)
    return content


def generate_draft(collected: dict, date_str: str | None = None) -> tuple[str, int, str]:
    date_str = date_str or _today_cst()
    issue = _next_issue()
    template = _extract_template()

    data_json = json.dumps(collected, ensure_ascii=False, indent=2)
    prompt = f"""你是 AI 领域资深中文编辑，请根据以下采集数据生成一期 AI 日报草稿。

## 采集数据
{data_json}

## 输出模板
{template}

## 约束规则
- 所有链接必须来自采集数据，禁止编造任何 URL
- frontmatter 中 issue={issue}，date={date_str}，draft=true
- 标题 headline 不超过 30 字，提炼最重要的 1-2 个事件
- 焦点事件选 3-5 条，论文速递选 2-3 篇，工具选 3-5 个，行业动态选 3-5 条
- 如某类数据不足，该板块可缩减条目，不要编造内容
- 输出纯 Markdown，不加任何解释或前言
"""

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    content = msg.content[0].text.strip()

    # 去掉模型可能包裹的 ```markdown 代码块
    content = re.sub(r"^```markdown\n?", "", content)
    content = re.sub(r"\n?```$", "", content)

    content = _fix_frontmatter(content, issue, date_str)

    year = date_str[:4]
    out_dir = f"{config.SERIES_DIR}/{year}"
    os.makedirs(out_dir, exist_ok=True)
    file_path = f"{out_dir}/{issue:03d}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    headline = _extract_headline(content)
    print(f"[OK] 生成草稿：{file_path}（#{issue} · {headline}）")
    return file_path, issue, headline


if __name__ == "__main__":
    import sys
    from collect import collect_all
    date = sys.argv[1] if len(sys.argv) > 1 else None
    collected = collect_all(date)
    fp, num, hl = generate_draft(collected, date)
    print(f"file: {fp}\nissue: {num}\nheadline: {hl}")
