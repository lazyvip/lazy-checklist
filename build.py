#!/usr/bin/env python3
"""「懒人性价比清单」静态站生成器 v3
解析 HowToLiveBetter book/*.md（CC BY 4.0），生成零依赖静态站。
v3：修复条目页打勾按钮被标题盒遮挡的点击 bug（改为 flex 布局内嵌）；
    质感升级——渐变墨色标题、卡片悬浮抬升、打勾弹跳动效、滚动渐显、统计数字滚动。
"""
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
CONTENT = ROOT / "content" / "book"
DIST = ROOT / "dist"

SITE_TITLE = "懒人性价比清单"
SITE_SUB = "0 元 · 不费毅力 · 收益大 · 证据硬"
UPSTREAM = "https://github.com/eternity4719/HowToLiveBetter"
REPO_FILE = UPSTREAM + "/blob/main/book"
BASE_URL = "https://qingdan.lazyso.com"

TAG_RE = re.compile(r"<!--\s*成本标签:\s*([^>]+?)-->")
LEVEL_RE = re.compile(r"证据等级[:：]\s*([ABC])")


def parse_label(line: str) -> tuple[str, str]:
    m = re.match(r"-\s*(成本|说人话|收益|证据等级|来源|备注)[:：]\s*(.*)", line)
    if m:
        return m.group(1), m.group(2).strip()
    return "", ""


def parse_book() -> list[dict]:
    chapters = []
    for md in sorted(CONTENT.glob("*.md")):
        nn = md.stem.split("-")[0]
        text = md.read_text(encoding="utf8")
        h1 = re.search(r"^#\s*(\d+)\.\s*(.+)$", text, re.M)
        chap = {"nn": nn, "num": int(h1.group(1)) if h1 else int(nn),
                "title": h1.group(2).strip() if h1 else md.stem,
                "intro": "", "entries": []}
        first_h3 = text.find("### ")
        head = text[:first_h3] if first_h3 > 0 else ""
        for ln in head.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and not ln.startswith("[←"):
                chap["intro"] += ln
        blocks = re.split(r"(?=^### )", text[first_h3:], flags=re.M) if first_h3 > 0 else []
        for block in blocks:
            if not block.startswith("### "):
                continue
            lines = block.splitlines()
            m = re.match(r"###\s*(\d+)\.\s*(.+)", lines[0])
            if not m:
                continue
            num, title = int(m.group(1)), m.group(2).strip()
            tagm = TAG_RE.search(block)
            tags = {}
            if tagm:
                for kv in tagm.group(1).split():
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        tags[k] = v
            fields, level, body_lines = {}, "", []
            for ln in lines[1:]:
                ln = ln.strip()
                if not ln or ln.startswith("<!--"):
                    continue
                k, v = parse_label(ln)
                if k == "证据等级":
                    level = v
                    continue
                if k:
                    fields[k] = v
                else:
                    body_lines.append(ln)
            em = LEVEL_RE.search(block)
            if not level and em:
                level = em.group(1)
            chap["entries"].append({
                "id": f"{nn}-{num}", "num": num, "title": title,
                "tags": tags, "level": level, "fields": fields,
                "extra": body_lines,
            })
        chapters.append(chap)
    return chapters


