# v0.2 FastAPI API Development Report

## 1. Version

```text
v0.2-fastapi-api
```

---

## 2. Version Background

MVP 已经完成：

```text
1. Agent 采集论文、GitHub 项目和新闻
2. LLM 筛选和总结
3. Markdown 日报生成
4. PostgreSQL 持久化
5. React 前端框架
```

当前缺口：

```text
React 前端仍然使用 mock data
前端还不能从 PostgreSQL 获取真实数据
项目还没有 FastAPI API 层
```

因此 v0.2 的目标是新增 FastAPI 后端，让数据库中的日报、文章、新闻和 GitHub 项目可以通过 HTTP API 查询。

---

## 3. Development Goal

本版本目标：

```text
新增 FastAPI 后端 API
从 PostgreSQL 读取当前 MVP 数据
先用浏览器 / curl 验证 API
暂时不让 React 前端接入 API
```

最终数据流目标：

```text
main.py
  ↓
PostgreSQL
  ↓
FastAPI
  ↓
React frontend
```

v0.2 只完成中间两层：

```text
PostgreSQL
  ↓
FastAPI
```

当前实现状态：

```text
Completed
```

已完成：

1. FastAPI app 已创建。
2. `/health` 已实现。
3. `/api/dashboard` 已实现。
4. `/api/articles` 已实现。
5. `/api/news` 已实现。
6. `/api/github-projects` 已实现。
7. `/api/reports` 已实现。
8. `/api/reports/{report_date}` 已实现。
9. API 单元测试已添加。
10. 已用真实 PostgreSQL 数据进行手动验证。

---

## 4. Scope

### 4.1 In Scope

本版本要做：

1. 新增 `api/` 目录。
2. 新增 FastAPI app。
3. 新增数据库 session dependency。
4. 新增 Pydantic response schemas。
5. 新增 `/health` 接口。
6. 新增 `/api/dashboard` 接口。
7. 新增 `/api/articles` 分页接口。
8. 新增 `/api/news` 分页接口。
9. 新增 `/api/github-projects` 分页接口。
10. 新增 `/api/reports` 和 `/api/reports/{report_date}` 接口。
11. 新增 API 测试。
12. 更新 requirements。

### 4.2 Out of Scope

本版本暂时不做：

1. React 前端接入 API。
2. 删除 mock data。
3. 用户登录。
4. 收藏、书签、提醒。
5. 真实评分系统。
6. WebSocket 实时推送。
7. 生产部署。
8. Docker Compose 多服务拆分。
9. Alembic 数据库迁移。

---

## 5. Recommended Project Structure

新增：

```text
api/
├── __init__.py
├── main.py
├── deps.py
├── schemas.py
└── routes/
    ├── __init__.py
    ├── dashboard.py
    ├── articles.py
    ├── news.py
    ├── github.py
    └── reports.py
```

测试：

```text
tests/test_api_health.py
tests/test_api_dashboard.py
tests/test_api_lists.py
```

实际实现文件：

```text
api/__init__.py
api/main.py
api/deps.py
api/schemas.py
api/routes/__init__.py
api/routes/items.py
api/routes/dashboard.py
api/routes/articles.py
api/routes/news.py
api/routes/github.py
api/routes/reports.py
tests/test_api.py
requirements.txt
```

---

## 6. Dependencies

需要新增 Python 依赖：

```text
fastapi
uvicorn
pydantic
```

说明：

1. FastAPI 用于提供 HTTP API。
2. Uvicorn 用于本地启动 API 服务。
3. Pydantic 用于定义响应结构。

启动命令：

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7. API Design

### 7.1 Health Check

```text
GET /health
```

返回：

```json
{
  "status": "ok"
}
```

用途：

1. 验证 FastAPI 服务启动。
2. 给 Docker / 部署健康检查预留接口。

---

### 7.2 Dashboard

```text
GET /api/dashboard
```

目标：

返回最新日报对应的 Dashboard 数据。

查询策略：

```text
1. 查询最新 reports 记录
2. 根据 report_id 查询 report_items
3. 根据 item_type 读取 articles / news / github_repositories
4. 每类最多返回 4 条
5. 统计 totals
```

