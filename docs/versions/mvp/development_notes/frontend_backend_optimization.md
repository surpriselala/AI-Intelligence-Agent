# Frontend + Backend Optimization Document

本文档用于规划 AI Intelligence Agent 的前端和后端优化方向。

当前系统已经完成：

```text
1. 每日采集 AI 论文、新闻和 GitHub 项目
2. 使用 LLM 进行筛选和中英文总结
3. 生成 Markdown 日报
4. 生成 frontend/data/dashboard_data.js
5. 使用静态 HTML/CSS/JavaScript Dashboard 展示数据
6. 将日报和入选内容写入 PostgreSQL
```

下一阶段目标是：

```text
把当前静态前端升级为 React 应用
把当前 dashboard_data.js 数据源升级为 FastAPI + PostgreSQL
让前端可以从数据库动态读取报告、文章、新闻和 GitHub 项目
```

---

## 1. 当前问题

### 1.1 前端仍然是静态数据展示

当前前端数据来自：

```text
frontend/data/dashboard_data.js
```

它由 `tools/dashboard_data_tool.py` 从 Markdown 报告中解析生成。

这个方案适合 MVP，但有几个限制：

1. 前端只能展示已经生成到 JS 文件里的数据。
2. 每次数据更新都需要重新生成 `dashboard_data.js`。
3. 前端无法直接查询数据库。
4. 后续筛选、分页、搜索、排序都会越来越依赖前端本地逻辑。
5. 如果报告数量变多，JS 文件会越来越大。

### 1.2 前端没有使用框架

当前前端由以下文件组成：

```text
frontend/index.html
frontend/styles.css
frontend/app.js
frontend/data/dashboard_data.js
```

这种方式简单直接，但随着页面变多，会出现问题：

1. UI 状态管理会变复杂。
2. 组件复用困难。
3. 页面结构和交互逻辑混在一起。
4. 后续接 API、loading、error、pagination 会更难维护。

考虑到后续 Dashboard 会继续扩展，建议迁移到 React。

### 1.3 后端还没有 API 层

当前项目有数据库，但没有 HTTP API。

数据库写入流程已经完成 Phase 1：

```text
main.py 生成报告
        ↓
写入 reports / articles / news / github_repositories / report_items
```

但前端还不能直接读取这些表。

因此下一阶段需要增加 FastAPI：

```text
React Frontend
        ↓ HTTP JSON API
FastAPI Backend
        ↓ SQLAlchemy
PostgreSQL
```

---

## 2. 优化目标

### 2.1 第一目标：React 化

把当前静态前端迁移为 React 项目。

推荐技术：

```text
React + Vite + TypeScript
```

理由：

1. Vite 启动快，配置轻。
2. React 组件适合 Dashboard 页面拆分。
3. TypeScript 能让 API 数据结构更可靠。
4. 后续接 FastAPI 返回的 JSON 更自然。

### 2.2 第二目标：FastAPI 化

增加后端 API 层，让前端从数据库读取数据。

推荐技术：

```text
FastAPI + SQLAlchemy
```

理由：

1. 项目后端已经是 Python。
2. 当前数据库层已经使用 SQLAlchemy。
3. FastAPI 适合快速提供 JSON API。
4. 后续可以加入 OpenAPI 文档。

### 2.3 第三目标：保留现有可运行链路

优化过程中不要一次性废弃当前静态前端。

推荐策略：

```text
先保留旧 frontend/
新建 frontend-react/
等 React + FastAPI 稳定后再替换
```

这样可以保证任何时候都有一个可用 Dashboard。

---

## 3. 推荐阶段拆分

## Phase 1：搭建 React 前端框架

目标：

```text
先用 React 复刻当前 Dashboard 页面
数据源暂时仍然使用 dashboard_data.js 或静态 mock data
```

本阶段不接数据库，不接 FastAPI。

建议新增目录：

```text
frontend-react/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── styles.css
│   ├── api/
│   │   └── mockData.ts
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   ├── StatCard.tsx
│   │   ├── ContentCard.tsx
│   │   ├── ContentSection.tsx
│   │   └── Pagination.tsx
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── ArticlesPage.tsx
│   │   ├── NewsPage.tsx
│   │   └── GithubPage.tsx
│   └── types/
│       └── dashboard.ts
```

Phase 1 完成标准：

1. React 页面视觉上接近当前 Dashboard。
2. 侧边栏固定高度。
3. 主体内容区域滚动。
4. Dashboard 每类展示 4 条。
5. Articles / News / GitHub 页面每页展示 10 条。
6. 搜索和分页逻辑正常。
7. 旧 `frontend/` 不受影响。

