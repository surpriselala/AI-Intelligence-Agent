# MVP Release Notes

## 1. Release Summary

MVP 版本完成了 AI Intelligence Agent 的基础可运行链路。

用户现在可以运行 Agent，自动生成每日 AI 技术情报报告，并将结果保存到本地文件和 PostgreSQL 数据库。

---

## 2. User-facing Changes

### 2.1 每日 AI 报告

新增每日 Markdown 报告生成能力。

报告包含：

1. Research Papers
2. GitHub Projects
3. Industry News
4. 中文版本报告

---

### 2.2 GitHub 项目追踪

新增 GitHub AI 项目搜索、筛选和总结。

---

### 2.3 AI 新闻追踪

新增 RSS 新闻源采集和总结。

---

### 2.4 Dashboard

新增基础 Dashboard：

```text
frontend/
```

新增 React Dashboard 框架：

```text
frontend-react/
```

---

### 2.5 数据库持久化

新增 PostgreSQL 持久化能力。

保存内容：

1. 运行记录
2. 每日报告
3. 入选论文
4. 入选新闻
5. 入选 GitHub 项目
6. 报告与内容的关联关系

---

## 3. Technical Changes

新增模块：

```text
tools/news_tool.py
tools/github_tool.py
tools/dashboard_data_tool.py
agents/news_agent.py
agents/github_agent.py
database/
frontend-react/
```

新增配置：

```text
GITHUB_TOKEN
OPENAI_API_KEY
DATABASE_URL
NEWS_FEEDS
```

---

## 4. Run Commands

本地运行：

```bash
.venv/bin/python main.py
```

Docker 运行：

```bash
docker compose up -d
docker compose logs
```

React 前端：

```bash
cd frontend-react
npm install
npm run dev
```

---

## 5. Known Limitations

1. React 前端暂时使用 mock data。
2. 当前没有 FastAPI。
3. 当前没有真实评分系统。
4. Dashboard 数据源仍然处于过渡阶段。
5. Docker Compose 还没有完整拆分多服务。
6. 旧静态前端仍保留。

---

## 6. Next Version

推荐下一版本：

```text
v0.2-fastapi-api
```

主要目标：

```text
新增 FastAPI，从 PostgreSQL 提供 Dashboard 和列表 API。
```
