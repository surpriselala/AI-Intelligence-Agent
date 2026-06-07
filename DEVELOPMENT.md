# Development Document / 开发文档

## English Version

### 1. Development Background

The purpose of this project is to build an AI-powered intelligence agent that automatically tracks and summarizes the latest developments in artificial intelligence.

The agent focuses on three main information sources:

```text
1. Research papers
2. GitHub open-source projects
3. AI industry news
```

The final output is a structured daily AI intelligence report.

This project can be understood as an extension of an Email Agent. Instead of reading and processing emails, this agent reads and processes public AI information sources.

---

### 2. Core Development Principle

The first version should not be overly complex.

The development principle is:

```text
Build the workflow first, then upgrade it into an agent.
```

The first MVP should follow a fixed workflow:

```text
Collect information
   ↓
Filter useful content
   ↓
Summarize selected items
   ↓
Generate Markdown report
   ↓
Save report
```

After this workflow is stable, more agent-like capabilities can be added gradually.

---

### 3. MVP Scope

The first version only needs to support:

```text
1. Fetch recent AI papers from arXiv
2. Fetch AI-related repositories from GitHub
3. Use LLM to select and summarize important items
4. Generate a Markdown daily report
```

The first version does not need:

```text
1. Web frontend
2. User login
3. Vector database
4. Multi-agent collaboration
5. Complex memory
6. Automatic email delivery
7. Notion integration
```

These features can be added later.

---

### 4. Main Workflow

The MVP workflow is:

```text
Step 1: Load configuration
Step 2: Collect paper data from arXiv
Step 3: Collect repository data from GitHub
Step 4: Use LLM to select important papers
Step 5: Use LLM to select important repositories
Step 6: Summarize selected papers
Step 7: Summarize selected repositories
Step 8: Build Markdown report
Step 9: Save the report to outputs/
```

Pseudo code:

```python
def main():
    papers = collect_papers()
    repos = collect_repositories()

    selected_papers = select_important_papers(papers)
    selected_repos = select_important_repos(repos)

    paper_summaries = summarize_papers(selected_papers)
    repo_summaries = summarize_repositories(selected_repos)

    report = build_report(
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries
    )

    save_report(report)
```

---

### 5. Recommended Project Structure

```text
ai-intelligence-agent/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── DEVELOPMENT.md
│
├── tools/
│   ├── arxiv_tool.py
│   ├── github_tool.py
│   └── news_tool.py
│
├── agents/
│   ├── paper_agent.py
│   ├── github_agent.py
│   ├── news_agent.py
│   └── report_agent.py
│
├── prompts/
│   ├── paper_selection_prompt.txt
│   ├── paper_summary_prompt.txt
│   ├── github_selection_prompt.txt
│   ├── github_summary_prompt.txt
│   └── report_prompt.txt
│
├── outputs/
│   └── daily_ai_report.md
│
├── data/
│   └── history.db
│
└── tests/
    ├── test_arxiv_tool.py
    ├── test_github_tool.py
    └── test_report_agent.py
```

---

### 6. Module Design

#### 6.1 config.py

Responsible for global configuration.

Example:

```python
AI_KEYWORDS = [
    "large language model",
    "AI agent",
    "RAG",
    "multimodal AI",
    "AI coding",
    "reasoning model"
]

ARXIV_MAX_RESULTS = 10
GITHUB_MAX_RESULTS = 10
REPORT_OUTPUT_PATH = "outputs/daily_ai_report.md"
```

Environment variables:

```text
OPENAI_API_KEY
GITHUB_TOKEN
```

---

#### 6.2 tools/arxiv_tool.py

Responsible for collecting papers from arXiv.

Main function:

```python
def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict]:
    pass
```

Expected output:

```python
[
    {
        "title": "Paper title",
        "authors": ["Author A", "Author B"],
        "summary": "Paper abstract",
        "published_date": "2026-06-07",
        "url": "https://arxiv.org/abs/xxxx.xxxxx"
    }
]
```

