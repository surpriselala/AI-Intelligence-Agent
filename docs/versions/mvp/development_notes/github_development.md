# GitHub Development Document

本文档用于记录 AI Intelligence Agent 第三个功能：GitHub 开源项目获取、筛选与总结。

前两个功能已经完成了 arXiv 论文获取和论文结构化总结。本阶段目标是补齐 MVP 中的第二个主要信息源，让 `main.py` 可以真实获取 AI 相关 GitHub 仓库，并由 `github_agent.py` 生成 `report_agent.py` 可直接使用的结构化项目总结。

---

## 1. 功能目标

本功能需要完成：

```text
输入：关键词 query，例如 "AI agent" 或 "large language model"
处理：调用 GitHub Search API 获取相关仓库，筛选重要项目，并生成结构化总结
输出：report_agent.py 可直接使用的 repo_summaries
```

GitHub 获取输出示例：

```python
[
    {
        "name": "owner/repo",
        "description": "Repository description",
        "stars": 1200,
        "language": "Python",
        "url": "https://github.com/owner/repo",
        "created_at": "2026-06-07T00:00:00Z",
        "updated_at": "2026-06-08T00:00:00Z"
    }
]
```

GitHub Agent 输出示例：

```python
[
    {
        "name": "owner/repo",
        "one_sentence_summary": "One sentence summary.",
        "chinese_summary": "中文摘要。",
        "main_features": "Main project features.",
        "technical_highlights": "Technical highlights.",
        "learning_value": "Learning value.",
        "recommended_for": "Who should read or use it.",
        "possible_use_cases": "Possible use cases.",
        "stars": 1200,
        "url": "https://github.com/owner/repo"
    }
]
```

---

## 2. 本阶段不做什么

为了保持 MVP 简单，本阶段暂时不做：

```text
1. 不 clone 仓库
2. 不读取 README 全文
3. 不分析源码质量
4. 不保存仓库历史记录
5. 不做复杂 trending 计算
6. 不做 star 增长趋势分析
7. 不接数据库或向量数据库
```

当前目标是先让 GitHub 项目数据真实进入每日报告，而不是追求项目分析质量一步到位。

---

## 3. 涉及文件

主要实现文件：

```text
tools/github_tool.py
agents/github_agent.py
```

可能需要调整的文件：

```text
config.py
prompts/github_selection_prompt.txt
prompts/github_summary_prompt.txt
tests/test_github_tool.py
tests/test_github_agent.py
main.py
agents/report_agent.py
```

本阶段优先改：

```text
1. tools/github_tool.py
2. agents/github_agent.py
3. tests/test_github_tool.py
4. tests/test_github_agent.py
5. config.py
```

---

## 4. 推荐技术方案

### 4.1 GitHub Search API

推荐使用 GitHub REST Search API：

```text
GET https://api.github.com/search/repositories
```

请求参数：

```text
q: 搜索关键词
sort: stars
order: desc
per_page: max_results
```

原因：

```text
1. requirements.txt 中已经包含 requests
2. 不需要额外 SDK
3. 返回字段足够支撑 MVP 报告
4. 可选使用 GITHUB_TOKEN 提高 rate limit
```

`.env` 示例：

```text
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_GITHUB_SELECTION_MODEL=gpt-4o-mini
OPENAI_GITHUB_SUMMARY_MODEL=gpt-4o-mini
```

注意：

```text
.env 不应该提交到 Git。
```

---

## 5. 开发流程

### Step 1: 实现 GitHub 获取工具

函数：

```python
def search_github_repositories(
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    ...
```

作用：

```text
根据关键词搜索 GitHub 仓库，并返回结构化 list[dict]。
```

行为要求：

```text
1. query 为空或 max_results <= 0 时返回 []
2. 请求失败时返回 []
3. 单条仓库解析失败时跳过该条
4. 不把 requests 的原始 Response 或 GitHub 原始 item 泄漏给外部模块
```

字段映射：

```text
full_name -> name
description -> description
stargazers_count -> stars
language -> language
html_url -> url
created_at -> created_at
updated_at -> updated_at
```

### Step 2: 实现本地仓库筛选

函数：

```python
def select_important_repositories(
    repos: list[dict[str, Any]],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    ...
```

