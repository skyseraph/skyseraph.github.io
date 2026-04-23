"""main.py — 入口，串联采集 + 生成，输出 GitHub Actions outputs"""
import os
import sys
from datetime import datetime, timezone, timedelta

import config
from collect import collect_all
from generate import generate_draft


def today_cst() -> str:
    cst = timezone(timedelta(hours=8))
    return datetime.now(cst).strftime("%Y-%m-%d")


def set_output(key: str, value: str):
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"[output] {key}={value}")


def main():
    if not config.ANTHROPIC_API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY 未设置")
        sys.exit(1)

    date_str = os.environ.get("TARGET_DATE") or today_cst()
    print(f"[INFO] 目标日期: {date_str}")

    collected = collect_all(date_str)
    total = sum(len(v) for v in collected.values())
    print(f"[INFO] 采集总条目: {total}")

    if total == 0:
        print("[WARN] 无有效内容，跳过生成")
        set_output("has_content", "false")
        return

    file_path, issue_num, headline = generate_draft(collected, date_str)

    set_output("has_content", "true")
    set_output("file_path", file_path)
    set_output("issue_num", str(issue_num))
    set_output("headline", headline)
    set_output("date", date_str)


if __name__ == "__main__":
    main()