Responsibilities:

```text
1. Search papers by keyword
2. Parse title, authors, abstract, date, and URL
3. Return structured data
```

---

#### 6.3 tools/github_tool.py

Responsible for collecting GitHub repositories.

Main function:

```python
def search_github_repositories(query: str, max_results: int = 10) -> list[dict]:
    pass
```

Expected output:

```python
[
    {
        "name": "repo-name",
        "description": "Repository description",
        "stars": 1200,
        "language": "Python",
        "url": "https://github.com/user/repo",
        "created_at": "2026-06-07",
        "updated_at": "2026-06-07"
    }
]
```

Responsibilities:

```text
1. Search AI-related repositories
2. Sort repositories by relevance or stars
3. Return structured repository data
```

---

#### 6.4 tools/news_tool.py

Responsible for collecting AI news.

This module can be added in Version 2.

Possible sources:

```text
1. Company blogs
2. RSS feeds
3. Hacker News
4. Tech news websites
5. Product Hunt
```

Main function:

```python
def collect_ai_news(max_results: int = 10) -> list[dict]:
    pass
```

---

### 7. Agent Design

In the MVP version, the agent does not need autonomous planning. It can be implemented as several LLM-powered processing modules.

---

#### 7.1 Paper Agent

File:

```text
agents/paper_agent.py
```

Responsibilities:

```text
1. Select important papers
2. Summarize selected papers
3. Extract technical value and learning value
```

Main functions:

```python
def select_important_papers(papers: list[dict], top_k: int = 3) -> list[dict]:
    pass

def summarize_paper(paper: dict) -> dict:
    pass
```

Paper summary output:

```python
{
    "title": "Paper title",
    "one_sentence_summary": "...",
    "research_problem": "...",
    "core_method": "...",
    "innovation": "...",
    "why_it_matters": "...",
    "learning_value": "...",
    "url": "..."
}
```

---

#### 7.2 GitHub Agent

File:

```text
agents/github_agent.py
```

Responsibilities:

```text
1. Select valuable repositories
2. Summarize project features
3. Evaluate learning value
```

Main functions:

```python
def select_important_repositories(repos: list[dict], top_k: int = 3) -> list[dict]:
    pass

def summarize_repository(repo: dict) -> dict:
    pass
```

Repository summary output:

```python
{
    "name": "Repository name",
    "one_sentence_summary": "...",
    "main_features": "...",
    "learning_value": "...",
    "recommended_for": "...",
    "stars": 1200,
    "url": "..."
}
```

---

#### 7.3 Report Agent

File:

```text
agents/report_agent.py
```

Responsibilities:

```text
1. Combine paper summaries and repository summaries
2. Generate a complete Markdown report
3. Ensure the report is readable and structured
```

Main function:

```python
def build_daily_report(
    paper_summaries: list[dict],
    repo_summaries: list[dict],
    news_summaries: list[dict] | None = None
) -> str:
    pass
```

---

### 8. Prompt Design

#### 8.1 Paper Selection Prompt

```text
You are an AI research intelligence analyst.

The following are candidate AI research papers collected today.
Please select the top {top_k} papers that are most worth reading.

Selection criteria:
1. Relevance to AI, LLM, Agent, RAG, Multimodal AI, AI Coding, or Machine Learning
2. Novelty of the idea
3. Potential impact on AI development
4. Learning value for AI developers or students
5. Practical or research significance

Return the result in JSON format.

Candidate papers:
{papers}
```

---

#### 8.2 Paper Summary Prompt

```text
You are an AI research assistant.

Please summarize the following paper in a clear and structured way.

Paper title:
{title}

Abstract:
{abstract}

Please output the following fields:

1. one_sentence_summary
2. research_problem
3. core_method
4. key_innovation
5. why_it_matters
6. potential_application
7. learning_value

Use concise and clear language.
```

---

#### 8.3 GitHub Selection Prompt

