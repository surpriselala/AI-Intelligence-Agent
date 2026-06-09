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
