# v0.3 React API Integration Development Report

## 1. Version

```text
v0.3-react-api-integration
```

---

## 2. Version Background

MVP 已经完成：

```text
1. Agent 固定工作流
2. Markdown 日报生成
3. PostgreSQL 持久化
4. React 前端框架
```

v0.2 已经完成：

```text
1. FastAPI app
2. /health
3. /api/dashboard
4. /api/articles
5. /api/news
6. /api/github-projects
7. /api/reports
8. /api/reports/{report_date}
```

当前缺口：

```text
React 前端仍然读取 frontend-react/src/api/mockData.ts
真实数据库数据已经可以通过 FastAPI 查询
但 React 页面还没有调用 FastAPI
```

因此 v0.3 的目标是让 React 前端从 FastAPI 获取真实数据，替代 mock data。

---

## 3. Development Goal

本版本目标：

```text
React frontend
  ↓ fetch
FastAPI
  ↓ SQLAlchemy
PostgreSQL
```

具体目标：

1. React Dashboard 首页读取 `/api/dashboard`。
2. Articles 页面读取 `/api/articles`。
3. News 页面读取 `/api/news`。
4. GitHub Projects 页面读取 `/api/github-projects`。
5. 搜索和主题筛选通过 API query params 传给后端。
6. 分页由后端返回结果，前端不再本地分页完整历史数据。
7. 移除或停止使用 mock data。
8. 前端显示 loading / error / empty states。

---

## 4. Scope

### 4.1 In Scope

本版本要做：

1. 新增前端 API base URL 配置。
2. 修改 `frontend-react/src/api/dashboardApi.ts`。
3. 从 FastAPI 获取 Dashboard 数据。
4. 从 FastAPI 获取 Articles 列表。
5. 从 FastAPI 获取 News 列表。
6. 从 FastAPI 获取 GitHub Projects 列表。
7. 调整 `App.tsx` 中的数据加载逻辑。
8. 保留 React Router。
9. 保留搜索框和主题筛选分离。
10. 加入 loading 和 error 状态。
11. 修改分页逻辑，使用 API 返回的 `page / total_pages / total`。
12. 更新前端文档和运行说明。

### 4.2 Out of Scope

本版本暂时不做：

1. Docker Compose 多服务托管前端和后端。
2. 用户登录。
3. 收藏、书签、提醒。
4. 真实评分系统。
5. WebSocket 实时更新。
6. 后端数据库 schema 修改。
7. Alembic 迁移。
8. 报告详情页 UI。
9. 前端生产部署。

---

## 5. Current Frontend State

当前核心数据文件：

```text
frontend-react/src/api/dashboardApi.ts
frontend-react/src/api/mockData.ts
```

当前数据流：

```text
React App
  ↓
dashboardApi.ts
  ↓
mockData.ts
```

当前问题：

1. 页面展示的是 mock data。
2. 数据不会跟随 PostgreSQL 变化。
3. 搜索和主题筛选在前端本地完成。
4. 分页在前端本地完成。
5. FastAPI 已经可用但前端未使用。

---

## 6. Target Frontend Data Flow

目标数据流：

```text
React App
  ↓
dashboardApi.ts
  ↓
fetch(`${API_BASE_URL}/api/...`)
  ↓
FastAPI
  ↓
PostgreSQL
```

推荐环境变量：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

默认值：

```text
http://127.0.0.1:8000
```

说明：

```text
Vite 前端环境变量必须以 VITE_ 开头。
```

---

## 7. API Contract

v0.3 前端应使用 v0.2 已提供的接口。

### 7.1 Dashboard

```text
GET /api/dashboard
```

用于：

1. 首页 overview totals。
2. 首页 Articles 4 条。
3. 首页 News 4 条。
4. 首页 GitHub Projects 4 条。

---

### 7.2 Articles

```text
GET /api/articles?page=1&page_size=10&query=&topic=
```

用于：

```text
/articles
```

---

### 7.3 News

```text
GET /api/news?page=1&page_size=10&query=&topic=
```

用于：

```text
/news
```

---

