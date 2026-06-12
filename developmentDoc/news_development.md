# News Development Document

本文档用于记录 AI Intelligence Agent 第四个功能：AI 行业新闻获取、筛选与总结。

当前 MVP 已经完成论文和 GitHub 项目的获取、筛选、结构化总结与每日报告生成。News 功能属于下一阶段扩展，目标是让日报不仅覆盖研究论文和开源项目，也能覆盖 AI 公司、产品、模型发布、工具更新和重要行业动态。

---

## 1. 功能目标

本功能需要完成：

```text
输入：新闻源配置或固定 RSS / API / 网页来源
处理：获取 AI 相关新闻，筛选重要新闻，并生成结构化中英文总结
输出：report_agent.py 可直接使用的 news_summaries
```

新闻获取输出示例：

```python
[
    {
        "title": "News title",
        "source": "OpenAI Blog",
        "summary": "Raw description or excerpt.",
        "published_date": "2026-06-11",
        "url": "https://example.com/news",
        "source_type": "rss"
    }
]
```

News Agent 输出示例：

```python
[
    {
        "title": "News title",
        "source": "OpenAI Blog",
        "one_sentence_summary": "One sentence English summary.",
        "chinese_summary": "中文摘要。",
        "what_happened": "What happened.",
        "chinese_what_happened": "发生了什么。",
        "why_it_matters": "Why it matters.",
        "chinese_why_it_matters": "为什么重要。",
        "impact": "Impact on developers, researchers, or AI users.",
        "chinese_impact": "对开发者、研究人员或 AI 用户的影响。",
        "related_technologies": "Related technologies.",
        "chinese_related_technologies": "相关技术。",
        "url": "https://example.com/news"
    }
]
```

---

## 2. 本阶段不做什么

为了控制复杂度，本阶段暂时不做：

```text
1. 不做全网新闻爬虫
2. 不绕过网站反爬或付费墙
3. 不抓取完整网页正文作为主要数据源
4. 不做社交媒体追踪
5. 不保存历史数据库
6. 不做复杂趋势分析
7. 不做真假新闻自动判定
8. 不做邮件、Notion 或前端推送
```

当前目标是先让可信新闻源稳定进入日报，而不是做完整新闻搜索引擎。

---

## 3. 涉及文件

主要实现文件：

```text
tools/news_tool.py
agents/news_agent.py
```

可能需要调整的文件：

```text
config.py
main.py
agents/report_agent.py
prompts/news_selection_prompt.txt
prompts/news_summary_prompt.txt
tests/test_news_tool.py
tests/test_news_agent.py
README.md
```

本阶段优先改：

```text
1. tools/news_tool.py
2. agents/news_agent.py
3. prompts/news_selection_prompt.txt
4. prompts/news_summary_prompt.txt
5. tests/test_news_tool.py
6. tests/test_news_agent.py
7. config.py
8. main.py
```

---

## 4. 推荐技术方案

### 4.1 第一版优先使用 RSS

推荐第一版使用 RSS / Atom feed。

原因：

```text
1. requirements.txt 中已经包含 feedparser
2. RSS 格式相对稳定
3. 可以避免复杂网页解析和反爬问题
4. 每条新闻通常自带 title、summary、published、link
5. 适合 MVP 之后的轻量扩展
```

推荐新闻源先从少量高信号来源开始：

```text
1. OpenAI Blog
2. Anthropic News
3. Google DeepMind Blog
4. Microsoft AI Blog
5. NVIDIA Blog
6. Hugging Face Blog
```

注意：

```text
新闻源 URL 可能变化，实现时需要把 feed URL 放在 config.py，方便后续维护。
```

### 4.2 OpenAI API

新闻筛选和总结继续使用 OpenAI Python SDK。

原因：

```text
1. 当前 paper_agent.py 和 github_agent.py 已经使用 OpenAI
2. 可以保持结构化 JSON 输出方式一致
3. 中文字段生成方式可以复用前面的经验
4. 有 OPENAI_API_KEY 时生成真正总结，没有 key 时 fallback
```

`.env` 示例：

```text
OPENAI_API_KEY=your_openai_api_key
OPENAI_NEWS_SELECTION_MODEL=gpt-4o-mini
OPENAI_NEWS_SUMMARY_MODEL=gpt-4o-mini
```

---

## 5. 开发流程

### Step 1: 在 config.py 中配置新闻源