第一版策略：

```text
1. 如果没有 OPENAI_API_KEY，使用本地打分
2. AI 关键词命中加分
3. star 数越高越靠前
4. 如果没有关键词命中，按 stars 保持稳定排序
```

后续升级：

```text
使用 LLM 根据相关性、实用价值、学习价值和项目质量排序。
```

### Step 3: 实现单个仓库总结

函数：

```python
def summarize_repository(repo: dict[str, Any]) -> dict[str, Any]:
    ...
```

作用：

```text
把 GitHub 仓库 dict 转换成 report_agent.py 可以展示的结构化 summary dict。
```

输出字段：

```text
name
one_sentence_summary
chinese_summary
main_features
technical_highlights
learning_value
recommended_for
possible_use_cases
stars
url
```

### Step 4: OpenAI 调用设计

有 `OPENAI_API_KEY` 时：

```text
1. select_important_repositories() 优先尝试 LLM 筛选
2. summarize_repository() 优先尝试 LLM 结构化总结
3. OpenAI 调用失败时自动 fallback 到本地逻辑
```

OpenAI JSON 返回格式：

```json
{
    "selected_indices": [0, 1, 2]
}
```

总结 JSON 返回字段：

```text
one_sentence_summary
chinese_summary
main_features
technical_highlights
learning_value
recommended_for
possible_use_cases
```

---

## 6. 异常处理

需要处理：

```text
1. requests 导入失败
2. GitHub API 请求失败
3. GitHub API 返回非 200 状态码
4. GitHub API 返回结构异常
5. 单条仓库字段缺失
6. OpenAI rate limit 或 JSON 解析失败
7. 没有 GITHUB_TOKEN 或 OPENAI_API_KEY
```

处理策略：

```text
1. 打印清晰错误信息
2. 返回 [] 或 fallback summary
3. 不让 main.py 因单个模块失败而中断
4. 单元测试不真实请求 GitHub 或 OpenAI
```

---

## 7. 测试计划

测试文件：

```text
tests/test_github_tool.py
tests/test_github_agent.py
```

测试点：

```text
1. 空 query 返回 []
2. max_results <= 0 返回 []
3. GitHub API item 可以解析为标准 dict
4. 请求异常时返回 []
5. 没有 API key 时使用本地筛选
6. summarize_repository() 输出中文摘要字段
7. 有 API key 时可以使用 LLM 结构化结果
8. LLM 失败时 fallback 不影响报告生成
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
1. search_github_repositories("AI agent", 3) 返回 list
2. 每个 repo 至少包含 name、description、stars、language、url、created_at、updated_at
3. select_important_repositories() 可以返回 top_k 个项目
4. summarize_repository() 输出 report_agent.py 所需字段
5. 没有 GITHUB_TOKEN 和 OPENAI_API_KEY 时，主流程仍可运行
6. 有 OPENAI_API_KEY 时，可以生成结构化 GitHub 项目总结
7. 单元测试和 compileall 通过
```

---

## 9. 当前限制

```text
1. 不读取 README，所以项目总结主要依赖 GitHub description
2. 没有 GITHUB_TOKEN 时 GitHub API rate limit 更低
3. 没有 OPENAI_API_KEY 时，结构化总结仍然是 fallback 内容
4. 没有历史记录，可能重复推荐同一个热门项目
5. 当前按搜索结果和 stars 选择，不能代表真实增长趋势
```

---

## 10. 下一步建议

```text
1. 配置 GITHUB_TOKEN，提升 GitHub API 稳定性
2. 配置 OPENAI_API_KEY，验证真实项目总结效果
3. 接入 prompt 文件，避免 prompt 写死在代码里
4. 后续读取 README，提高 GitHub 项目总结质量
5. 再进入 Version 2 的 AI news 支持
```

---

## 11. 第二阶段：GitHub 总结增强

当前 GitHub 功能已经可以把项目数据写入日报，但报告内容仍然主要依赖 GitHub description。

例如当前日报中 GitHub 项目通常会出现：

```text
Summary: repo description
Main Features: repo description
Technical Highlights: TBD
Learning Value: TBD
Recommended For: TBD
Possible Use Cases: TBD
```

