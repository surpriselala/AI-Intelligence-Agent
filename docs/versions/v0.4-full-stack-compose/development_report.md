# v0.4 Full Stack Docker Compose Development Report

## 1. Version

```text
v0.4-full-stack-compose
```

---

## 2. Version Background

v0.3 已经完成：

```text
PostgreSQL -> FastAPI -> React
```

当前本地开发运行方式是：

```text
FastAPI: .venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
React:   cd frontend-react && npm run dev
Agent:   .venv/bin/python main.py
DB:      本机 PostgreSQL
```

当前 Docker Compose 状态：

```text
docker-compose.yml
  ai-intelligence-agent:
    command: python main.py
```

也就是说，Docker 目前只覆盖了“运行一次 Agent 生成报告”的场景，还没有覆盖完整服务：

1. PostgreSQL 数据库服务
2. FastAPI 后端服务
3. React 前端服务
4. Agent 报告生成任务

v0.4 的目标是把这些服务统一纳入 Docker Compose，让项目进入“一条命令启动完整系统”的阶段。

---

## 3. Development Goal

本版本目标：

```text
docker compose up
  -> postgres
  -> api
  -> frontend

docker compose run agent
  -> generate daily report
  -> write PostgreSQL
```

完成后，本地开发和演示的默认入口应变成：

```text
Frontend: http://localhost:5173 或 http://localhost:8080
API:      http://localhost:8000
DB:       postgres service
```

核心目标：

1. 使用 Docker Compose 启动 PostgreSQL。
2. 使用 Docker Compose 启动 FastAPI。
3. 使用 Docker Compose 启动 React 前端。
4. 保留 Agent 作为可手动运行的一次性任务。
5. 统一容器内服务之间的 `DATABASE_URL`。
6. 避免前端继续依赖本机 `.venv` 后端。
7. 保持 `.env` 不提交真实密钥。

---

## 4. Scope

### 4.1 In Scope

本版本要做：

1. 重构 `docker-compose.yml`。
2. 增加 PostgreSQL service。
3. 增加 FastAPI service。
4. 增加 React frontend service。
5. 调整现有 Python Dockerfile，支持 `api` 和 `agent` 两种命令。
6. 为 React 增加 Dockerfile 或 Compose build 配置。
7. 增加 `.env.example` 或补齐现有环境变量说明。
8. 更新 README 的 Docker 启动方式。
9. 增加 Docker 运行验证记录。

### 4.2 Out of Scope

本版本暂时不做：

1. 生产级 Nginx 反向代理。
2. HTTPS。
3. 用户登录和权限。
4. Celery / APScheduler 定时任务。
5. 云部署。
6. 多环境 CI/CD。
7. 数据库迁移工具 Alembic。
8. 评分系统。

这些可以放到后续版本：

```text
v0.5-scoring-system
v0.6-production-deployment
v0.7-scheduler
```

---

## 5. Target Architecture

### 5.1 Service Layout

推荐 Compose 服务：

```text
postgres
  PostgreSQL database

api
  FastAPI backend
  depends_on postgres
  exposes 8000

frontend
  React frontend
  depends_on api
  exposes 5173 for dev mode

agent
  one-off report generation task
  depends_on postgres
  command: python main.py
```

### 5.2 Runtime Flow

Dashboard 查看流程：

```text
Browser
  -> frontend container
  -> api container
  -> postgres container
```

报告生成流程：

```text
docker compose run --rm agent
  -> fetch papers/news/github
  -> LLM summaries
  -> markdown report
  -> write postgres
```

---

## 6. Compose Design

### 6.1 Recommended Services

目标 `docker-compose.yml` 结构：

```yaml
services:
  postgres:
    image: postgres:16
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-ai_research_agent}
      POSTGRES_USER: ${POSTGRES_USER:-aiden}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      TZ: Asia/Shanghai
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend-react
      dockerfile: Dockerfile
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    depends_on:
      - api
    ports:
      - "5173:5173"

  agent:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      TZ: Asia/Shanghai
    depends_on:
      - postgres
    volumes:
      - ./outputs:/app/outputs
    command: python main.py

volumes:
  postgres_data:
```

实际实现时需要注意：

1. Compose 变量替换来自项目根目录 `.env`。
2. 不要把真实 `.env` 提交到 git。
3. `DATABASE_URL` 在容器内不能继续使用 `localhost` 指向数据库。
4. 容器内访问 PostgreSQL 应使用 service name：`postgres`。

