# MVP Development Report

## 1. 版本概览

版本名称：

```text
MVP
```

版本目标：

```text
完成 AI Intelligence Agent 的基础工作流，从采集、筛选、总结、报告生成到数据库持久化和基础 Dashboard 展示。
```

---

## 2. 已完成功能

### 2.1 论文采集与总结

相关文件：

```text
tools/arxiv_tool.py
agents/paper_agent.py
prompts/paper_selection_prompt.txt
prompts/paper_summary_prompt.txt
docs/versions/mvp/development_notes/article_fetching_development.md
docs/versions/mvp/development_notes/paper_summary_development.md
```

完成内容：

1. 支持从 arXiv 搜索 AI 相关论文。
2. 支持关键词 fallback 筛选。
3. 支持 OpenAI LLM 筛选。
4. 支持结构化论文总结。
5. 支持中文总结。

---

### 2.2 GitHub 项目采集与总结

相关文件：

```text
tools/github_tool.py
agents/github_agent.py
prompts/github_selection_prompt.txt
prompts/github_summary_prompt.txt
docs/versions/mvp/development_notes/github_development.md
```

完成内容：

1. 支持 GitHub repository search。
2. 支持从 `.env` 读取 `GITHUB_TOKEN`。
3. 支持 README 摘要上下文。
4. 支持项目筛选和结构化总结。
5. 支持中文字段生成。

---

### 2.3 新闻采集与总结

相关文件：

```text
tools/news_tool.py
agents/news_agent.py
prompts/news_selection_prompt.txt
prompts/news_summary_prompt.txt
docs/versions/mvp/development_notes/news_development.md
```

完成内容：

1. 支持 RSS / Atom feed。
2. 支持多个新闻源。
3. 支持每个新闻源限制采集数量。
4. 支持新闻筛选。
5. 支持新闻中英文结构化总结。

---

### 2.4 每日报告生成

相关文件：

```text
agents/report_agent.py
main.py
outputs/
```

完成内容：

1. 生成英文日报。
2. 生成中文日报。
3. 按日期保存 Markdown 文件。
4. 报告包含论文、GitHub 项目和新闻三部分。

---

### 2.5 Dashboard 数据生成

相关文件：

```text
tools/dashboard_data_tool.py
frontend/data/dashboard_data.js
```

完成内容：

1. 从历史 Markdown 报告解析 Dashboard 数据。
2. 生成 `window.AI_DASHBOARD_DATA`。
3. 支持历史内容聚合。
4. 支持 Dashboard 每类展示 4 条。
5. 支持列表页每页 10 条。

---

### 2.6 静态前端 Dashboard

相关文件：

```text
frontend/index.html
frontend/styles.css
frontend/app.js
```

完成内容：

1. 支持 Dashboard 首页。
2. 支持 Articles / News / GitHub Projects 页面。
3. 支持搜索。
4. 支持分页。
5. 支持固定侧边栏和主体滚动。

---

### 2.7 PostgreSQL 数据库持久化

相关文件：

```text
DATABASE_DESIGN.md
database/db.py
database/models.py
database/repository.py
tests/test_database_repository.py
```

完成内容：

1. 支持读取 `DATABASE_URL`。
2. 支持 SQLAlchemy 建表。
3. 支持保存运行记录。
4. 支持保存每日报告。
5. 支持保存入选 articles / news / github repositories。
6. 支持 `report_items` 保存日报和内容的关联。
7. 重复运行同一天报告不会无限插入重复 report。

已验证数据库写入：

```text
runs: 1
reports: 1
articles: 5
news: 3
github_repositories: 5
report_items: 13
```

---

### 2.8 Docker 打包

相关文件：

```text
Dockerfile
docker-compose.yml
.dockerignore
```

完成内容：

1. 支持 Docker build。
2. 支持 `docker compose up` 运行一次日报生成。
3. 支持 `.env` 注入环境变量。
4. 支持挂载 `outputs/` 和 `frontend/data/`。

说明：

```text
当前容器不是常驻服务，而是执行一次 python main.py 后退出。
```

---

### 2.9 React 前端框架

相关文件：

```text
frontend-react/
docs/versions/mvp/development_notes/frontend_backend_optimization.md
docs/versions/mvp/development_notes/frontend_react_revision_report.md
```

完成内容：

1. 使用 React + Vite + TypeScript。
2. 支持组件化结构。
3. 支持 React Router。
4. 支持 Dashboard / Articles / News / GitHub Projects 路由。
5. 搜索和主题筛选状态已分离。
6. Dashboard 卡片间距已优化。
7. 当前使用 mock data。
8. 后续版本接入 FastAPI。

---

## 3. 当前运行方式

### 3.1 本地运行 Agent

```bash
.venv/bin/python main.py
```

运行结果：

```text
outputs/daily_ai_report_YYYY-MM-DD.md
frontend/data/dashboard_data.js
PostgreSQL database records
```

### 3.2 Docker 运行 Agent

```bash
docker compose up -d
docker compose logs
```

### 3.3 React 前端运行

```bash
cd frontend-react
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173/
```

---

## 4. 验证记录

Python 测试：

```text
Ran 64 tests
OK
```

React 构建：

```text
npm run build
success
```

npm 安全检查：

```text
npm audit --audit-level=high
found 0 vulnerabilities
```

React 路由检查：

```text
/                  200
/articles          200
/news              200
/github-projects   200
```

---

## 5. MVP 技术债

当前仍然存在的技术债：

1. React 前端仍使用 mock data。
2. 还没有 FastAPI 后端。
3. 前端尚未直接读取 PostgreSQL。
4. 评分字段存在，但评分系统尚未实现。
5. Docker Compose 还没有拆分 agent / api / frontend / postgres。
6. 旧静态前端和新 React 前端并存。
7. 数据库迁移工具 Alembic 尚未接入。

---

## 6. 后续建议

下一版本建议做：

```text
v0.2-fastapi-api
```

目标：

1. 新增 FastAPI。
2. 从 PostgreSQL 查询 Dashboard 数据。
3. 提供 `/api/dashboard`。
4. 提供分页列表 API。
5. 暂时不替换 React mock data，先独立验证 API。
