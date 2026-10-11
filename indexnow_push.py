#!/usr/bin/env python3
"""IndexNow 全站推送：把 sitemap 里的所有 URL 一次性推给必应。
用法：python3 indexnow_push.py          （推送全站）
     python3 indexnow_push.py url1 url2 （只推指定 URL）
"""
import sys
import urllib.request
import urllib.error
from pathlib import Path

KEY = (Path(__file__).parent / "IndexNow.key").read_text(encoding="utf8").strip()
BASE = "https://qingdan.lazyso.com"
LOC = f"{BASE}/{KEY}.txt"


def all_urls() -> list[str]:
    sm = (Path(__file__).parent / "dist" / "sitemap.xml").read_text(encoding="utf8")
    return [u.strip() for u in sm.split("<loc>")[1:]]


def push(urls: list[str]) -> None:
    body = {
        "host": "qingdan.lazyso.com",
        "key": KEY,
        "keyLocation": LOC,
        "urlList": urls,
    }
    import json
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(body).encode("utf8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"HTTP {r.status} — 已推送 {len(urls)} 条 URL")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {e.reason}：{e.read().decode(errors='ignore')[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    urls = sys.argv[1:] or all_urls()
    if not urls:
        print("没有可推送的 URL，先跑 build.py 生成 sitemap")
        sys.exit(1)
    push(urls)