### 7.4 GitHub Projects

```text
GET /api/github-projects?page=1&page_size=10&query=&topic=
```

用于：

```text
/github-projects
```

---

## 8. Frontend API Module Design

建议将 `dashboardApi.ts` 改成真正 API client。

建议导出：

```ts
export async function getDashboardData(): Promise<DashboardPayload>

export async function getArticles(params: ListParams): Promise<PaginatedResult<DashboardItem>>

export async function getNews(params: ListParams): Promise<PaginatedResult<DashboardItem>>

export async function getGithubProjects(params: ListParams): Promise<PaginatedResult<DashboardItem>>
```

建议类型：

```ts
export interface ListParams {
  page: number;
  pageSize: number;
  query: string;
  topic: string;
}
```

API base URL：

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
```

错误处理：

```ts
if (!response.ok) {
  throw new Error(`API request failed: ${response.status}`);
}
```

---

## 9. React State Design

当前已有状态：

```ts
searchQuery
activeTopic
pages
```

v0.3 建议新增：

```ts
dashboardData
archiveData
isLoading
errorMessage
```

列表页状态建议按 category 保存：

```ts
Record<ContentKind, PaginatedResult<DashboardItem> | null>
```

数据加载策略：

1. App 启动时加载 `/api/dashboard`。
2. 进入 `/articles` 时加载 `/api/articles`。
3. 进入 `/news` 时加载 `/api/news`。
4. 进入 `/github-projects` 时加载 `/api/github-projects`。
5. `searchQuery` 改变时重新请求当前页面。
6. `activeTopic` 改变时重新请求当前页面。
7. `page` 改变时重新请求当前页面。

---

## 10. Pagination Strategy

当前前端分页：

```text
前端拿完整列表
前端 slice
```

v0.3 目标分页：

```text
前端传 page / page_size
后端返回当前页 items 和 total_pages
```

前端 `Pagination` 组件继续保留，但数据来源改成 API response：

```ts
page={result.page}
total={result.total}
totalPages={result.total_pages}
```

注意：

API 返回字段是 snake_case：

```text
page_size
total_pages
```

前端可以：

1. 保持 snake_case 类型。
2. 或在 api client 中转换为 camelCase。

推荐在 api client 中转换为 camelCase，保持当前 React 类型稳定。

---

## 11. Loading / Error / Empty States

本版本需要补足三个状态：

### 11.1 Loading

接口请求中显示：

```text
Loading latest intelligence...
```

或页面级 loading skeleton。

第一版可以先用简单文字状态。

### 11.2 Error

FastAPI 未启动或请求失败时显示：

```text
Unable to load data from API.
```

同时提示：

```text
Start FastAPI with:
.venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 11.3 Empty

API 返回空 items 时显示：

```text
No matching items found.
```

---

## 12. Development Commands

启动 FastAPI：