---

## Phase 2：增加 FastAPI 后端框架

目标：

```text
新增 api/ 目录
使用 FastAPI 暴露数据库查询接口
React 暂时可以不接入，先用浏览器或 curl 验证 API
```

建议新增目录：

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

需要新增依赖：

```text
fastapi
uvicorn
pydantic
```

后端启动命令：

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Phase 2 完成标准：

1. FastAPI 可以正常启动。
2. `/health` 返回成功。
3. 可以连接现有 PostgreSQL。
4. 可以读取 `reports`、`articles`、`news`、`github_repositories`、`report_items`。
5. API 不影响现有 `main.py` 生成日报。

---

## Phase 3：设计 API 接口

目标：

```text
让 React 前端可以通过 API 获取 Dashboard 和列表数据
```

### 3.1 Dashboard 接口

```text
GET /api/dashboard
```

返回：

```json
{
  "generated_at": "2026-06-14",
  "totals": {
    "articles": 5,
    "news": 3,
    "projects": 5,
    "reports": 1,
    "stars": 12345
  },
  "dashboard": {
    "articles": [],
    "news": [],
    "projects": []
  }
}
```

说明：

1. Dashboard 每类默认返回 4 条。
2. 当前没有真实评分系统，所以默认按时间排序。
3. 后续评分系统完成后，改为评分优先、时间第二。

### 3.2 Articles 列表接口

```text
GET /api/articles?page=1&page_size=10&query=&sort=latest
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

### 3.3 News 列表接口

```text
GET /api/news?page=1&page_size=10&query=&sort=latest
```

返回格式同 Articles。

### 3.4 GitHub Projects 列表接口

```text
GET /api/github-projects?page=1&page_size=10&query=&sort=latest
```

返回格式同 Articles。

### 3.5 Reports 接口

```text
GET /api/reports
GET /api/reports/{report_date}
```

用途：

1. 展示历史日报列表。
2. 查看某一天完整 Markdown 报告。
3. 后续支持报告详情页。

---

## 4. 数据读取策略

当前数据库中有：

```text
runs
reports
articles
news
github_repositories
report_items
```

推荐 FastAPI 读取方式：

### 4.1 Dashboard

Dashboard 优先从 `report_items` 读取最新报告中的内容。

流程：

```text
1. 找到最新 reports.report_date
2. 查询该 report_id 下的 report_items
3. 根据 item_type 分别 join articles / news / github_repositories
4. 每类取前 4 条
```

原因：

```text
Dashboard 展示的是“日报选中的内容”
不是数据库里所有历史内容
```

### 4.2 列表页

Articles / News / GitHub 页面可以从 `report_items` 聚合历史内容。

推荐第一版：

```text
以 report_items 为入口
按 report_date DESC、rank ASC 排序
分页返回
```

这样可以保证前端展示的是历史日报中真实出现过的内容。

后续如果想展示所有采集过但没入选的内容，再增加候选表或采集缓存。

### 4.3 排序规则

当前没有评分系统，排序规则为：

```text
report_date DESC
rank ASC
```

后续有评分后改为：

```text
score_snapshot DESC
report_date DESC
rank ASC
```

---

## 5. React 数据结构设计

建议前端统一使用以下 TypeScript 类型。

```ts
export type ContentKind = "articles" | "news" | "projects";

export interface DashboardItem {
  id: number;
  type: ContentKind;
  title: string;
  summary: string;
  url: string;
  date: string;
  source?: string;
  stars?: number;
  language?: string;
  tags?: string[];
  score?: number;
}