```text
You are an AI open-source project analyst.

The following are candidate GitHub repositories collected today.
Please select the top {top_k} repositories that are most valuable for AI learning or development.

Selection criteria:
1. Relevance to AI, LLM, Agent, RAG, or Machine Learning
2. Practical usefulness
3. Learning value
4. Code or documentation quality
5. Popularity or recent attention

Return the result in JSON format.

Candidate repositories:
{repos}
```

---

#### 8.4 GitHub Summary Prompt

```text
You are an AI engineering assistant.

Please summarize the following GitHub repository.

Repository name:
{name}

Description:
{description}

Stars:
{stars}

Language:
{language}

URL:
{url}

Please output the following fields:

1. one_sentence_summary
2. main_features
3. technical_highlights
4. learning_value
5. recommended_for
6. possible_use_cases

Use concise and clear language.
```

---

### 9. Data Flow

Paper data flow:

```text
arXiv API
   ↓
arxiv_tool.py
   ↓
paper_agent.py
   ↓
report_agent.py
   ↓
daily_ai_report.md
```

GitHub data flow:

```text
GitHub API
   ↓
github_tool.py
   ↓
github_agent.py
   ↓
report_agent.py
   ↓
daily_ai_report.md
```

---

### 10. Development Steps

#### Step 1: Initialize the project

```bash
mkdir ai-intelligence-agent
cd ai-intelligence-agent
touch main.py config.py requirements.txt README.md DEVELOPMENT.md
mkdir tools agents prompts outputs data tests
```

---

#### Step 2: Implement arXiv tool

Goal:

```text
Given a keyword, return recent AI papers.
```

Example:

```python
papers = search_arxiv_papers("AI agent", max_results=10)
```

---

#### Step 3: Implement GitHub tool

Goal:

```text
Given a keyword, return AI-related repositories.
```

Example:

```python
repos = search_github_repositories("AI agent", max_results=10)
```

---

#### Step 4: Implement LLM client

Create a simple reusable LLM calling function:

```python
def call_llm(prompt: str) -> str:
    pass
```

---

#### Step 5: Implement paper agent

Functions:

```python
select_important_papers()
summarize_paper()
```

Goal:

```text
Input: 10 papers
Output: 3 selected and summarized papers
```

---

#### Step 6: Implement GitHub agent

Functions:

```python
select_important_repositories()
summarize_repository()
```

Goal:

```text
Input: 10 repositories
Output: 3 selected and summarized repositories
```

---

#### Step 7: Implement report agent

Function:

```python
build_daily_report()
```

Goal:

```text
Input: paper summaries + repository summaries
Output: Markdown report
```

---

#### Step 8: Connect everything in main.py

Example:

```python
def main():
    papers = search_arxiv_papers("AI agent OR large language model OR RAG", 10)
    repos = search_github_repositories("AI agent", 10)

    selected_papers = select_important_papers(papers, top_k=3)
    selected_repos = select_important_repositories(repos, top_k=3)

    paper_summaries = [summarize_paper(paper) for paper in selected_papers]
    repo_summaries = [summarize_repository(repo) for repo in selected_repos]

    report = build_daily_report(paper_summaries, repo_summaries)

    with open("outputs/daily_ai_report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
```

---

### 11. Requirements

Initial dependencies:

```text
openai
requests
python-dotenv
feedparser
arxiv
```

Possible later dependencies:

```text
fastapi
uvicorn
apscheduler
sqlalchemy
pydantic
langgraph
chromadb
```

Example `requirements.txt`:

```text
openai
requests
python-dotenv
feedparser
arxiv
```

---

### 12. Environment Variables

Create a `.env` file:

```text
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
```

Do not upload `.env` to GitHub.

Add `.env` to `.gitignore`:

```text
.env
__pycache__/
outputs/
data/
```

---

### 13. Error Handling

The system should handle:

```text
1. API request failure
2. Empty search result
3. Invalid LLM output
4. JSON parsing failure
5. Missing environment variables
6. Rate limit errors
```

Recommended strategy:

