# 部署与运营手册 —— 懒人性价比清单（HowToLiveBetter 衍生站）

> 目标子域名（建议）：`qingdan.lazyso.com`（也可 `life.lazyso.com` / `howto.lazyso.com`，改 `build.py` 里 `BASE_URL` 重新构建即可）
> 上游内容：github.com/eternity4719/HowToLiveBetter（CC BY 4.0），本站已完整署名

## 一、这是什么

从 677 条有证据等级的人生建议里，按 **0 元 × 不费毅力 × 收益大 × 证据硬** 组合筛选的清单站。
差异化位子：衍生生态里已有打勾清单/地图版/阶段版/阅读站，但「性价比筛选器」没人做——而这个标签数据书里每条自带，成本几乎为零。

核心数字（构建自 content/book）：34 章 · 677 条 · 证据 A 级 438 · 0 元条目 531。
杀手筛选组合「0元+不费毅力+收益大+证据A」= 92 条，天然是"懒人开工包"。

## 二、本地文件

```
htlb-lazy/
├── build.py            # 生成器：content/book/*.md → dist/（712 个静态页）
├── assets/app.js       # 前端交互（筛选/打勾/进度，零依赖）
├── content/book/       # 上游正文快照（更新：git pull 上游后覆盖重跑）
└── dist/               # 构建产物，整目录上传即可，任何静态托管都能跑
```

重新构建：`python3 build.py`
本地预览：`cd dist && python3 -m http.server 8737`

## 三、部署步骤（沿用 clean/ai.lazyso.com 的既有套路，半小时）

1. **建独立 GitHub 仓库**（如 `lazyvip/lazy-checklist`），推本项目（含 netlify.toml，Netlify 会自动执行 `python3 build.py` 并发布 `dist/`）
2. **Netlify 添加站点** → 绑定子域名 `qingdan.lazyso.com`
3. **⚠️ 国内 DNS 污染问题**（来自 lazyso HANDOFF 教训）：Netlify 边缘节点在国内常被污染（clean.lazyso.com 即中招）。解决：在 Cloudflare 给 lazyso.com 加一条**代理模式（橙色云）CNAME** 指向该 Netlify 站点，走 Cloudflare IP 国内可直连；对外主推走 Cloudflare 别名
4. **验证文件坑**：任何搜索引擎验证文件必须在 `_redirects` 里加 `200!` 规则（Netlify Pretty URLs 会静默改写路径导致验证失效），`_redirects` 占位已生成
5. 验证：首页 / 条目页 / sitemap.xml / 验证文件 全部 200

## 四、SEO（必应为主，参考复盘文档的数据：必应 1623 vs Google 45）

1. 注册 [Bing 站长工具](https://www.bing.com/webmasters)，提交 `sitemap.xml`
2. 用 URL 提交接口先推首页 + 34 个章节页（内容聚合页权重高）
3. 条目页 677 个有独立 title/description/canonical（已生成），等必应自然抓取
4. 目标关键词：人生清单、省钱清单、性价比人生、个人风险清单、人生体检——常青词，不依赖热度

## 五、向上游占位（复制粘贴即用）

上游 `衍生项目.md` 收录规则：**直接提 PR 改该文件，链接能打开+写明出处许可就会合并**。

在「## 网站」分组末尾加一行：

```markdown
[懒人性价比清单](https://qingdan.lazyso.com/)，[lazyvip](https://github.com/lazyvip) 做的筛选站：按「0 元、不费毅力、收益大、证据 A」组合筛选 677 条建议，打勾记进度、每日一条；不用注册、没有广告
```

PR 流程：fork 上游仓库 → 编辑 `衍生项目.md` 加上面这行 → PR 标题「新增衍生项目：懒人性价比清单」。
README 入口是长期流量（复盘数据：收录后每天 100-200 次稳定访问）。

## 六、内容更新 SOP（上游新书发布时）

```
cd /tmp && git clone --depth 1 https://github.com/eternity4719/HowToLiveBetter htlb
cp -r htlb/book  <本项目>/content/book
python3 build.py   # 条目数变化会自动反映到首页统计
```
每月跑一次即可；上游发 release（PDF/EPUB 更新）时通常正文也有更新。

## 七、后续模板化（一子域名一赛道）

本站即「清单/筛选型」模板 v1。换赛道时的替换点：
- `content/` 换成新仓库的结构化内容
- `build.py` 顶部站点名/描述/筛选维度（标签体系要对齐新仓库）
- 每个站固定四件套：首页+筛选、条目 SEO 页、sitemap、上游署名

下一个赛道候选标准：协议宽松（CC-BY/MIT）+ 内容结构化 + 星标 7 日增量陡峭 + 中文可用。