```bash
.venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

启动 React：

```bash
cd frontend-react
npm run dev
```

访问：

```text
http://127.0.0.1:5173/
```

---

## 13. Test Plan

### 13.1 Backend Must Be Running

先确认：

```bash
curl http://127.0.0.1:8000/health
```

应返回：

```json
{"status":"ok"}
```

### 13.2 Frontend Build

```bash
cd frontend-react
npm run build
```

### 13.3 Manual Frontend Verification

检查页面：

```text
/
/articles
/news
/github-projects
```

检查行为：

1. 首页数据来自 FastAPI。
2. Articles 列表来自 FastAPI。
3. News 列表来自 FastAPI。
4. GitHub Projects 列表来自 FastAPI。
5. 搜索框不会被主题按钮填充。
6. 主题按钮会触发 API 重新请求。
7. 分页会触发 API 重新请求。
8. FastAPI 停止后，前端显示 error state。

---

## 14. Acceptance Criteria

v0.3 完成后应满足：

1. `mockData.ts` 不再作为页面数据源。
2. Dashboard 首页从 `/api/dashboard` 获取数据。
3. Articles 页面从 `/api/articles` 获取数据。
4. News 页面从 `/api/news` 获取数据。
5. GitHub Projects 页面从 `/api/github-projects` 获取数据。
6. 搜索通过 `query` 参数传给后端。
7. 主题筛选通过 `topic` 参数传给后端。
8. 分页通过 `page` 和 `page_size` 参数传给后端。
9. FastAPI 未启动时，前端有明确错误提示。
10. `npm run build` 通过。
11. Python API 测试仍然通过。
12. React 路由仍然可用。

---

## 15. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| FastAPI 未启动 | 前端无法加载数据 | 增加 error state 和启动提示 |
| CORS 配置错误 | 浏览器无法请求 API | v0.2 已允许 5173，v0.3 再验证 |
| API snake_case 与前端 camelCase 不一致 | 分页数据错误 | api client 中统一转换 |
| 数据库没有数据 | 页面显示空状态 | 先运行 `main.py` 生成并写入报告 |
| 搜索请求太频繁 | 后端请求过多 | 第一版可接受，后续加 debounce |

---

## 16. Implementation Order

推荐实现顺序：

```text
Step 1: 增加 frontend-react/.env.example
Step 2: 修改 dashboardApi.ts，增加 fetch helper
Step 3: 实现 getDashboardData()
Step 4: 实现 getArticles/getNews/getGithubProjects()
Step 5: 调整 App.tsx 数据加载逻辑
Step 6: 调整 ArchivePage 使用 API 分页结果
Step 7: 增加 loading/error state
Step 8: 停止使用 mockData.ts
Step 9: npm run build
Step 10: 启动 FastAPI + React 手动验证
```

---

## 17. Outgoing State

v0.3 完成后，项目状态应变为：

```text
Agent 负责采集和写库
FastAPI 负责从数据库提供数据
React 负责从 FastAPI 展示数据
```

下一版本可进入：

```text
v0.4-scoring-system
```

或：

```text
v0.4-docker-production
```

取决于下一阶段优先级。

---

## 18. Implementation Result

Status:

```text
Implemented
```

Completed changes:

1. `frontend-react/src/api/dashboardApi.ts` 已切换为 FastAPI fetch client。
2. `frontend-react/src/api/mockData.ts` 已删除，页面不再使用静态 mock 数据。
3. `frontend-react/.env.example` 已新增 `VITE_API_BASE_URL` 配置示例。
4. `frontend-react/src/App.tsx` 已改为通过 API 加载 Dashboard 和归档列表数据。
5. `frontend-react/src/pages/ArchivePage.tsx` 已改为使用后端分页结果。
6. `frontend-react/src/types/dashboard.ts` 已移除历史 mock 数据结构，新增列表请求参数类型。
7. `frontend-react/src/styles.css` 已增加 API loading/error 状态样式。
8. `api/routes/dashboard.py` 已支持 `query` 和 `topic` 参数，使首页筛选与归档页一致。
9. `api/main.py` 已允许本机 Vite 开发端口 `5170-5179`，避免 5173 被占用时 CORS 阻塞。

Runtime behavior:

1. Dashboard 首页请求 `/api/dashboard`。
2. Articles 页面请求 `/api/articles?page=...&page_size=10&query=...&topic=...`。
3. News 页面请求 `/api/news?page=...&page_size=10&query=...&topic=...`。
4. GitHub Projects 页面请求 `/api/github-projects?page=...&page_size=10&query=...&topic=...`。
5. 主题按钮只改变 `topic` 参数，不会自动填充搜索框。
6. 搜索框只改变 `query` 参数。
7. 分页由后端返回 `page/page_size/total/total_pages`，前端只负责展示。

Verification:

```bash
cd frontend-react
npm run build
```

Result:

```text
passed
```

```bash
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 68 tests
OK
```

CORS check:

```bash
curl -i -X OPTIONS 'http://127.0.0.1:8000/api/dashboard' \
  -H 'Origin: http://127.0.0.1:5174' \
  -H 'Access-Control-Request-Method: GET'
```

Result:

```text
HTTP/1.1 200 OK
access-control-allow-origin: http://127.0.0.1:5174
```