这说明 GitHub 链路已经跑通，但还没有真正形成“项目分析”。本阶段目标是让 GitHub 总结从“能显示”升级为“有分析价值”。

---

### 11.1 功能目标

本阶段需要完成：

```text
输入：GitHub Search API 返回的仓库列表
处理：读取更丰富的仓库上下文，并生成结构化项目分析
输出：更完整、更可读的 repo_summaries
```

增强后的 GitHub 项目总结应该回答：

```text
1. 这个项目是做什么的
2. 它解决了什么开发或研究问题
3. 主要功能有哪些
4. 技术亮点是什么
5. 适合谁学习或使用
6. 可以用在什么场景
7. 为什么它值得出现在今天的报告中
```

目标输出字段继续保持和 `report_agent.py` 兼容：

```python
{
    "name": "owner/repo",
    "one_sentence_summary": "...",
    "chinese_summary": "...",
    "main_features": "...",
    "technical_highlights": "...",
    "learning_value": "...",
    "recommended_for": "...",
    "possible_use_cases": "...",
    "stars": 1200,
    "url": "https://github.com/owner/repo"
}
```

可以新增但不强制展示的内部字段：

```python
{
    "readme_excerpt": "...",
    "topics": ["llm", "rag"],
    "homepage": "...",
    "license": "MIT"
}
```

---

### 11.2 本阶段不做什么

为了控制复杂度，本阶段暂时不做：

```text
1. 不 clone 仓库
2. 不分析源码目录
3. 不计算 star 增长趋势
4. 不保存历史数据库
5. 不抓取 issue、PR、release 全量数据
6. 不做项目安全审计
7. 不做复杂多 Agent 协作
```

当前目标是先提高日报里的 GitHub 项目总结质量，而不是做完整开源项目评估系统。

---

### 11.3 推荐实现顺序

推荐按以下顺序推进：

```text
Step 1: 配置 OPENAI_API_KEY，验证当前 LLM 总结路径
Step 2: 将 github_summary_prompt.txt 接入 github_agent.py
Step 3: 将 github_selection_prompt.txt 接入 github_agent.py
Step 4: 扩展 github_tool.py，解析 topics、homepage、license 等轻量字段
Step 5: 增加 README 获取函数，只读取前 N 个字符作为上下文
Step 6: 在 summarize_repository() 中把 description + topics + README excerpt 交给 LLM
Step 7: 补充测试，保证无网络、无 key、LLM 失败时仍可 fallback
```

这样可以先验证 LLM 总结效果，再逐步增加上下文。不要一开始就读取太多 GitHub 内容，否则容易把 OpenAI、prompt、README、GitHub API 的问题混在一起。

---

### 11.4 Prompt 文件化

当前 `github_agent.py` 中的 prompt 是内联字符串。为了后续调优，需要改为读取：

```text
prompts/github_selection_prompt.txt
prompts/github_summary_prompt.txt
```

建议增加内部函数：

```python
def _load_prompt_template(filename: str, fallback: str) -> str:
    ...
```

要求：

```text
1. 优先读取 prompts/ 下的 prompt 文件
2. 文件不存在或读取失败时使用代码内 fallback
3. prompt 文件只负责模板，不负责 API 调用
4. 单元测试不依赖真实文件系统复杂状态
```

好处：

```text
1. 调整总结风格时不用改 Python 代码
2. prompt 可以和开发文档一起迭代
3. 后续 paper_agent.py 也可以复用同样模式
```

---

### 11.5 README 获取设计

建议新增函数：

```python
def fetch_repository_readme(
    full_name: str,
    max_chars: int = 6000,
) -> str:
    ...
```

GitHub API：

```text
GET https://api.github.com/repos/{owner}/{repo}/readme
```

实现要求：

```text
1. 使用 GITHUB_TOKEN 认证
2. 只返回 README 文本前 max_chars 个字符
3. README 不存在、请求失败或解码失败时返回 ""
4. 不让 README 获取失败影响主流程
5. 不把超长 README 直接塞进 LLM，避免 token 成本失控
```

README 可以给 LLM 提供的信息：

```text
1. 项目介绍
2. 安装方式
3. 核心功能
4. 示例代码
5. 使用场景
6. 支持的模型或框架
```