```text
1. Print clear error messages
2. Skip failed items instead of stopping the whole process
3. Save partial reports when possible
4. Add retry logic for API calls
```

---

### 14. Testing Plan

Test arXiv tool:

```python
def test_search_arxiv_papers():
    papers = search_arxiv_papers("AI agent", max_results=3)
    assert len(papers) > 0
    assert "title" in papers[0]
    assert "url" in papers[0]
```

Test GitHub tool:

```python
def test_search_github_repositories():
    repos = search_github_repositories("AI agent", max_results=3)
    assert len(repos) > 0
    assert "name" in repos[0]
    assert "url" in repos[0]
```

Test report generation:

```python
def test_build_daily_report():
    report = build_daily_report([], [])
    assert isinstance(report, str)
    assert "# Daily AI Intelligence Report" in report
```

---

### 15. Definition of Done for MVP

The MVP is complete when:

```text
1. Running `python main.py` successfully collects paper data
2. Running `python main.py` successfully collects GitHub repository data
3. The LLM can summarize at least 3 papers
4. The LLM can summarize at least 3 repositories
5. A Markdown report is generated in outputs/
6. The report is readable and structured
```

---

### 16. Relationship to Email Agent

This project can be understood as an extension of an Email Agent.

| Email Agent | AI Intelligence Agent |
|---|---|
| Read emails | Read papers, repositories, and news |
| Classify email intent | Classify content importance |
| Call email tools | Call arXiv, GitHub, and news tools |
| Generate email replies | Generate daily AI reports |
| Execute email actions | Save or deliver reports |

The core transferable skills are:

```text
1. Tool design
2. Prompt engineering
3. Workflow control
4. Structured LLM output
5. Backend implementation
```

---

## 中文版本

### 1. 开发背景

本项目的目标是构建一个 AI 技术情报智能体，用于自动追踪和总结人工智能领域的最新进展。

Agent 主要关注三类信息源：

```text
1. 研究论文
2. GitHub 开源项目
3. AI 行业新闻
```

最终输出是一份结构化的每日 AI 技术情报报告。

这个项目可以理解为 Email Agent 的延伸。Email Agent 处理的是邮件，而 AI Intelligence Agent 处理的是公开的 AI 信息源，例如论文、开源项目和新闻。

---

### 2. 核心开发原则

第一版不要做得过于复杂。

本项目的开发原则是：

```text
先做 workflow，再升级成 agent。
```

第一版 MVP 应该先按照固定流程运行：

```text
收集信息
   ↓
筛选有价值内容
   ↓
总结被选中的内容
   ↓
生成 Markdown 报告
   ↓
保存报告
```

当这个流程稳定后，再逐步加入更强的 Agent 能力。

---

### 3. MVP 范围

第一版只需要支持：

```text
1. 从 arXiv 获取最新 AI 论文
2. 从 GitHub 获取 AI 相关项目
3. 使用 LLM 选择并总结重要内容
4. 生成 Markdown 每日 AI 报告
```

第一版暂时不需要：

```text
1. Web 前端
2. 用户登录
3. 向量数据库
4. 多 Agent 协作
5. 复杂记忆系统
6. 自动邮件推送
7. Notion 集成
```

这些功能可以后续再加入。

---

### 4. 主工作流

MVP 工作流如下：

```text
Step 1: 加载配置
Step 2: 从 arXiv 收集论文数据
Step 3: 从 GitHub 收集项目数据
Step 4: 使用 LLM 选择重要论文
Step 5: 使用 LLM 选择重要 GitHub 项目
Step 6: 总结选中的论文
Step 7: 总结选中的 GitHub 项目
Step 8: 生成 Markdown 报告
Step 9: 保存报告到 outputs/
```

伪代码：

```python
def main():
    papers = collect_papers()
    repos = collect_repositories()

    selected_papers = select_important_papers(papers)
    selected_repos = select_important_repos(repos)

    paper_summaries = summarize_papers(selected_papers)
    repo_summaries = summarize_repositories(selected_repos)

    report = build_report(
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries
    )

    save_report(report)
```