建议新增：

```python
NEWS_MAX_RESULTS = 10
OPENAI_NEWS_SELECTION_MODEL = "gpt-4o-mini"
OPENAI_NEWS_SUMMARY_MODEL = "gpt-4o-mini"

NEWS_FEEDS = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "source_type": "rss",
    },
]
```

注意：

```text
1. NEWS_FEEDS 先保持少量可靠来源
2. 每个 feed 至少包含 name、url、source_type
3. 如果某个 feed 失败，不影响其他 feed
```

### Step 2: 实现新闻获取工具

函数：

```python
def collect_ai_news(
    max_results: int = 10,
    feeds: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    ...
```

作用：

```text
从配置的新闻源中获取 AI 相关新闻，并返回结构化 list[dict]。
```

行为要求：

```text
1. max_results <= 0 时返回 []
2. feeds 为空时使用 config.NEWS_FEEDS
3. 单个 feed 失败时跳过该 feed
4. 单条新闻解析失败时跳过该条
5. 不把 feedparser 原始对象泄漏给 agent
```

字段映射：

```text
entry.title -> title
entry.summary 或 entry.description -> summary
entry.link -> url
entry.published 或 entry.updated -> published_date
feed.name -> source
feed.source_type -> source_type
```

### Step 3: 实现新闻筛选

函数：

```python
def select_important_news(
    news_items: list[dict[str, Any]],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    ...
```

第一版策略：

```text
1. 有 OPENAI_API_KEY 时优先使用 LLM 筛选
2. 没有 key 或 LLM 失败时使用本地关键词打分
3. 本地打分依据 title、summary、source
4. 如果没有关键词命中，保持原始顺序返回前 top_k
```

本地关键词建议：

```text
LLM
agent
RAG
multimodal
reasoning
model release
API
developer
benchmark
open source
research
安全
产品发布
```

### Step 4: 实现新闻总结

函数：

```python
def summarize_news_item(news_item: dict[str, Any]) -> dict[str, Any]:
    ...
```

输出字段：

```text
title
source
one_sentence_summary
chinese_summary
what_happened
chinese_what_happened
why_it_matters
chinese_why_it_matters
impact
chinese_impact
related_technologies
chinese_related_technologies
url
```

中文字段要求：

```text
1. 正文语句使用自然简体中文
2. 公司名、产品名、模型名、API 名称和技术术语按习惯保留英文
3. 不要机械翻译 OpenAI、Claude、Gemini、Hugging Face、CUDA、Transformer 等专有名词
```

### Step 5: Prompt 文件化

新增 prompt 文件：

```text
prompts/news_selection_prompt.txt
prompts/news_summary_prompt.txt
```

要求：

```text
1. prompt 文件用于调节筛选和总结风格
2. Python 代码中保留 fallback prompt
3. prompt 文件读取失败时不影响主流程
4. JSON 示例中的大括号需要转义，避免 str.format() 报错
```

### Step 6: 接入 report_agent.py 和 main.py

当前 `report_agent.py` 已经支持：

```python
build_daily_report(
    paper_summaries=paper_summaries,
    repo_summaries=repo_summaries,
    news_summaries=news_summaries,
)
```

需要调整 `main.py`：

```python
news_items = collect_ai_news(max_results=NEWS_MAX_RESULTS)
selected_news = select_important_news(news_items, top_k=SELECTION_TOP_K)
news_summaries = [summarize_news_item(item) for item in selected_news]

report = build_daily_report(
    paper_summaries=paper_summaries,
    repo_summaries=repo_summaries,
    news_summaries=news_summaries,
)
```

注意：

```text
如果新闻源失败，news_summaries 可以是 []，报告中显示暂无入选行业新闻。
```

---

## 6. 异常处理

需要处理：

```text
1. feedparser 导入失败
2. RSS feed 请求失败或解析失败
3. feed entry 缺少 title、summary、link
4. published 日期格式不稳定
5. 单条新闻解析失败
6. OpenAI 调用失败
7. JSON 解析失败
8. prompt 文件缺失或格式化失败
```

处理策略：

```text
1. 打印清晰错误信息
2. 单个 feed 或单条新闻失败时跳过
3. LLM 失败时 fallback
4. 不让新闻模块阻塞论文和 GitHub 报告
5. 单元测试不真实请求 RSS 或 OpenAI
```

---

## 7. 测试计划

测试文件：

