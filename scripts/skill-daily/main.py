"""main.py — Skill 日报入口，串联采集 + 生成，本地发布

用法：
  python3 main.py               # 今日日报（草稿 draft: true）
  python3 main.py publish       # 今日日报（发布 draft: false + git commit/push）
  python3 main.py 2026-07-01    # 指定日期
  python3 main.py publish 2026-07-01  # 指定日期 + 发布
"""
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

import config
from collect import collect_all
from generate import generate_draft


def today_cst() -> str:
    cst = timezone(timedelta(hours=8))
    return datetime.now(cst).strftime("%Y-%m-%d")


def _set_draft(file_path: str, draft: bool) -> None:
    """修改文件中的 draft 字段"""
    import re
    content = open(file_path, encoding="utf-8").read()
    content = re.sub(r"draft:\s*true", f"draft: {draft}", content)
    content = re.sub(r"draft:\s*false", f"draft: {draft}", content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def _git_publish(file_path: str, issue_num: int, headline: str) -> None:
    """git add + commit + push"""
    try:
        subprocess.run(["git", "add", file_path], check=True)
        msg = f"feat: Skill日报 #{issue_num} · {headline}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"[OK] 已推送：{msg}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] git 操作失败：{e}")
        sys.exit(1)


def main():
    # 解析参数
    args = sys.argv[1:]
    publish = "publish" in args
    date_arg = next((a for a in args if a != "publish"), None)

    if not config.ANTHROPIC_API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY 未设置")
        print("  请编辑 inner/api_keys.yml 填写 api_key")
        sys.exit(1)

    date_str = date_arg or today_cst()
    print(f"[INFO] 目标日期: {date_str}")
    print(f"[INFO] 模式: {'发布' if publish else '草稿'}")

    # 采集
    collected = collect_all(date_str)
    total = sum(len(v) for v in collected.values())
    print(f"[INFO] 采集总条目: {total}")

    if total < 3:
        print(f"[WARN] 有效内容仅 {total} 条，不足以生成日报，跳过")
        return

    # 生成
    file_path, issue_num, headline = generate_draft(collected, date_str)

    # 发布模式：draft: false + git push
    if publish:
        _set_draft(file_path, False)
        _git_publish(file_path, issue_num, headline)
    else:
        print(f"[INFO] 草稿已生成：{file_path}")
        print(f"[INFO] Review 后手动发布：python3 main.py publish {date_str}")


if __name__ == "__main__":
    main()