---

### 11.6 GitHub Summary Prompt 目标

增强后的 prompt 应要求 LLM：

```text
1. 不要只复述 description
2. 基于 description、topics、language、stars、README excerpt 做总结
3. 输出 JSON object
4. 所有字段必须是字符串
5. 中文摘要要自然，不要机器翻译腔
6. 如果信息不足，明确写“信息不足”，不要编造功能
```

期望 JSON 字段：

```text
one_sentence_summary
chinese_summary
main_features
technical_highlights
learning_value
recommended_for
possible_use_cases
```

---

### 11.7 测试计划

需要补充或调整的测试：

```text
1. prompt 文件读取成功时使用文件内容
2. prompt 文件缺失时使用 fallback
3. GitHub repo item 可以解析 topics、homepage、license
4. fetch_repository_readme() 可以解析 base64 README 内容
5. fetch_repository_readme() 请求失败时返回 ""
6. summarize_repository() 有 README 上下文时仍返回稳定字段
7. OpenAI 返回部分字段时，_merge_repository_summary() 自动补 fallback
8. 没有 OPENAI_API_KEY 时不读取 README 或不调用 OpenAI
```

测试原则：

```text
1. 不真实请求 GitHub API
2. 不真实调用 OpenAI API
3. 用 fake requests 和 patch 模拟外部依赖
4. 主流程失败时仍能生成部分报告
```

---

### 11.8 验收标准

本阶段完成后应该满足：

```text
1. 配置 OPENAI_API_KEY 后，GitHub 项目不再大面积显示 TBD
2. GitHub 项目的 technical_highlights、learning_value、recommended_for、possible_use_cases 有实际内容
3. prompt 文件可以控制 GitHub 总结风格
4. README 获取失败不会导致 main.py 失败
5. 无 OPENAI_API_KEY 时 fallback 行为保持稳定
6. 单元测试和 compileall 通过
7. 新生成的 daily_ai_report_YYYY-MM-DD.md 同时包含论文和 GitHub 项目
```

验收命令：

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q .
.venv/bin/python main.py
```

---

### 11.9 风险与限制

```text
1. README 内容可能很长，需要截断
2. README 可能不是英文，LLM 总结质量会波动
3. GitHub API rate limit 可能限制 README 获取数量
4. 热门项目不一定是最新项目
5. LLM 可能基于不足信息做过度推断，需要 prompt 约束
```

---

### 11.10 建议完成顺序

推荐下一步具体执行：

```text
1. 先填 OPENAI_API_KEY，直接跑一次当前 GitHub LLM 总结
2. 如果总结质量尚可，再做 prompt 文件化
3. 如果总结内容太空，再增加 README excerpt
4. 等 GitHub 报告质量稳定后，再进入 News 功能
```

---

## 12. 第二阶段实现结果

本次已经完成 `## 11. 第二阶段：GitHub 总结增强` 的第一版实现。

已完成：

```text
1. github_agent.py 已接入 prompts/github_selection_prompt.txt
2. github_agent.py 已接入 prompts/github_summary_prompt.txt
3. github_tool.py 已解析 topics、homepage、license 等轻量字段
4. github_tool.py 已新增 fetch_repository_readme()
5. summarize_repository() 在有 OPENAI_API_KEY 时会把 README excerpt 交给 LLM
6. 没有 OPENAI_API_KEY 时仍然保持原有 fallback，不额外请求 README
7. README 请求失败、prompt 文件缺失、prompt 格式错误时都可以 fallback
```

本次补充的测试覆盖：

```text
1. prompt 文件读取成功
2. prompt 文件缺失 fallback
3. prompt format 失败 fallback
4. GitHub repo item 解析 topics、homepage、license
5. README base64 内容解码
6. README 请求失败返回 ""
7. LLM 总结 prompt 中包含 README excerpt 和 topics
```

已通过验收命令：

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q .
```

当前仍需真实验证：

```text
1. 配置 OPENAI_API_KEY 后运行 main.py
2. 检查 GitHub 项目的 technical_highlights、learning_value、recommended_for、possible_use_cases 是否明显优于 description fallback
3. 根据真实输出继续调 prompts/github_summary_prompt.txt
```