---

## 7. Dockerfile Design

### 7.1 Python Dockerfile

现有 `Dockerfile` 可以继续作为 Python runtime：

```text
Dockerfile
  used by api
  used by agent
```

建议保留一个 Python Dockerfile，分别通过 Compose command 区分：

```text
api:
  command: uvicorn api.main:app --host 0.0.0.0 --port 8000

agent:
  command: python main.py
```

这样可以避免维护两个几乎相同的 Python 镜像。

### 7.2 Frontend Dockerfile

需要新增：

```text
frontend-react/Dockerfile
```

v0.4 第一版建议使用开发模式：

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
```

原因：

1. 当前还处于本地开发阶段。
2. Vite dev server 方便快速验证。
3. 暂时不引入 Nginx，减少版本复杂度。

后续生产版本再改为：

```text
npm run build
nginx serve dist/
```

---

## 8. Environment Design

### 8.1 Required Variables

根目录 `.env` 应包含：

```env
OPENAI_API_KEY=
GITHUB_TOKEN=

POSTGRES_DB=ai_research_agent
POSTGRES_USER=aiden
POSTGRES_PASSWORD=change_me

OPENAI_PAPER_SELECTION_MODEL=
OPENAI_PAPER_SUMMARY_MODEL=
OPENAI_GITHUB_SELECTION_MODEL=
OPENAI_GITHUB_SUMMARY_MODEL=
OPENAI_NEWS_SELECTION_MODEL=
OPENAI_NEWS_SUMMARY_MODEL=
```

本机运行时可以继续使用：

```env
DATABASE_URL=postgresql+psycopg2://aiden:password@localhost:5432/ai_research_agent
```

Docker Compose 内部应覆盖为：

```env
DATABASE_URL=postgresql+psycopg2://aiden:password@postgres:5432/ai_research_agent
```

### 8.2 Frontend API URL

React 容器需要：

```env
VITE_API_BASE_URL=http://localhost:8000
```

注意：

浏览器运行在宿主机，不是在 frontend 容器里。因此前端请求 API 时应使用宿主机可访问地址：

```text
http://localhost:8000
```

不是：

```text
http://api:8000
```

`api:8000` 只适合容器之间通信，浏览器无法直接解析。

---

## 9. Database Initialization

当前项目通过 SQLAlchemy `Base.metadata.create_all` 创建表。

v0.4 第一版可继续使用应用初始化逻辑，不引入 Alembic。

需要确认：

1. `api` 启动时是否会初始化数据库表。
2. 如果不会，需要在 api startup 或 agent run 前调用 `init_database()`。
3. `agent` 写入前必须确保表已存在。

推荐策略：

```text
api startup:
  init_database()

agent startup:
  init_database()