def esc(s) -> str:
    s = str(s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def linkify(s: str) -> str:
    s = esc(s)
    return re.sub(r"(https?://[^\s<）)；、，。]+[^\s<）)；、，。])",
                  r'<a href="\1" target="_blank" rel="noopener nofollow">\1</a>', s)


CHIP_COLOR = {"0": "g", "少": "b", "否": "g", "些": "b", "要": "o",
              "大": "g", "中": "b", "小": "m", "多": "o"}


def tag_chip(k: str, v: str) -> str:
    return f'<span class="chip {CHIP_COLOR.get(v, "m")}">{esc(k)}={esc(v)}</span>'


def level_chip(lv: str) -> str:
    color = {"A": "g", "B": "b", "C": "o"}.get(lv, "m")
    return f'<span class="chip {color}">证据 {esc(lv or "—")}</span>'


def source_list(raw: str) -> str:
    items = [x.strip() for x in re.split(r"；|;", raw) if x.strip()]
    if len(items) <= 1:
        return f'<div class="cite">{linkify(raw)}</div>'
    lis = "".join(f'<li><span class="cno">[{i}]</span><span>{linkify(x)}</span></li>'
                  for i, x in enumerate(items, 1))
    return f'<ol class="cites">{lis}</ol>'


CSS = """:root{
--paper:#f6f3ec;--surface:#fffdf9;--ink:#211f1a;--body:#56524a;--mut:#a39d92;
--line:#e7e1d5;--line2:#d9d2c3;--green:#1f5c3d;--green-deep:#0f2a21;--green-soft:#e6efe6;
--amber:#b45309;--amber-soft:#fdf1e0;--blue:#3b6b8c;--blue-soft:#e6eef4;
--shadow-1:0 1px 2px rgba(28,25,23,.05),0 10px 30px -18px rgba(28,25,23,.25);
--serif:"Songti SC","Noto Serif SC",STSong,STZhongsong,ui-serif,Georgia,"Times New Roman",serif;
--sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}
@media(prefers-color-scheme:dark){:root{
--paper:#141311;--surface:#1d1c19;--ink:#ece7dd;--body:#b5afa4;--mut:#7d776c;
--line:#332f28;--line2:#453f35;--green:#7cb98f;--green-deep:#274a38;--green-soft:#243628;
--amber:#e0a458;--amber-soft:#3a2d1c;--blue:#82aec9;--blue-soft:#1f2d38;
--shadow-1:0 1px 2px rgba(0,0,0,.4),0 12px 32px -18px rgba(0,0,0,.7);}}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--sans);color:var(--ink);line-height:1.7;font-size:16px;-webkit-font-smoothing:antialiased;
background:var(--paper);background-image:radial-gradient(1100px 380px at 50% -120px,rgba(31,92,61,.09),transparent);}
::selection{background:var(--green);color:#fff}
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
/* header */
header{border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--paper) 86%,transparent);backdrop-filter:blur(10px);position:sticky;top:0;z-index:9}
header .wrap{display:flex;align-items:center;gap:12px;padding:12px 20px}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none}
.brand .mark{width:36px;height:36px;background:linear-gradient(145deg,var(--green-deep),var(--green));color:#f3efe6;font-family:var(--serif);font-size:20px;display:flex;align-items:center;justify-content:center;border-radius:9px;font-weight:700;box-shadow:var(--shadow-1)}
.brand .name{font-family:var(--serif);font-size:20px;font-weight:700;letter-spacing:.02em}
.brand .sub{font-size:12px;color:var(--mut)}
.top-nav{margin-left:auto;display:flex;gap:16px;font-size:13.5px}
.top-nav a{text-decoration:none;color:var(--body);padding:4px 2px;border-bottom:2px solid transparent;transition:color .15s ease,border-color .15s ease}
.top-nav a:hover{color:var(--ink);border-color:var(--green)}
main{padding:26px 0 90px}
/* hero */
.hero{padding:22px 0 6px}
.hero .kick{font-size:12.5px;color:var(--green);letter-spacing:.18em;font-weight:600}
.hero h2{font-family:var(--serif);font-size:38px;line-height:1.26;margin:12px 0 12px;font-weight:900;letter-spacing:.01em}
@supports(-webkit-background-clip:text){
.hero h2{background:linear-gradient(120deg,var(--ink) 30%,var(--green-deep));-webkit-background-clip:text;background-clip:text;color:transparent}}
@media(prefers-color-scheme:dark){.hero h2{background:linear-gradient(120deg,var(--ink) 30%,var(--green));-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero p{color:var(--body);font-size:15px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 4px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 18px;min-width:104px;box-shadow:var(--shadow-1);transition:transform .2s ease}
.stat:hover{transform:translateY(-2px)}
.stat b{font-family:var(--serif);font-size:23px;display:block;line-height:1.25}
.stat span{font-size:12px;color:var(--mut)}
/* daily */
.daily{margin:24px 0 6px;background:var(--surface);border:1px solid var(--line2);border-radius:18px;padding:24px 26px;position:relative;overflow:hidden;box-shadow:var(--shadow-1)}
.daily::before{content:"「";position:absolute;top:-14px;left:10px;font-family:var(--serif);font-size:88px;color:var(--green);opacity:.10;pointer-events:none}
.daily .dt{font-size:12.5px;color:var(--mut);letter-spacing:.08em;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.daily .dt .rr{font-size:12px;border:1px solid var(--line2);background:none;color:var(--body);border-radius:20px;padding:3px 12px;cursor:pointer;transition:all .15s ease}
.daily .dt .rr:hover{color:var(--green);border-color:var(--green);transform:translateY(-1px)}
.daily .t{font-family:var(--serif);font-size:21px;font-weight:700;line-height:1.5}
.daily .t a{text-decoration:none}
.daily .t a:hover{color:var(--green)}
.daily .human{color:var(--body);font-size:14.5px;margin-top:9px}
/* progress */
.pwrap{margin:22px 0 4px}
.ptext{display:flex;justify-content:space-between;font-size:13px;color:var(--mut)}
.ptext b{color:var(--ink)}
.progress{height:8px;background:var(--line);border-radius:5px;overflow:hidden;margin-top:7px}
.progress i{display:block;height:100%;background:linear-gradient(90deg,var(--green),#4c9c68);border-radius:5px;transition:width .5s cubic-bezier(.22,1,.36,1)}
.mile{font-size:12.5px;color:var(--green);margin-top:7px;min-height:18px;animation:mileIn .4s ease}
@keyframes mileIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
/* sections */
.sec{margin-top:38px}
.sec>.st{display:flex;align-items:baseline;gap:10px;margin-bottom:14px}
.sec>.st h3{font-family:var(--serif);font-size:20px;font-weight:700}
.sec>.st .hint{font-size:12.5px;color:var(--mut)}
/* presets */
.presets{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.preset{font-size:13.5px;padding:8px 15px;border-radius:24px;border:1px solid var(--line2);background:var(--surface);color:var(--body);cursor:pointer;transition:all .18s ease}
.preset:hover{border-color:var(--green);color:var(--green);transform:translateY(-1px)}
.preset.on{background:var(--green-deep);border-color:var(--green-deep);color:#f3efe6;box-shadow:var(--shadow-1)}
/* filters */
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.filters .f{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--body)}
.filters select{font-size:13px;padding:6px 10px;border:1px solid var(--line2);border-radius:8px;background:var(--surface);color:var(--ink)}
#fKw{font-size:13.5px;padding:7px 12px;border:1px solid var(--line2);border-radius:8px;background:var(--surface);color:var(--ink);width:210px}
.count{font-size:13.5px;color:var(--mut);margin:13px 0 4px}
.count b{color:var(--green)}
/* cards */
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:17px 19px;margin:10px 0;box-shadow:var(--shadow-1);transition:border-color .18s ease,transform .18s ease,box-shadow .18s ease,background .3s ease}
.card:hover{border-color:var(--line2);transform:translateY(-2px);box-shadow:0 2px 4px rgba(28,25,23,.05),0 16px 38px -18px rgba(28,25,23,.32)}
.card.done{background:color-mix(in srgb,var(--green-soft) 60%,var(--surface))}
.card .t{font-weight:650;font-size:16px;line-height:1.5}
.card .t a{text-decoration:none}
.card .t a:hover{color:var(--green)}
.card .human{color:var(--body);font-size:14px;margin-top:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.chips{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.chip{font-size:12px;padding:2.5px 9px;border-radius:20px;background:var(--paper);color:var(--body);border:1px solid var(--line)}
.chip.g{background:var(--green-soft);color:var(--green);border-color:transparent}
.chip.b{background:var(--blue-soft);color:var(--blue);border-color:transparent}
.chip.o{background:var(--amber-soft);color:var(--amber);border-color:transparent}
.chip.m{background:var(--paper);color:var(--mut)}
.chk button{font-size:12.5px;padding:5px 14px;border-radius:8px;border:1px solid var(--line2);background:var(--surface);cursor:pointer;color:var(--body);transition:all .15s ease}
.chk button:hover{border-color:var(--green);color:var(--green);transform:translateY(-1px)}
.chk button.on{background:var(--green);border-color:var(--green);color:#fff;animation:pop .35s cubic-bezier(.34,1.56,.64,1)}
@keyframes pop{0%{transform:scale(1)}45%{transform:scale(1.18)}100%{transform:scale(1)}}
/* chapter grid */
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.ccard{display:flex;gap:12px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:14px 16px;text-decoration:none;box-shadow:var(--shadow-1);transition:border-color .18s ease,transform .18s ease}
.ccard:hover{border-color:var(--green);transform:translateY(-2px)}
.ccard .no{font-family:var(--serif);font-size:20px;font-weight:700;color:var(--green);min-width:32px}
.ccard .ct{font-size:14px;line-height:1.4}
.ccard .cn{font-size:11.5px;color:var(--mut)}
/* entry page */
.crumbs{margin:20px 0 8px;font-size:13px}
.crumbs a{color:var(--mut);text-decoration:none}
.crumbs a:hover{color:var(--green)}
.entry h2{font-family:var(--serif);font-size:27px;line-height:1.4;margin:2px 0 12px}
.evhead{display:flex;gap:16px;align-items:flex-start}
.evbadge{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:var(--serif);font-weight:700;background:var(--paper);border:1px solid var(--line)}
.evbadge .big{font-size:26px;line-height:1.1}
.evbadge .evlbl{font-size:10.5px;letter-spacing:.12em;font-weight:400;opacity:.7}
.evbadge.g{background:linear-gradient(145deg,var(--green-soft),color-mix(in srgb,var(--green-soft) 60%,var(--surface)));color:var(--green);border-color:color-mix(in srgb,var(--green) 30%,transparent)}
.evbadge.b{background:var(--blue-soft);color:var(--blue);border-color:color-mix(in srgb,var(--blue) 30%,transparent)}
.evbadge.o{background:var(--amber-soft);color:var(--amber);border-color:color-mix(in srgb,var(--amber) 30%,transparent)}
.evhead .etitle{flex:1;min-width:0}
.evhead .chk{flex-shrink:0;padding-top:6px}
.block{margin:22px 0}
.block .blab{font-size:12px;letter-spacing:.14em;color:var(--mut);margin-bottom:7px;font-weight:600}
.block .btxt{font-size:15.5px}
.block .btxt.plain{color:var(--body);font-size:14.5px}
.block .btxt a{color:var(--blue);word-break:break-all}
.human-box{background:var(--surface);border:1px solid var(--line2);border-left:4px solid var(--green);border-radius:12px;padding:16px 20px;font-size:16.5px;box-shadow:var(--shadow-1)}
.cites{list-style:none}
.cites li{display:flex;gap:9px;font-size:13.5px;color:var(--body);padding:8px 0;border-bottom:1px dashed var(--line);transition:background .15s ease}
.cites li:hover{background:color-mix(in srgb,var(--green-soft) 30%,transparent)}
.cites li:last-child{border-bottom:none}
.cites .cno{color:var(--mut);font-size:12px;flex-shrink:0;padding-top:2px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.note{font-size:13.5px;color:var(--mut)}
.srcbox{margin-top:28px;border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:var(--surface);box-shadow:var(--shadow-1)}
.srcbox .st{font-size:12px;letter-spacing:.14em;color:var(--mut);margin-bottom:9px;font-weight:600}
.srcbox p{font-size:12.5px;color:var(--body);line-height:1.9}
.srcbox a{color:var(--blue)}
.pn{display:flex;justify-content:space-between;gap:10px;margin-top:28px}
.pn a{flex:1;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:11px 15px;font-size:13px;color:var(--body);text-decoration:none;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;transition:border-color .15s ease,color .15s ease}
.pn a:hover{border-color:var(--green);color:var(--green)}
.pn a:last-child{text-align:right}
/* chapter page */
.chaphead{margin:24px 0 6px;display:flex;gap:18px;align-items:flex-start}
.chaphead .no{font-family:var(--serif);font-size:48px;font-weight:700;color:var(--green);line-height:1}
.chaphead h2{font-family:var(--serif);font-size:25px;margin:2px 0 4px}
.chaphead .meta{font-size:12.5px;color:var(--mut)}
.chapintro{color:var(--body);font-size:14.5px;margin:14px 0 6px}
/* footer */
footer{border-top:1px solid var(--line);padding:28px 0 64px;color:var(--mut);font-size:12.5px;line-height:1.9;background:var(--surface)}
footer .wrap{display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between}
footer .fcol{max-width:420px}
footer a{color:var(--body)}
.lic{display:inline-block;font-size:11.5px;border:1px solid var(--line2);border-radius:6px;padding:1px 9px;color:var(--body);text-decoration:none;margin:0 2px;transition:all .15s ease}
.lic:hover{border-color:var(--green);color:var(--green)}
/* mobile tabbar */
.tabbar{display:none}
@media(max-width:640px){
.hero h2{font-size:26px}
main{padding-bottom:130px}
.top-nav{display:none}
.brand .sub{display:none}
.tabbar{display:flex;position:fixed;bottom:0;left:0;right:0;background:var(--surface);border-top:1px solid var(--line);z-index:10;padding:6px 0 max(6px,env(safe-area-inset-bottom))}
.tabbar a{flex:1;text-align:center;font-size:11px;color:var(--mut);text-decoration:none}
.tabbar a span{display:block;font-size:19px;margin-bottom:1px}
}
/* 动效：滚动渐显 + 打勾完成态 */
.reveal{opacity:0;transform:translateY(16px);transition:opacity .55s ease,transform .55s cubic-bezier(.22,1,.36,1)}
.reveal.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){
.reveal{opacity:1;transform:none;transition:none}
.card,.ccard,.preset,.chk button,.stat{transition:none;animation:none}
}
.empty{ text-align:center;color:var(--mut);padding:16px;font-size:13.5px}
"""


def entry_href(eid: str) -> str:
    return f"/e/{quote(eid)}.html"


HEADER = """<header><div class="wrap">
<a class="brand" href="/"><span class="mark">懒</span>
<span><span class="name">{t}</span><br><span class="sub">{s}</span></span></a>
<nav class="top-nav"><a href="/#filter">筛选</a><a href="/#chapters">章节</a><a href="/s/export.html">备份</a></nav>
</div></header>"""

TABBAR = """<nav class="tabbar">
<a href="/"><span>🏠</span>首页</a>
<a href="/#filter"><span>🎯</span>筛选</a>
<a href="/#daily"><span>📅</span>每日</a>
<a href="/#chapters"><span>📚</span>章节</a>
</nav>"""

FOOTER = """<footer><div class="wrap">
<div class="fcol">
<p><b>关于内容</b>　本站是《高性价比人生指南》的衍生筛选工具，全部条目正文来自
<a href="{up}" target="_blank" rel="noopener">github.com/eternity4719/HowToLiveBetter</a>
<a class="lic" href="{up}" target="_blank" rel="noopener">上游仓库</a><a class="lic" href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a></p>
<p>内容可能过时，以原仓库为准。真去办事、看病、打官司，以当地部门、医生和律师的说法为准。</p>
</div>
<div class="fcol">
<p><b>关于进度</b>　打勾只存在你自己的浏览器（localStorage），不注册、不上传。换设备用
<a href="/s/export.html">备份 / 恢复</a> 带走。</p>
<p>© 2026 {t} · 一个用 AI 写的衍生站</p>
</div>
</div></footer>"""


def head_html(title: str, desc: str, canonical: str) -> str:
    return (f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f"<title>{esc(title)}</title>\n"
            f'<meta name="description" content="{esc(desc)}">\n'
            f'<link rel="canonical" href="{BASE_URL}{canonical}">\n'
            f'<link rel="stylesheet" href="/s/style.css"></head><body>')


def card_html(e: dict) -> str:
    chips = " ".join(tag_chip(k, v) for k, v in e["tags"].items()) + " " + level_chip(e["level"])
    btn = f'<span class="chk"><button data-ck="{e["id"]}" onclick="toggleDone(\'{e["id"]}\',this)">打勾</button></span>'
    return (f'<div class="card reveal" data-eid="{e["id"]}">{btn}'
            f'<div class="t"><a href="{entry_href(e["id"])}">{esc(e["title"])}</a></div>'
            f'<div class="human">{esc(e["fields"].get("说人话", ""))}</div>'
            f'<div class="chips">{chips}</div></div>')


def build():
    chapters = parse_book()
    flat = [e for c in chapters for e in c["entries"]]
    total = len(flat)
    levels = {"A": 0, "B": 0, "C": 0}
    zero_free = 0
    for e in flat:
        levels[e["level"]] = levels.get(e["level"], 0) + 1
        if e["tags"].get("钱") == "0":
            zero_free += 1
    print(f"解析：{len(chapters)} 章，{total} 条；A/B/C = "
          f"{levels.get('A',0)}/{levels.get('B',0)}/{levels.get('C',0)}；0 元 {zero_free}")

    if DIST.exists():
        shutil.rmtree(DIST)
    for d in ("e", "c", "s"):
        (DIST / d).mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "app.js", DIST / "s" / "app.js")

    today_seed = date.today().isoformat()
    daily = flat[(sum(ord(ch) for ch in today_seed) + int(today_seed.replace("-", ""))) % total]

    search = [{"id": e["id"], "t": e["title"], "h": e["fields"].get("说人话", "")[:90],
               "c": c["num"], "lv": e["level"], "tags": e["tags"]}
              for c in chapters for e in c["entries"]]
    (DIST / "s" / "search.json").write_text(
        json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf8")

    head = HEADER.format(t=SITE_TITLE, s=SITE_SUB)
    foot = FOOTER.format(up=UPSTREAM, t=SITE_TITLE)

    presets = [
        ("🎯 懒人开工包", "0", "否", "大", "A"),
        ("💰 钱包保卫", "0", "", "大", "AB"),
        ("⏰ 时间翻身", "", "些", "大", "AB"),
        ("🧠 健康保命", "", "", "大", "A"),
        ("📚 只要硬证据", "", "", "", "A"),
    ]
    preset_html = "".join(
        f'<button class="preset" data-p="{q}|{y}|{s}|{l}">{name}</button>'
        for name, q, y, s, l in presets)
    cgrid = "".join(
        f'<a class="ccard reveal" href="/c/{c["nn"]}.html"><span class="no">{c["num"]:02d}</span>'
        f'<span><span class="ct">{esc(c["title"])}</span><br><span class="cn">{len(c["entries"])} 条建议</span></span></a>'
        for c in chapters)
    daily_card = card_html(daily).replace('class="card reveal"', 'class="card daily" id="dailyCard"', 1)
    home = (head_html(f"{SITE_TITLE} · 高性价比人生指南衍生站",
                      f"从 {total} 条有证据等级的人生建议里，筛出 0 元、不费毅力、收益大、证据硬的那几条。打勾记进度，不用注册。", "/")
            + head
            + f"""<main><div class="wrap">
<section class="hero reveal">
<div class="kick">HOW TO LIVE BETTER · 衍生站</div>
<h2>别整本读完，<br>先做最划算的那几件。</h2>
<p>全书 {total} 条建议都标了成本、毅力和证据等级。这里把它们拆开，让你按「懒人性价比」挑着做。</p>
<div class="stats">
<div class="stat"><b data-count="{total}">0</b><span>条建议</span></div>
<div class="stat"><b data-count="{levels.get("A",0)}">0</b><span>证据 A 级</span></div>
<div class="stat"><b data-count="{zero_free}">0</b><span>0 元可做</span></div>
<div class="stat"><b id="doneCount">0</b><span>你已打勾</span></div>
</div></section>
<section class="sec reveal" id="daily">
<div class="st"><h3>今天的一条</h3><span class="hint">每天零点换，碰到对味的就打勾</span></div>
{daily_card}
</section>
<div class="pwrap reveal">
<div class="ptext"><span>我的进度</span><span><b id="doneCount2">0</b> / {total}</span></div>
<div class="progress"><i id="doneBar" style="width:0"></i></div>
<div class="mile" id="milestone"></div>
</div>
<section class="sec reveal" id="filter">
<div class="st"><h3>按性价比筛</h3><span class="hint">点套餐一键开筛，或自己组合</span></div>
<div class="presets">{preset_html}</div>
<div class="filters">
<span class="f">花钱 <select id="fQian"><option value="">不限</option><option value="0">0 元</option><option value="少">少</option></select></span>
<span class="f">毅力 <select id="fYili"><option value="">不限</option><option value="否">不费</option><option value="些">一点点</option></select></span>
<span class="f">收益 <select id="fShouyi"><option value="">不限</option><option value="大">大</option><option value="中">中</option></select></span>
<span class="f">证据 <select id="fLv"><option value="">不限</option><option value="A">只要 A</option><option value="AB">A 或 B</option></select></span>
<input id="fKw" type="search" placeholder="搜标题或一句话版本…">
</div>
<div class="count" id="filterCount">点上面的套餐一键开筛，或自己组合条件</div>
<div id="filterList"></div>
</section>
<section class="sec" id="chapters">
<div class="st"><h3>全部 34 章</h3><span class="hint">按主题逛</span></div>
<div class="cgrid">{cgrid}</div>
</section>
</div></main>
""" + foot + TABBAR
            + f'<script>window.__TOTAL__={total};</script>'
            + '<script src="/s/app.js" defer></script></body></html>')
    (DIST / "index.html").write_text(home, encoding="utf8")
    (DIST / "s" / "style.css").write_text(CSS, encoding="utf8")

    # ---------------- 条目页（打勾按钮放进 evhead flex，不再 float） ----------------
    def entry_page(c: dict, e: dict, prev_e, next_e) -> str:
        desc = e["fields"].get("说人话", e["title"])[:150]
        f = e["fields"]
        lv_color = {"A": "g", "B": "b", "C": "o"}.get(e["level"], "m")
        chips = " ".join(tag_chip(k, v) for k, v in e["tags"].items())
        blocks = []
        if "成本" in f:
            blocks.append(f'<div class="block reveal"><div class="blab">💰 成本</div><div class="btxt plain">{linkify(f["成本"])}</div></div>')
        if "说人话" in f:
            blocks.append(f'<div class="block reveal"><div class="blab">💡 说人话</div><div class="human-box">{linkify(f["说人话"])}</div></div>')
        if "收益" in f:
            blocks.append(f'<div class="block reveal"><div class="blab">📈 收益与证据</div><div class="btxt plain">{linkify(f["收益"])}</div></div>')
        if "来源" in f:
            n = len([x for x in re.split("；|;", f["来源"]) if x.strip()])
            blocks.append(f'<div class="block reveal"><div class="blab">📚 来源（{n} 条文献）</div>{source_list(f["来源"])}</div>')
        for ln in e["extra"]:
            blocks.append(f'<div class="block reveal"><div class="btxt plain">{linkify(ln)}</div></div>')
        if "备注" in f:
            blocks.append(f'<div class="block reveal"><div class="blab">📝 备注</div><div class="btxt note">{linkify(f["备注"])}</div></div>')
        nav = ""
        if prev_e:
            nav += f'<a href="{entry_href(prev_e["id"])}">← {esc(prev_e["title"][:18])}</a>'
        if next_e:
            nav += f'<a href="{entry_href(next_e["id"])}">{esc(next_e["title"][:18])} →</a>'
        return (head_html(f"{e['title']} · 第{c['num']}节 · {SITE_TITLE}", desc, entry_href(e["id"]))
                + head
                + f"""<main><div class="wrap entry">
<div class="crumbs"><a href="/c/{c["nn"]}.html">第 {c["num"]:02d} 节 · {esc(c["title"])}</a> / 条目 {c["num"]}.{e["num"]}</div>
<div class="evhead">
<div class="evbadge {lv_color}"><div><div class="big">{esc(e["level"] or "—")}</div><div class="evlbl">证据等级</div></div></div>
<div class="etitle"><h2>{esc(e["title"])}</h2><div class="chips">{chips or level_chip(e["level"])}</div></div>
<span class="chk"><button data-ck="{e["id"]}" onclick="toggleDone('{e["id"]}',this)">打勾</button></span>
</div>
{"".join(blocks)}
<div class="pn reveal">{nav}</div>
<div class="srcbox reveal"><div class="st">来源与许可</div>
<p>本条整理自 <a href="{REPO_FILE}/{quote(c['nn'] + '-' + c['title'])}.md" target="_blank" rel="noopener">上游仓库 · 第{c["num"]}节第{e["num"]}条</a>
<a class="lic" href="{UPSTREAM}" target="_blank" rel="noopener">GitHub 原仓库</a><a class="lic" href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>，内容以原文为准。</p>
</div>
</div></main>""" + foot + TABBAR
                + f'<script>window.__TOTAL__={total};</script><script src="/s/app.js" defer></script></body></html>')

    for c in chapters:
        es = c["entries"]
        for i, e in enumerate(es):
            (DIST / "e" / f"{e['id']}.html").write_text(
                entry_page(c, e, es[i - 1] if i else None, es[i + 1] if i < len(es) - 1 else None),
                encoding="utf8")
        cards = "".join(card_html(e) for e in es)
        intro = f'<p class="chapintro">{esc(c["intro"][:200])}…</p>' if c["intro"] else ""
        (DIST / "c" / f"{c['nn']}.html").write_text(
            head_html(f"{c['num']:02d} {c['title']} · {SITE_TITLE}",
                      f"{c['title']}：{len(es)} 条有证据等级的行动建议，来自高性价比人生指南。", f"/c/{c['nn']}.html")
            + head
            + f"""<main><div class="wrap">
<div class="chaphead reveal"><div class="no">{c["num"]:02d}</div>
<div><h2>{esc(c["title"])}</h2><div class="meta">{len(es)} 条建议 · 证据 A {sum(1 for e in es if e["level"]=="A")} 条</div></div></div>
{intro}{cards}
</div></main>""" + foot + TABBAR
            + f'<script>window.__TOTAL__={total};</script><script src="/s/app.js" defer></script></body></html>',
            encoding="utf8")

    # ---------------- 备份页 ----------------
    (DIST / "s" / "export.html").write_text(
        head_html(f"备份 / 恢复进度 · {SITE_TITLE}", "导出或恢复你的打勾进度。", "/s/export.html")
        + head
        + """<main><div class="wrap entry"><h2 style="font-family:var(--serif);margin-top:20px">备份 / 恢复打勾进度</h2>
<p style="color:var(--body)">进度只存在本机浏览器。换设备时导出一份 JSON 文件带走，在新设备上导入即可。</p>
<p style="margin:16px 0"><button onclick="exportDone()" style="padding:11px 18px;border:none;border-radius:10px;background:var(--green);color:#fff;font-size:14px;cursor:pointer">⬇ 导出进度文件</button>
<span style="margin-left:12px;font-size:13px">或导入：<input type="file" id="imp" accept=".json" onchange="importDone(this)"></span></p>
<p id="msg" style="color:var(--green);font-size:14px"></p></div></main>"""
        + foot + '<script src="/s/app.js" defer></script>'
        + """<script>
function exportDone(){const d=localStorage.getItem("htlb_done")||"{}";const b=new Blob([d],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="htlb_progress.json";a.click();}
function importDone(input){const f=input.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{try{const o=JSON.parse(r.result);localStorage.setItem("htlb_done",r.result);document.getElementById("msg").textContent="已恢复 "+Object.keys(o).length+" 条，回首页即可看到";document.dispatchEvent(new Event("DOMContentLoaded"));}catch(e){alert("文件格式不对");}};r.readAsText(f);}
</script></body></html>""", encoding="utf8")

    # ---------------- sitemap / robots / netlify ----------------
    urls = ["/"] + [f"/c/{c['nn']}.html" for c in chapters] + [entry_href(e["id"]) for e in flat]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{BASE_URL}{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm), encoding="utf8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf8")
    (DIST / "_redirects").write_text(
        "# Netlify Pretty URLs 会改写带大写/后缀的路径，平台验证文件必须加 200! 规则\n"
        "# /baidu_verify_xxx.html /baidu_verify_xxx.html 200!\n", encoding="utf8")
    (DIST / "netlify.toml").write_text(
        '[build]\n  command = "python3 build.py"\n  publish = "dist"\n', encoding="utf8")
    print(f"生成完成：{len(urls)} 个页面 → dist/")


if __name__ == "__main__":
    build()
