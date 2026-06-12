# AI Intelligence Agent

AI Intelligence Agent is an automated daily AI research and industry intelligence assistant.  
It collects the latest AI-related papers, GitHub projects, and industry news, then uses large language models to filter, summarize, rank, and generate a structured daily AI report.

The goal of this project is to help AI learners, researchers, and developers quickly understand important daily developments in artificial intelligence.

---

## Project Overview

With the rapid development of AI, new papers, open-source projects, tools, and company updates appear every day. However, manually tracking these sources is time-consuming and inefficient.

This project aims to build an AI-powered agent that can automatically:

- Collect the latest AI research papers
- Track trending AI-related GitHub repositories
- Gather important AI industry news
- Filter and rank valuable information
- Summarize technical content in a structured format
- Generate a daily AI intelligence report

The project is designed as a practical agent system that combines tool usage, prompt engineering, workflow orchestration, and LLM-based summarization.

---

## Core Features

### 1. AI Paper Tracking

The agent collects recent AI-related papers from sources such as arXiv.

It focuses on topics including:

- Large Language Models
- AI Agents
- RAG
- Multimodal AI
- AI Coding
- Model Compression
- Reasoning Models
- Machine Learning Systems

For each selected paper, the agent generates:

- One-sentence summary
- Research problem
- Core method
- Key innovation
- Why it matters
- Potential applications
- Original paper link

---

### 2. GitHub Trending Project Tracking

The agent searches for AI-related GitHub repositories that are gaining attention.

It analyzes projects based on:

- Relevance to AI learning
- Practical value
- Star growth
- README quality
- Technical usefulness
- Learning potential

For each selected repository, the agent generates:

- Project name
- Short description
- Main features
- Learning value
- Recommended audience
- GitHub link

---

### 3. AI Industry News Summary

The agent can collect news from AI companies, technical blogs, RSS feeds, and other public sources.

Target companies and organizations may include:

- OpenAI
- Anthropic
- Google DeepMind
- Meta AI
- Microsoft
- NVIDIA
- Mistral AI
- xAI
- Hugging Face

For each news item, the agent summarizes:

- What happened
- Why it matters
- Impact on developers or researchers
- Related technologies
- Source link

---

### 4. Daily Report Generation

The final output is a structured Markdown report.

Example report structure:

```markdown
# Daily AI Intelligence Report

## 1. Research Papers

### Paper 1: Title
- Summary:
- Key Idea:
- Innovation:
- Why It Matters:
- Link:

## 2. GitHub Projects

### Project 1: Repository Name
- Summary:
- Main Features:
- Learning Value:
- Link:

## 3. Industry News

### News 1: Title
- Summary:
- Impact:
- Link:
```

--------------------------------------------------------------------------------

# AI Intelligence Agent 中文说明

AI Intelligence Agent 是一个自动化的每日 AI 技术情报助手。  
它会收集最新的 AI 论文、GitHub 开源项目和行业新闻，并使用大语言模型进行筛选、总结、排序，最终生成结构化的每日 AI 技术情报报告。

这个项目的目标是帮助 AI 学习者、研究人员和开发者快速了解每天值得关注的人工智能进展。

---

## 项目概览

AI 领域发展很快，每天都会出现新的论文、开源项目、工具和公司动态。手动追踪这些信息源既耗时，也很容易遗漏重要内容。

本项目希望构建一个由 AI 驱动的 agent 工作流，自动完成：

- 收集最新 AI 研究论文
- 追踪 AI 相关 GitHub 开源项目
- 收集重要 AI 行业新闻
- 筛选和排序有价值的信息
- 用结构化格式总结技术内容
- 生成每日 AI 技术情报报告

项目设计重点不是一开始就做复杂的多 Agent 系统，而是先搭建稳定的固定工作流：采集信息、筛选内容、生成总结、写入 Markdown 报告。

---

## 核心功能

### 1. AI 论文追踪

Agent 会从 arXiv 等来源收集近期 AI 相关论文。

当前重点关注的方向包括：

- Large Language Models
- AI Agents
- RAG
- Multimodal AI
- AI Coding
- Model Compression
- Reasoning Models
- Machine Learning Systems

对于每篇入选论文，Agent 会生成：

- 一句话总结
- 研究问题
- 核心方法
- 创新点
- 重要性
- 学习价值
- 原论文链接

中文报告中会尽量翻译正文语句，同时保留模型名、方法名、项目名和常见技术术语，例如 LLM、RAG、RL、VLM、Transformer、LoRA 等。

---

### 2. GitHub 开源项目追踪

Agent 会搜索 AI 相关的 GitHub 仓库，并筛选值得关注的项目。

项目分析会参考：

- 与 AI 学习和开发的相关性
- 实用价值
- Stars 数量
- README 信息
- 技术亮点
- 学习价值

对于每个入选项目，Agent 会生成：

- 项目名称
- 简短总结
- 主要功能
- 技术亮点
- 学习价值
- 推荐人群
- 使用场景
- GitHub 链接

---

### 3. AI 行业新闻总结

News 功能可以作为后续版本继续扩展，用于收集 AI 公司博客、技术博客、RSS、新闻网站等公开信息源。

目标关注对象包括：

- OpenAI
- Anthropic
- Google DeepMind
- Meta AI
- Microsoft
- NVIDIA
- Mistral AI
- xAI
- Hugging Face

对于每条新闻，Agent 可以总结：

- 发生了什么
- 为什么重要
- 对开发者或研究人员的影响
- 相关技术
- 来源链接

---

### 4. 每日报告生成

最终输出是一份结构化 Markdown 报告。

报告结构示例：

```markdown
# 每日 AI 技术情报报告

## 1. 研究论文

### 论文 1：标题
- 摘要：
- 研究问题：
- 核心方法：
- 创新点：
- 重要性：
- 学习价值：
- 链接：

## 2. GitHub 项目

### 项目 1：仓库名称
- 摘要：
- 主要功能：
- 技术亮点：
- 学习价值：
- 推荐人群：
- 使用场景：
- Stars：
- 链接：

## 3. 行业新闻

### 新闻 1：标题
- 摘要：
- 影响：
- 链接：
```

---

## 当前 MVP 状态

当前版本已经完成：

- arXiv 论文获取
- 论文筛选和结构化总结
- GitHub 仓库获取
- GitHub 项目筛选和结构化总结
- GitHub README 摘要上下文读取
- 英文和中文 Markdown 报告生成
- `.env` 环境变量配置
- 单元测试和基础编译检查

后续可以继续扩展：

- AI 行业新闻采集
- 历史去重
- 定时任务
- 更丰富的 README 和 release 分析
- 报告推送到邮件、Notion 或其他平台