```

这样即使用户只运行：

```bash
docker compose up api frontend postgres
```

或：

```bash
docker compose run --rm agent
```

都不会因为表不存在而失败。

---

## 10. Command Design

### 10.1 Start Full Stack

目标命令：

```bash
docker compose up --build
```

启动：

```text
postgres
api
frontend
```

### 10.2 Run Agent Once

目标命令：

```bash
docker compose run --rm agent
```

生成：

```text
outputs/daily_ai_report_YYYY-MM-DD.md
database records
```

### 10.3 Check Logs

```bash
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f postgres
```

### 10.4 Stop Services

```bash
docker compose down
```

保留数据库 volume：

```bash
docker compose down
```

删除数据库 volume：

```bash
docker compose down -v
```

---

## 11. File Change Plan

预计修改或新增：

```text
docker-compose.yml
Dockerfile
.dockerignore
.env.example
README.md
api/main.py
database/db.py
frontend-react/Dockerfile
frontend-react/.dockerignore
frontend-react/.env.example
docs/versions/v0.4-full-stack-compose/development_report.md
```

可能需要修改：

```text
config.py
main.py
```

修改原因：

1. 让 Docker 内部数据库 URL 更稳定。
2. 确认 app 启动时初始化数据库。
3. 避免 frontend build context 带入 `node_modules` 和 `dist`。

---

## 12. Acceptance Criteria

v0.4 完成后应满足：

1. `docker compose up --build` 可以启动 `postgres`、`api`、`frontend`。
2. 浏览器访问前端页面成功。
3. 前端可以请求 Docker 启动的 FastAPI。
4. FastAPI 可以连接 Docker 启动的 PostgreSQL。
5. `docker compose run --rm agent` 可以生成报告并写入 PostgreSQL。
6. 前端刷新后可以看到 agent 写入的新数据。
7. 关闭本机 `.venv` FastAPI 后，前端仍然可用。
8. 不需要本机 PostgreSQL 也可以运行完整系统。
9. `.env.example` 不包含真实密钥。
10. `npm run build` 仍然通过。
11. Python 单元测试仍然通过。

---

## 13. Test Plan

### 13.1 Build Images

```bash
docker compose build
```

### 13.2 Start Services

```bash
docker compose up
```

检查：

```bash
docker compose ps
```

应看到：

```text
postgres   running
api        running
frontend   running
```

### 13.3 API Health

```bash
curl http://localhost:8000/health
```

应返回：

```json
{"status":"ok"}
```

### 13.4 Frontend

浏览器打开：

```text
http://localhost:5173
```

检查：

1. Dashboard 页面可打开。
2. Network 面板看到 `/api/dashboard`。
3. Articles / News / GitHub Projects 路由可打开。
4. 搜索和主题筛选仍然可用。

### 13.5 Agent

```bash
docker compose run --rm agent
```

检查：

1. `outputs/` 中生成新报告。
2. PostgreSQL 中新增 report 记录。
3. 前端刷新后展示最新数据。

### 13.6 Local Backend Shutdown Test

确保本机没有 `.venv` uvicorn：

```bash
lsof -i :8000
```

然后只通过 Docker Compose 启动 API。

这个测试用于确认前端不是误连本机后端。

---

## 14. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| 容器内 `DATABASE_URL` 仍使用 localhost | API/Agent 无法连接数据库 | Compose 中覆盖为 `postgres` service name |
| 前端请求 `api:8000` | 浏览器无法解析 | `VITE_API_BASE_URL` 使用 `http://localhost:8000` |
| PostgreSQL 启动慢于 API | API 启动时报错 | 增加 healthcheck 或应用层重试 |
| 数据库表未初始化 | API 查询失败 | api/agent 启动前调用 `init_database()` |
| 真实密钥写入文档或示例 | 安全风险 | `.env.example` 只放空值或占位值 |
| Vite dev server 用于生产 | 不适合正式部署 | v0.4 只定义为本地完整编排 |
| Docker volume 中旧数据影响测试 | 数据不符合预期 | 必要时使用 `docker compose down -v` 重置 |

---

## 15. Implementation Order

推荐实现顺序：

```text
Step 1: 新增 frontend-react/Dockerfile
Step 2: 新增 frontend-react/.dockerignore
Step 3: 补齐根目录 .env.example
Step 4: 重构 docker-compose.yml，增加 postgres/api/frontend/agent
Step 5: 确认 api/agent 启动前初始化数据库
Step 6: 启动 docker compose build
Step 7: 启动 docker compose up 验证 postgres/api/frontend
Step 8: 停止本机 uvicorn，确认前端仍从 Docker API 取数据
Step 9: docker compose run --rm agent 生成新报告
Step 10: 更新 README Docker 运行说明
Step 11: 补充 release_notes.md 和 test_report.md
```

---

## 16. Open Questions

实现前需要确认：

1. v0.4 是否继续使用 Vite dev server，还是直接用 Nginx serve React build？
2. PostgreSQL 是否完全迁入 Docker，还是继续兼容宿主机 PostgreSQL？
3. Agent 是否只保留手动运行，还是需要 Docker Compose 启动时自动跑一次？
4. 是否需要数据库 healthcheck 和 API 启动等待逻辑？

建议 v0.4 第一版选择：

```text
Vite dev server
Docker PostgreSQL
Agent 手动运行
增加 PostgreSQL healthcheck
```

这样范围最稳，也最符合当前开发阶段。

---

## 17. Outgoing State

v0.4 完成后，项目运行形态应变为：

```text
docker compose up
  full local dashboard stack

docker compose run --rm agent
  generate and persist new report
```

下一版本可以进入：

```text
v0.5-scoring-system
```

或：

```text
v0.5-production-frontend
```

取决于下一阶段优先级。