---

### 5. 推荐项目结构

```text
ai-intelligence-agent/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── DEVELOPMENT.md
│
├── tools/
│   ├── arxiv_tool.py
│   ├── github_tool.py
│   └── news_tool.py
│
├── agents/
│   ├── paper_agent.py
│   ├── github_agent.py
│   ├── news_agent.py
│   └── report_agent.py
│
├── prompts/
│   ├── paper_selection_prompt.txt
│   ├── paper_summary_prompt.txt
│   ├── github_selection_prompt.txt
│   ├── github_summary_prompt.txt
│   └── report_prompt.txt
│
├── outputs/
│   └── daily_ai_report.md
│
├── data/
│   └── history.db
│
└── tests/
    ├── test_arxiv_tool.py
    ├── test_github_tool.py
    └── test_report_agent.py
```

---

### 6. 模块设计

#### 6.1 config.py

负责全局配置。

示例：

```python
AI_KEYWORDS = [
    "large language model",
    "AI agent",
    "RAG",
    "multimodal AI",
    "AI coding",
    "reasoning model"
]

ARXIV_MAX_RESULTS = 10
GITHUB_MAX_RESULTS = 10
REPORT_OUTPUT_PATH = "outputs/daily_ai_report.md"
```

环境变量：

```text
OPENAI_API_KEY
GITHUB_TOKEN
```

---

#### 6.2 tools/arxiv_tool.py

负责从 arXiv 收集论文。

主函数：

```python
def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict]:
    pass
```

期望输出：

```python
[
    {
        "title": "Paper title",
        "authors": ["Author A", "Author B"],
        "summary": "Paper abstract",
        "published_date": "2026-06-07",
        "url": "https://arxiv.org/abs/xxxx.xxxxx"
    }
]
```

职责：

```text
1. 根据关键词搜索论文
2. 解析标题、作者、摘要、日期和链接
3. 返回结构化数据
```

---

#### 6.3 tools/github_tool.py

负责从 GitHub 收集项目。

主函数：

```python
def search_github_repositories(query: str, max_results: int = 10) -> list[dict]:
    pass
```

期望输出：

```python
[
    {
        "name": "repo-name",
        "description": "Repository description",
        "stars": 1200,
        "language": "Python",
        "url": "https://github.com/user/repo",
        "created_at": "2026-06-07",
        "updated_at": "2026-06-07"
    }
]
```

职责：

```text
1. 搜索 AI 相关 GitHub 仓库
2. 根据相关性或 star 数排序
3. 返回结构化仓库数据
```

---

#### 6.4 tools/news_tool.py

负责收集 AI 新闻。

该模块可以在 Version 2 中加入。

可选信息源：

```text
1. 公司博客
2. RSS feeds
3. Hacker News
4. 科技新闻网站
5. Product Hunt
```

主函数：

```python
def collect_ai_news(max_results: int = 10) -> list[dict]:
    pass
```

---

### 7. Agent 设计

在 MVP 版本中，Agent 不需要具备完全自主规划能力。可以先实现为多个由 LLM 驱动的处理模块。

---

#### 7.1 Paper Agent

文件：

```text
agents/paper_agent.py
```

职责：

```text
1. 选择重要论文
2. 总结选中的论文
3. 提取技术价值和学习价值
```

主函数：

```python
def select_important_papers(papers: list[dict], top_k: int = 3) -> list[dict]:
    pass

def summarize_paper(paper: dict) -> dict:
    pass
```

论文总结输出：

```python
{
    "title": "Paper title",
    "one_sentence_summary": "...",
    "research_problem": "...",
    "core_method": "...",
    "innovation": "...",
    "why_it_matters": "...",
    "learning_value": "...",
    "url": "..."
}
```

---

#### 7.2 GitHub Agent

文件：

```text
agents/github_agent.py
```

职责：

```text
1. 选择有价值的仓库
2. 总结项目功能
3. 评估学习价值
```