export interface DashboardPayload {
  generated_at: string;
  totals: {
    articles: number;
    news: number;
    projects: number;
    reports: number;
    stars: number;
  };
  dashboard: {
    articles: DashboardItem[];
    news: DashboardItem[];
    projects: DashboardItem[];
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
```

---

## 6. 前端页面设计

React 版本先复刻当前页面，不做过多功能发散。

### 6.1 Layout

组件：

```text
AppLayout
Sidebar
Topbar
MainContent
```

布局要求：

1. Sidebar 固定高度。
2. Sidebar 不跟随主体内容滚动。
3. 主体内容区域独立滚动。
4. 搜索框在顶部。
5. 页面最大宽度和卡片密度延续当前设计。

### 6.2 DashboardPage

展示：

1. 今日概览。
2. Articles 最新 4 条。
3. News 最新 4 条。
4. GitHub Projects 最新 4 条。
5. 点击 View all 跳转到对应列表页。

### 6.3 Archive Pages

页面：

```text
ArticlesPage
NewsPage
GithubPage
```

共同要求：

1. 每页最多 10 条。
2. 支持搜索。
3. 支持上一页 / 下一页。
4. 当前先按时间排序。
5. 后续支持按评分排序。

---

## 7. Docker 设计

后续会有两个运行方式。

### 7.1 开发环境

开发时建议两个服务分开跑：

```text
FastAPI: http://localhost:8000
React:   http://localhost:5173
```

命令：

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
npm run dev
```

React 使用环境变量：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 7.2 Docker Compose

后续可以把 compose 拆成：

```text
agent      跑每日采集和报告生成
api        跑 FastAPI
frontend   跑 React build 后的静态页面
postgres   可选，数据库服务
```

第一版不一定要马上把 PostgreSQL 放进 compose。当前如果 PostgreSQL 在宿主机，容器里要用：

```env
DATABASE_URL=postgresql+psycopg2://aiden:password@host.docker.internal:5432/ai_research_agent
```

---

## 8. 旧系统与新系统的过渡策略

为了降低风险，推荐保留两套前端一段时间：

```text
frontend/         旧静态 Dashboard
frontend-react/   新 React Dashboard
```

过渡顺序：

1. React 先读取 mock data。
2. React 再读取旧 `dashboard_data.js` 转换出来的 JSON。
3. FastAPI 完成后，React 切换到 API。
4. 确认稳定后，停止维护旧 `frontend/app.js`。
5. 最后再决定是否删除旧 `frontend/`。

这样不会因为新前端开发影响当前日报展示。

---

## 9. 依赖变化

### 9.1 Python 依赖

后端 API 阶段需要新增：

```text
fastapi
uvicorn
pydantic
```

如果后续做数据库迁移，增加：

```text
alembic
```

### 9.2 Node 依赖

React 阶段需要新增：

```text
react
react-dom
vite
typescript
@vitejs/plugin-react
lucide-react
```

是否引入 UI 库暂时不建议。

当前设计已经比较明确，第一版可以先用 CSS modules 或普通 CSS 完成。

---

## 10. 推荐开发顺序

建议按以下顺序做：

```text
Step 1: 新建 frontend-react/
Step 2: 用 React 复刻当前 Dashboard
Step 3: 用 mock data 完成页面状态、搜索、分页
Step 4: 新建 FastAPI api/
Step 5: 实现 /health
Step 6: 实现 /api/dashboard
Step 7: 实现 /api/articles、/api/news、/api/github-projects
Step 8: React 从 FastAPI 拉取数据
Step 9: Docker Compose 增加 api 和 frontend 服务
Step 10: 稳定后再考虑替换旧 frontend/
```

---

## 11. 第一版完成标准

React + FastAPI 第一版完成后，应满足：

1. `frontend-react` 可以独立启动。
2. React 页面视觉和当前 Dashboard 基本一致。
3. FastAPI 可以连接 PostgreSQL。
4. `/api/dashboard` 返回最新日报的三类内容。
5. `/api/articles` 支持分页，每页最多 10 条。
6. `/api/news` 支持分页，每页最多 10 条。
7. `/api/github-projects` 支持分页，每页最多 10 条。
8. React 前端不再依赖 `dashboard_data.js`。
9. 旧 `frontend/` 仍然可以作为 fallback。
10. Docker 环境可以同时运行 agent、api 和 frontend。

---

## 12. 当前不做的事情

为了控制复杂度，本阶段暂时不做：

```text
1. 用户登录
2. 收藏、书签、提醒
3. 复杂权限系统
4. WebSocket 实时推送
5. SSR / Next.js
6. GraphQL
7. 完整后台管理系统
8. 向量搜索
9. 评分系统
10. 多用户偏好推荐
```

这些都可以等 React + FastAPI + PostgreSQL 主链路稳定后再做。

---

## 13. 总结

当前项目已经完成从采集到报告再到数据库持久化的主链路。

下一阶段最合理的优化方向是：

```text
React 负责前端体验
FastAPI 负责数据接口
PostgreSQL 作为真实数据源
main.py 继续负责每日采集和写库
```

推荐先搭 React 框架，再接 FastAPI。不要一开始就同时重写前端、后端、Docker 和数据库查询逻辑。

这样可以让项目平滑从静态 Dashboard 升级为真正的数据库驱动 Web 应用。
