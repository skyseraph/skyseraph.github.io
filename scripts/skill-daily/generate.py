"""generate.py — 调用 Claude API 生成 Skill 日报草稿

将 skill-weekly SKILL.md Step 3-6 的逻辑封装为 Claude API prompt：
- Step 3: 评分筛选 → 通过 prompt 要求 Claude 内化评分逻辑
- Step 4: 逐项目深度调研 → 基于 GitHub API 返回的元数据 + Claude 补充
- Step 5: 趋势合成与洞察 → 通过 prompt 生成
- Step 6: 写入报告文件 → 生成 markdown 并写入 content 目录
"""
import glob
import json
import os
import re
from datetime import datetime, timezone, timedelta

import anthropic

import config


def _next_issue() -> int:
    """计算下一期期数"""
    files = glob.glob(f"{config.SERIES_DIR}/**/*.md", recursive=True)
    return len([f for f in files if "_index" not in f]) + 1


def _extract_template() -> str:
    """从 templates.md 提取日报 markdown 模板"""
    try:
        text = open(config.TEMPLATE_PATH, encoding="utf-8").read()
        m = re.search(r"```markdown\n(.*?)```", text, re.DOTALL)
        return m.group(1).strip() if m else ""
    except FileNotFoundError:
        print(f"[WARN] Template file not found: {config.TEMPLATE_PATH}")
        return ""


def _today_cst() -> str:
    """获取 CST 今天日期"""
    cst = timezone(timedelta(hours=8))
    return datetime.now(cst).strftime("%Y-%m-%d")


def _extract_headline(content: str) -> str:
    """从 frontmatter 提取 headline（标题 · 之后的部分）"""
    m = re.search(r'^title:\s*".*?·\s*(.+?)"', content, re.MULTILINE)
    return m.group(1).strip()[:40] if m else "Skill日报"


def _fix_frontmatter(content: str, issue: int, date_str: str) -> str:
    """修正 frontmatter 中的 issue、date、draft"""
    content = re.sub(r"(issue:\s*)\d+", f"\\g<1>{issue}", content)
    content = re.sub(r"(date:\s*)\S+", f"\\g<1>{date_str}T11:00:00+08:00", content)
    content = re.sub(r"draft:\s*false", "draft: true", content)
    if "draft:" not in content:
        content = content.replace("toc: false", "toc: false\ndraft: true", 1)
    return content


def generate_draft(collected: dict, date_str: str | None = None) -> tuple[str, int, str]:
    """生成 Skill 日报草稿

    Args:
        collected: collect_all() 返回的分类数据
        date_str: 目标日期 (YYYY-MM-DD)

    Returns: (file_path, issue_num, headline)
    """
    date_str = date_str or _today_cst()
    issue = _next_issue()
    template = _extract_template()

    # 计算时间窗口起始
    d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    window_start = (d - timedelta(hours=config.TIME_WINDOW_HOURS)).strftime("%Y-%m-%d")

    data_json = json.dumps(collected, ensure_ascii=False, indent=2)

    prompt = f"""你是 AI Skill 生态资深分析师，请根据以下采集数据生成一期 Skill 日报草稿。

## 采集数据
{data_json}

## 输出模板
{template}

## 时间窗口
本期覆盖：{window_start} ～ {date_str}（过去 24h）

## 评分筛选规则（Skill 相关性 40 + 新鲜度 25 + 热度 20 + 可用性 15 = 总分 100）

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| Skill 相关性 | 40 | 核心功能聚焦 AI Skill → 40 / 相关 → 20 / 边缘 → 5 |
| 新鲜度 | 25 | 过去 24h 内有提交或创建 → 25 / 近 48h → 15 / 更早 → 5 |
| 热度 | 20 | 新项目 ≥20 stars → 20 / 老项目 ≥100 stars → 20 / 其他 → 5-10 |
| 可用性 | 15 | 有可运行代码+清晰文档 → 15 / 基本可用 → 8 / README-only → 0 |

筛选规则：
- 总分 ≥ 50 → 纳入「今日榜」（主榜，日报 3-5 项）
- 创建日期在本期 24h 时间窗口内 + Skill 相关性 ≥ 20 → 纳入「新项目速递」（2-3 项）
- 若同时满足两榜条件 → 新项目速递中标注 ★ 双榜入选
- 总分 40-49 → 纳入「候补」（简列 1-2 项）
- 总分 < 40 → 排除

## 约束规则
- 所有项目 URL 必须来自采集数据，禁止编造任何 GitHub URL
- Stars 数据必须来自采集数据，不得估算；若缺失标注 [未知]
- frontmatter 中 issue={issue}，date={date_str}T11:00:00+08:00，draft=true
- 标题 headline 不超过 30 字，提炼最重要的 1 个趋势
- 今日趋势 2-3 条，每条有代表项目名
- 今日榜 3-5 个项目（每个项目有定位、Stars、语言、更新日期、核心功能、链接）
- 新项目速递 2-3 个项目（标注创建日期）
- 候补项目简列即可
- 如采集数据不足（某个类别条目 < 3），如实注明"今日数据有限"，不编造内容
- 输出纯 Markdown，不加任何解释或前言
"""

    client_kwargs = {"api_key": config.ANTHROPIC_API_KEY}
    if config.ANTHROPIC_BASE_URL:
        client_kwargs["base_url"] = config.ANTHROPIC_BASE_URL
    client = anthropic.Anthropic(**client_kwargs)
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    # 提取文本内容：只取 TextBlock，跳过 ThinkingBlock 等非文本块
    # 使用 SDK 类型精确判断，避免 ThinkingBlock.text 被误提取
    from anthropic.types import TextBlock, ThinkingBlock

    text_blocks = [b for b in msg.content if isinstance(b, TextBlock)]
    content = "\n".join(b.text for b in text_blocks).strip()

    if not content:
        # 兜底：用 type name 判断（兼容 DashScope 等代理可能返回的非标准类型）
        text_blocks = [b for b in msg.content
                       if type(b).__name__ == "TextBlock" and hasattr(b, "text")]
        content = "\n".join(b.text for b in text_blocks).strip()

    if not content:
        # 最终兜底：任何有 .text 属性且非 ThinkingBlock 的块
        content = "\n".join(
            getattr(b, "text", "") for b in msg.content
            if hasattr(b, "text") and not isinstance(b, ThinkingBlock)
            and type(b).__name__ != "ThinkingBlock"
        ).strip()

    if not content:
        print(f"[ERROR] Claude API 返回内容为空 (blocks: {len(msg.content)}, "
              f"types: {[type(b).__name__ for b in msg.content]}, "
              f"stop_reason: {msg.stop_reason})")
        return "", 0, ""

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