返回示例：

```json
{
  "generated_at": "2026-06-14",
  "totals": {
    "articles": 5,
    "news": 3,
    "projects": 5,
    "reports": 1,
    "stars": 633146
  },
  "dashboard": {
    "articles": [],
    "news": [],
    "projects": []
  }
}
```

---

### 7.3 Articles List

```text
GET /api/articles?page=1&page_size=10&query=&topic=
```

返回：

```json
{
  "items": [],
  "page": 1,
  "page_size": 10,
  "total": 42,
  "total_pages": 5
}
```

排序规则：

```text
report_date DESC
rank ASC
```

后续评分系统完成后改为：

```text
score_snapshot DESC
report_date DESC
rank ASC
```

---

### 7.4 News List

```text
GET /api/news?page=1&page_size=10&query=&topic=
```

返回结构同 Articles。

---

### 7.5 GitHub Projects List

```text
GET /api/github-projects?page=1&page_size=10&query=&topic=
```

返回结构同 Articles。

GitHub item 需要额外返回：

```text
stars
language
topics
full_name
```

---

### 7.6 Reports

```text
GET /api/reports
GET /api/reports/{report_date}
```

`GET /api/reports` 返回报告列表：

```json
{
  "items": [
    {
      "report_date": "2026-06-14",
      "title": "Daily AI Intelligence Report - 2026-06-14",
      "output_path": "outputs/daily_ai_report_2026-06-14.md"
    }
  ]
}
```

`GET /api/reports/{report_date}` 返回完整 Markdown：

```json
{
  "report_date": "2026-06-14",
  "title": "Daily AI Intelligence Report - 2026-06-14",
  "content_markdown": "# Daily AI Intelligence Report..."
}
```

---

## 8. Data Mapping

### 8.1 Shared Frontend Item Shape

API 返回给 React 的 item 建议对齐当前前端类型：

```ts
interface DashboardItem {
  id: string;
  type: "articles" | "news" | "projects";
  title: string;
  summary: string;
  url: string;
  date: string;
  source?: string;
  stars?: number;
  language?: string;
  tags?: string[];
  score?: number;
  order?: number;
}
```

这样 v0.3 React 接入 API 时，`dashboardApi.ts` 可以最小改动。

---

### 8.2 Article Mapping

来源表：

```text
articles
report_items
reports
```

字段映射：

| API Field | Source |
|---|---|
| id | articles.id |
| type | "articles" |
| title | articles.title |
| summary | articles.summary_data.one_sentence_summary |
| url | articles.url |
| date | reports.report_date |
| tags | articles.tags |
| score | report_items.score_snapshot |
| order | report_items.rank |

---

### 8.3 News Mapping

来源表：

```text
news
report_items
reports
```

字段映射：

| API Field | Source |
|---|---|
| id | news.id |
| type | "news" |
| title | news.title |
| summary | news.summary_data.one_sentence_summary |
| url | news.url |
| source | news.source |
| date | reports.report_date |
| tags | news.tags |
| score | report_items.score_snapshot |
| order | report_items.rank |

---

### 8.4 GitHub Mapping

来源表：

```text
github_repositories
report_items
reports
```

字段映射：

| API Field | Source |
|---|---|
| id | github_repositories.id |
| type | "projects" |
| title | github_repositories.full_name |
| summary | github_repositories.summary_data.one_sentence_summary |
| url | github_repositories.url |
| stars | github_repositories.stars |
| language | github_repositories.language |
| tags | github_repositories.tags |
| date | reports.report_date |
| score | report_items.score_snapshot |
| order | report_items.rank |

---

## 9. Database Query Strategy

### 9.1 Dashboard Query

Dashboard 应该以最新 `reports` 为入口，而不是直接查询所有 articles/news/github。

原因：

```text
Dashboard 展示的是“最新日报选中的内容”
不是数据库中所有历史内容
```

### 9.2 List Query

列表页应该以 `report_items` 为入口。

原因：

```text
列表页展示的是“历史日报中出现过的内容”
不是所有采集候选项
```

