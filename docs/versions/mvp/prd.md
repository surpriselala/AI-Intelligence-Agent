# MVP PRD

## 1. 产品名称

AI Intelligence Agent

---

## 2. 产品定位

AI Intelligence Agent 是一个每日 AI 技术情报助手。

它自动采集 AI 论文、GitHub 开源项目和行业新闻，使用 LLM 进行筛选和结构化总结，并生成每日 Markdown 报告和 Dashboard 展示数据。

---

## 3. MVP 目标

MVP 的目标不是一次性做完整平台，而是先完成一个稳定的 AI 情报工作流：

```text
采集信息
   ↓
筛选重要内容
   ↓
生成中英文结构化总结
   ↓
生成 Markdown 日报
   ↓
保存报告
   ↓
写入数据库
   ↓
提供基础 Dashboard 展示
```

---

## 4. 目标用户

MVP 主要面向：

1. AI 学习者
2. AI 开发者
3. 研究人员
4. 想快速跟踪 AI 行业动态的人

---

## 5. 核心使用场景

### 5.1 每日查看 AI 技术情报

用户每天运行 Agent，获得当天 AI 论文、GitHub 项目和行业新闻摘要。

### 5.2 快速了解值得关注的论文

用户不需要手动浏览 arXiv，通过日报了解近期论文的研究问题、核心方法、创新点和学习价值。

### 5.3 快速发现 GitHub AI 项目

用户可以看到近期值得关注的 AI 开源项目，包括项目用途、技术亮点、学习价值和使用场景。

### 5.4 跟踪 AI 行业新闻

用户可以看到来自 OpenAI、Anthropic、Google DeepMind、Microsoft、NVIDIA、Hugging Face 等来源的新闻摘要。

### 5.5 通过 Dashboard 查看历史内容

用户可以在前端 Dashboard 中查看最新内容和历史归档。

---

## 6. MVP 功能范围

### 6.1 论文模块

功能：

1. 从 arXiv 获取 AI 相关论文。
2. 根据关键词和 LLM 筛选重要论文。
3. 生成结构化英文总结。
4. 生成中文总结。
5. 写入每日 Markdown 报告。

输出字段：

```text
title
one_sentence_summary
research_problem
core_method
innovation
why_it_matters
learning_value
url
```

中文字段：

```text
chinese_summary
chinese_research_problem
chinese_core_method
chinese_innovation
chinese_why_it_matters
chinese_learning_value
```

---

### 6.2 GitHub 模块

功能：

1. 从 GitHub 搜索 AI 相关仓库。
2. 支持 GitHub token。
3. 拉取 README 摘要上下文。
4. 根据项目价值、AI 相关性和 stars 筛选项目。
5. 生成结构化中英文总结。
6. 写入每日 Markdown 报告。

输出字段：

```text
name
one_sentence_summary
main_features
technical_highlights
learning_value
recommended_for
possible_use_cases
stars
url
```

---

### 6.3 News 模块

功能：

1. 从 RSS / Atom feed 获取 AI 新闻。
2. 支持多新闻源配置。
3. 每个新闻源限制采集数量。
4. 筛选重要新闻。
5. 生成结构化中英文总结。
6. 写入每日 Markdown 报告。

输出字段：

```text
title
source
one_sentence_summary
what_happened
why_it_matters
impact
related_technologies
url
```

---

### 6.4 日报生成

功能：

1. 生成英文日报。
2. 生成中文日报。
3. 按日期保存到 `outputs/`。
4. 文件名格式为 `daily_ai_report_YYYY-MM-DD.md`。

---

### 6.5 数据库持久化

功能：

1. 使用 PostgreSQL 保存运行记录。
2. 保存每日报告。
3. 保存入选论文、新闻和 GitHub 项目。
4. 保存报告和入选内容之间的关系。

核心表：

```text
runs
reports
articles
news
github_repositories
report_items
```

---

### 6.6 前端 Dashboard

MVP 包含两个前端阶段：

```text
1. 旧静态 Dashboard
2. React Dashboard 框架
```

旧静态 Dashboard：

```text
frontend/
```

React Dashboard：

```text
frontend-react/
```

React 当前阶段先使用 mock data，后续版本接入 FastAPI。

---

## 7. MVP 不做什么

MVP 暂时不做：

1. 用户登录
2. 收藏、书签和提醒
3. 邮件推送
4. Notion 集成
5. 完整评分系统
6. 向量搜索
7. 多用户权限
8. FastAPI 数据接口
9. React 直接读取数据库
10. 自动部署到生产环境

---

## 8. 验收标准

MVP 完成后应满足：

1. 可以运行 `main.py` 生成每日 AI 报告。
2. 报告中包含论文、GitHub 项目和新闻。
3. 英文和中文报告都能生成。
4. GitHub token 配置后可以正常搜索项目。
5. OpenAI API key 配置后可以生成 LLM 总结。
6. PostgreSQL 配置后可以写入数据库。
7. 数据库中可以看到 `runs`、`reports`、`articles`、`news`、`github_repositories`、`report_items` 数据。
8. 静态 Dashboard 可以展示历史报告数据。
9. React Dashboard 可以启动和构建。
10. 单元测试通过。

---

## 9. 后续版本方向

MVP 之后建议优先开发：

1. FastAPI 后端 API。
2. React 前端接入 API。
3. 评分系统。
4. Docker Compose 多服务部署。
5. 用户偏好、收藏和提醒。