主函数：

```python
def select_important_repositories(repos: list[dict], top_k: int = 3) -> list[dict]:
    pass

def summarize_repository(repo: dict) -> dict:
    pass
```

项目总结输出：

```python
{
    "name": "Repository name",
    "one_sentence_summary": "...",
    "main_features": "...",
    "learning_value": "...",
    "recommended_for": "...",
    "stars": 1200,
    "url": "..."
}
```

---

#### 7.3 Report Agent

文件：

```text
agents/report_agent.py
```

职责：

```text
1. 合并论文总结和项目总结
2. 生成完整 Markdown 报告
3. 保证报告清晰、可读、结构化
```

主函数：

```python
def build_daily_report(
    paper_summaries: list[dict],
    repo_summaries: list[dict],
    news_summaries: list[dict] | None = None
) -> str:
    pass
```

---

### 8. Prompt 设计

#### 8.1 论文选择 Prompt

```text
You are an AI research intelligence analyst.

The following are candidate AI research papers collected today.
Please select the top {top_k} papers that are most worth reading.

Selection criteria:
1. Relevance to AI, LLM, Agent, RAG, Multimodal AI, AI Coding, or Machine Learning
2. Novelty of the idea
3. Potential impact on AI development
4. Learning value for AI developers or students
5. Practical or research significance

Return the result in JSON format.

Candidate papers:
{papers}
```

---

#### 8.2 论文总结 Prompt

```text
You are an AI research assistant.

Please summarize the following paper in a clear and structured way.

Paper title:
{title}

Abstract:
{abstract}

Please output the following fields:

1. one_sentence_summary
2. research_problem
3. core_method
4. key_innovation
5. why_it_matters
6. potential_application
7. learning_value

Use concise and clear language.
```

---

#### 8.3 GitHub 项目选择 Prompt

```text
You are an AI open-source project analyst.

The following are candidate GitHub repositories collected today.
Please select the top {top_k} repositories that are most valuable for AI learning or development.

Selection criteria:
1. Relevance to AI, LLM, Agent, RAG, or Machine Learning
2. Practical usefulness
3. Learning value
4. Code or documentation quality
5. Popularity or recent attention

Return the result in JSON format.

Candidate repositories:
{repos}
```

---

#### 8.4 GitHub 项目总结 Prompt

```text
You are an AI engineering assistant.

Please summarize the following GitHub repository.

Repository name:
{name}

Description:
{description}

Stars:
{stars}

Language:
{language}

URL:
{url}

Please output the following fields:

1. one_sentence_summary
2. main_features
3. technical_highlights
4. learning_value
5. recommended_for
6. possible_use_cases

Use concise and clear language.
```

---

### 9. 数据流

论文数据流：

```text
arXiv API
   ↓
arxiv_tool.py
   ↓
paper_agent.py
   ↓
report_agent.py
   ↓
daily_ai_report.md
```

GitHub 数据流：

```text
GitHub API
   ↓
github_tool.py
   ↓
github_agent.py
   ↓
report_agent.py
   ↓
daily_ai_report.md
```

---

### 10. 开发步骤

#### Step 1：初始化项目

```bash
mkdir ai-intelligence-agent
cd ai-intelligence-agent
touch main.py config.py requirements.txt README.md DEVELOPMENT.md
mkdir tools agents prompts outputs data tests
```

---

#### Step 2：实现 arXiv 工具

目标：

```text
给定关键词，返回最近的 AI 论文。
```

示例：

```python
papers = search_arxiv_papers("AI agent", max_results=10)
```

---

#### Step 3：实现 GitHub 工具

目标：

```text
给定关键词，返回 AI 相关 GitHub 仓库。
```

示例：

```python
repos = search_github_repositories("AI agent", max_results=10)
```

---

#### Step 4：实现 LLM Client

创建一个可复用的大模型调用函数：

```python
def call_llm(prompt: str) -> str:
    pass
```

---

#### Step 5：实现 Paper Agent

函数：