### 9.3 Pagination

分页参数：

```text
page: int = 1
page_size: int = 10
```

限制：

```text
page_size 最大 50
默认 10
```

---

## 10. Error Handling

推荐错误返回：

### 10.1 Database Not Configured

```json
{
  "detail": "DATABASE_URL is not configured"
}
```

### 10.2 Report Not Found

```json
{
  "detail": "Report not found"
}
```

### 10.3 Invalid Pagination

```json
{
  "detail": "page must be greater than 0"
}
```

---

## 11. CORS

本地开发需要允许 React dev server：

```text
http://127.0.0.1:5173
http://localhost:5173
```

FastAPI 中建议配置：

```python
CORSMiddleware
```

---

## 12. Tests

### 12.1 Unit Tests

需要测试：

1. `/health`
2. `/api/dashboard`
3. `/api/articles`
4. `/api/news`
5. `/api/github-projects`
6. `/api/reports`
7. `/api/reports/{report_date}`

### 12.2 Test Database

优先使用 SQLite 内存库测试 API 查询逻辑。

注意：

```text
如果使用 PostgreSQL JSONB 特性，测试时需要避免写死 Postgres-only 查询。
```

### 12.3 Manual Verification

本地启动：

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

检查：

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/dashboard
curl "http://127.0.0.1:8000/api/articles?page=1&page_size=10"
curl "http://127.0.0.1:8000/api/news?page=1&page_size=10"
curl "http://127.0.0.1:8000/api/github-projects?page=1&page_size=10"
```

实际测试记录：

```bash
.venv/bin/python -m unittest discover -s tests
```

结果：

```text
Ran 68 tests
OK
```

实际手动验证命令：

```bash
.venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/dashboard
curl -s "http://127.0.0.1:8000/api/articles?page=1&page_size=2"
curl -s http://127.0.0.1:8000/api/reports
```

实际验证结果：

```text
/health returned {"status":"ok"}
/api/dashboard returned latest 2026-06-14 report data
/api/articles returned paginated article data
/api/reports returned report metadata
```

---

## 13. Acceptance Criteria

v0.2 完成后应满足：

1. `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000` 可以启动。
2. `/health` 返回 `{"status": "ok"}`。
3. FastAPI 可以连接现有 PostgreSQL。
4. `/api/dashboard` 可以返回最新日报数据。
5. `/api/articles` 支持分页。
6. `/api/news` 支持分页。
7. `/api/github-projects` 支持分页。
8. `/api/reports` 可以返回报告列表。
9. `/api/reports/{report_date}` 可以返回完整 Markdown。
10. API 测试通过。
11. 现有 `main.py` 日报生成不受影响。
12. React 前端仍可通过 `npm run dev` 独立运行。

---

## 14. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| 数据库为空 | API 返回空数据，前端无法验证真实内容 | 先运行一次 `main.py` 写入数据 |
| 查询逻辑过早复杂化 | 开发速度下降 | 第一版只查 report_items 中已入选内容 |
| React 接入提前发生 | v0.2 范围膨胀 | React 接入放到 v0.3 |
| Docker 多服务提前改造 | 部署复杂度上升 | v0.2 只做本地 FastAPI |
| SQLite 测试和 PostgreSQL 行为差异 | 测试遗漏数据库问题 | 核心 SQLAlchemy 查询保持简单 |

---

## 15. Implementation Order

推荐实现顺序：

```text
Step 1: requirements.txt 增加 fastapi / uvicorn / pydantic
Step 2: 新建 api/main.py 和 /health
Step 3: 新建 api/deps.py，复用 database/db.py
Step 4: 新建 api/schemas.py
Step 5: 实现 reports API
Step 6: 实现 dashboard API
Step 7: 实现 articles/news/github list API
Step 8: 增加 CORS
Step 9: 增加测试
Step 10: 本地 uvicorn 手动验证
```

---

## 16. Next Version

v0.2 完成后，下一版本建议：

```text
v0.3-react-api-integration
```

目标：

```text
把 frontend-react/src/api/dashboardApi.ts 从 mock data 切换为 FastAPI fetch。
```
