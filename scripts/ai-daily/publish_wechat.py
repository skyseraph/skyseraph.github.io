"""publish_wechat.py — 推送微信公众号草稿箱"""
import json
import re
import sys

import markdown
import requests

import config

WECHAT_API = "https://api.weixin.qq.com/cgi-bin"


def _get_access_token() -> str:
    resp = requests.get(
        f"{WECHAT_API}/token",
        params={"grant_type": "client_credential",
                "appid": config.WECHAT_APP_ID,
                "secret": config.WECHAT_APP_SECRET},
        timeout=config.REQUEST_TIMEOUT,
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"获取 access_token 失败: {data}")
    return data["access_token"]


def _parse_frontmatter(text: str) -> tuple[str, str]:
    """返回 (title, body_markdown)"""
    m = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not m:
        return "AI日报", text
    fm, body = m.group(1), m.group(2)
    title_m = re.search(r'^title:\s*"(.+?)"', fm, re.MULTILINE)
    title = title_m.group(1) if title_m else "AI日报"
    return title, body.strip()


def _md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["tables", "fenced_code"])


def push_draft(file_path: str) -> str:
    text = open(file_path, encoding="utf-8").read()
    title, body_md = _parse_frontmatter(text)
    html_content = _md_to_html(body_md)

    token = _get_access_token()
    payload = {
        "articles": [{
            "title": title,
            "author": "SkySeraph",
            "content": html_content,
            "content_source_url": "https://skyseraph.github.io/series/ai-daily/",
            "thumb_media_id": config.WECHAT_THUMB_MEDIA_ID,
            "need_open_comment": 1,
        }]
    }
    resp = requests.post(
        f"{WECHAT_API}/draft/add",
        params={"access_token": token},
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=config.REQUEST_TIMEOUT,
    )
    result = resp.json()
    if "media_id" not in result:
        raise RuntimeError(f"创建草稿失败: {result}")
    media_id = result["media_id"]
    print(f"[OK] 微信草稿已创建，media_id: {media_id}")
    return media_id


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python publish_wechat.py <file_path>")
        sys.exit(1)
    if not config.WECHAT_APP_ID or not config.WECHAT_APP_SECRET:
        print("[SKIP] 未配置微信公众号 Secrets，跳过发布")
        sys.exit(0)
    push_draft(sys.argv[1])
