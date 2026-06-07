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