```python
select_important_papers()
summarize_paper()
```

目标：

```text
输入 10 篇论文，输出 3 篇被选中并总结后的论文。
```

---

#### Step 6：实现 GitHub Agent

函数：

```python
select_important_repositories()
summarize_repository()
```

目标：

```text
输入 10 个仓库，输出 3 个被选中并总结后的仓库。
```

---

#### Step 7：实现 Report Agent

函数：

```python
build_daily_report()
```

目标：

```text
输入论文总结和仓库总结，输出 Markdown 报告。
```

---

#### Step 8：在 main.py 中连接完整流程

示例：

```python
def main():
    papers = search_arxiv_papers("AI agent OR large language model OR RAG", 10)
    repos = search_github_repositories("AI agent", 10)

    selected_papers = select_important_papers(papers, top_k=3)
    selected_repos = select_important_repositories(repos, top_k=3)

    paper_summaries = [summarize_paper(paper) for paper in selected_papers]
    repo_summaries = [summarize_repository(repo) for repo in selected_repos]

    report = build_daily_report(paper_summaries, repo_summaries)

    with open("outputs/daily_ai_report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
```

---

### 11. 依赖项

初始依赖：

```text
openai
requests
python-dotenv
feedparser
arxiv
```

后续可能加入：

```text
fastapi
uvicorn
apscheduler
sqlalchemy
pydantic
langgraph
chromadb
```

`requirements.txt` 示例：

```text
openai
requests
python-dotenv
feedparser
arxiv
```

---

### 12. 环境变量

创建 `.env` 文件：

```text
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
```

不要把 `.env` 上传到 GitHub。

在 `.gitignore` 中加入：

```text
.env
__pycache__/
outputs/
data/
```

---

### 13. 错误处理

系统需要处理：

```text
1. API 请求失败
2. 搜索结果为空
3. LLM 输出格式错误
4. JSON 解析失败
5. 环境变量缺失
6. API rate limit
```

推荐策略：

```text
1. 打印清晰的错误信息
2. 跳过失败项，而不是让整个程序停止
3. 尽可能保存部分报告
4. 为 API 调用添加 retry 逻辑
```

---

### 14. 测试计划

测试 arXiv 工具：

```python
def test_search_arxiv_papers():
    papers = search_arxiv_papers("AI agent", max_results=3)
    assert len(papers) > 0
    assert "title" in papers[0]
    assert "url" in papers[0]
```

测试 GitHub 工具：

```python
def test_search_github_repositories():
    repos = search_github_repositories("AI agent", max_results=3)
    assert len(repos) > 0
    assert "name" in repos[0]
    assert "url" in repos[0]
```

测试报告生成：

```python
def test_build_daily_report():
    report = build_daily_report([], [])
    assert isinstance(report, str)
    assert "# Daily AI Intelligence Report" in report
```

---

### 15. MVP 完成标准

当满足以下条件时，MVP 可以认为完成：

```text
1. 运行 `python main.py` 能够成功获取论文数据
2. 运行 `python main.py` 能够成功获取 GitHub 仓库数据
3. LLM 能够总结至少 3 篇论文
4. LLM 能够总结至少 3 个 GitHub 项目
5. 能够在 outputs/ 目录下生成 Markdown 报告
6. 报告内容清晰、结构完整、可阅读
```

---

### 16. 与 Email Agent 的关系

本项目可以理解为 Email Agent 的延伸。

| Email Agent | AI Intelligence Agent |
|---|---|
| 读取邮件 | 读取论文、GitHub 项目和新闻 |
| 判断邮件意图 | 判断内容重要性 |
| 调用邮件工具 | 调用 arXiv、GitHub 和新闻工具 |
| 生成邮件回复 | 生成每日 AI 报告 |
| 执行邮件操作 | 保存或推送报告 |

可迁移的核心能力包括：

```text
1. Tool 设计
2. Prompt Engineering
3. 工作流控制
4. 结构化 LLM 输出
5. 后端实现能力
```