```text
tests/test_news_tool.py
tests/test_news_agent.py
tests/test_report_agent.py
```

测试点：

```text
1. max_results <= 0 返回 []
2. feeds 为空或全部失败时返回 []
3. feed entry 可以解析为标准 dict
4. title、summary、url 字段清理多余空白
5. select_important_news() 空输入返回 []
6. 没有 OPENAI_API_KEY 时使用本地关键词筛选
7. 有 OPENAI_API_KEY 时可以使用 LLM 筛选
8. summarize_news_item() 输出中英文字段
9. OpenAI 返回部分字段时自动补 fallback
10. report_agent.py 可以展示英文和中文新闻区
```

验收命令：

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q .
```

---

## 8. 验收标准

本阶段完成后应该满足：

```text
1. collect_ai_news(max_results=10) 返回 list
2. 每条 news 至少包含 title、source、summary、published_date、url、source_type
3. select_important_news() 可以返回 top_k 条重要新闻
4. summarize_news_item() 输出 report_agent.py 所需字段
5. main.py 可以生成包含论文、GitHub 项目、行业新闻的报告
6. 没有 OPENAI_API_KEY 时主流程仍可运行
7. 有 OPENAI_API_KEY 时新闻总结不应大面积出现 TBD
8. 中文新闻区应翻译正文语句，但保留公司名、产品名、模型名和技术术语
9. 单元测试和 compileall 通过
```

真实验收：

```bash
.venv/bin/python main.py
```

生成报告中应包含：

```text
## 3. Industry News
## 3. 行业新闻
```

---

## 9. 当前限制

```text
1. RSS feed 覆盖范围有限，可能漏掉部分重要新闻
2. 不读取完整网页正文，summary 可能信息不足
3. 不做历史去重，可能重复推荐同一新闻
4. 不做事实核查，只基于可信来源和 LLM 总结
5. 新闻源 URL 可能变动，需要维护
6. 没有时间窗口过滤时，旧新闻可能混入报告
```

---

## 10. 建议实现顺序

推荐下一步按这个顺序实现：

```text
1. 先实现 tools/news_tool.py 的 RSS 获取和离线测试
2. 再实现 agents/news_agent.py 的本地筛选和 fallback 总结
3. 接入 OpenAI JSON 筛选和总结
4. 新增 prompts/news_selection_prompt.txt 和 prompts/news_summary_prompt.txt
5. 接入 main.py 和 report_agent.py
6. 跑一次真实 main.py，检查报告中新闻区质量
7. 根据真实输出微调 prompt 和新闻源列表
```

---

## 11. 后续增强方向

News 第一版稳定后，可以继续做：

```text
1. 增加历史去重，避免重复新闻
2. 增加时间窗口过滤，例如只看最近 24-72 小时
3. 增加来源权重，例如官方博客优先
4. 读取网页正文摘要，提高总结质量
5. 增加来源分类：公司动态、模型发布、开发者工具、研究进展、政策安全
6. 把新闻和论文 / GitHub 项目关联，例如同一模型发布对应 paper 和 repo
```

---

## 12. 本次实现结果

本次已经完成 News 第一版实现。

已完成：

```text
1. config.py 新增 NEWS_MAX_RESULTS、NEWS_FEEDS、OpenAI News 模型配置
2. tools/news_tool.py 实现 RSS / Atom feed 获取
3. tools/news_tool.py 实现 feed entry 标准化和 HTML summary 清理
4. agents/news_agent.py 实现新闻筛选、本地关键词 fallback、OpenAI JSON 筛选
5. agents/news_agent.py 实现中英文结构化新闻总结
6. prompts/news_selection_prompt.txt 和 prompts/news_summary_prompt.txt 已新增
7. main.py 已接入 collect_ai_news、select_important_news、summarize_news_item
8. report_agent.py 已展示英文和中文新闻区
9. 新增 tests/test_news_tool.py 和 tests/test_news_agent.py
10. 扩展 tests/test_report_agent.py 验证新闻区输出
```

已通过验收命令：

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q .
```

当前仍需真实验证：

```text
1. 运行 .venv/bin/python main.py
2. 检查报告中是否出现 ## 3. Industry News 和 ## 3. 行业新闻
3. 检查 RSS 源是否仍然可用
4. 根据真实新闻质量调整 NEWS_FEEDS 和 prompts/news_summary_prompt.txt
```
