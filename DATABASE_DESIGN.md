# AI Intelligence Agent 数据库阶段性设计报告

## 1. 文档目的

本文档用于规划 AI Intelligence Agent 的数据库落地方案。

当前项目已经具备以下能力：

1. 每日采集 AI 论文、新闻和 GitHub 项目。
2. 使用 LLM 对内容进行筛选和中英文总结。
3. 生成 Markdown 日报。
4. 将日报和入选内容写入 PostgreSQL。
5. 使用 React Dashboard 展示前端页面框架。

因此，数据库的第一阶段目标不是重写现有系统，而是增加持久化能力：

```text
现有采集与报告流程继续保留
数据库先作为历史存储层和后续扩展基础
React 前端后续通过 FastAPI 读取数据库
```

---

## 2. 总体判断

数据库是必要的，但不能一次性替换当前架构。

原始设计中提到的 PostgreSQL、SQLAlchemy、Alembic、FastAPI 都是合理方向，但它们不应该在第一阶段同时完成。当前阶段应该避免把数据库、后端 API、前端数据源和评分系统一起重构。

推荐分阶段推进：

| 阶段 | 目标 | 是否现在做 |
|---|---|---|
| Phase 1 | 保存每次日报、入选内容、运行记录 | 是 |
| Phase 2 | 保存更多原始采集数据，减少重复 LLM 调用 | 后续 |
| Phase 3 | 增加评分、标签、趋势统计 | 后续 |
| Phase 4 | 增加 FastAPI，让前端从 API 读取数据 | 后续 |
| Phase 5 | 增加向量检索、问答和用户偏好 | 后续 |

---

## 3. 当前系统与数据库的关系

### 3.1 当前实际流程

当前项目的主流程是：

```text
arXiv / GitHub / RSS
        ↓
tools 层采集数据
        ↓
agents 层筛选与总结
        ↓
report_agent 生成 Markdown 日报
        ↓
写入 PostgreSQL
        ↓
后续 FastAPI / React Dashboard 读取数据库
```

这个流程已经可以运行，所以数据库第一阶段先作为结果持久化层：

```text
生成 Markdown 日报
        ↓
保存日报文件
        ↓
同步写入 PostgreSQL
```

这样做的好处是：

1. 不影响当前可运行的日报生成。
2. 不需要马上完成 FastAPI 数据接口。
3. 数据库失败时，可以先不阻塞整个报告流程。
4. 后续可以逐步把数据库变成主数据源。

### 3.2 第一阶段不做的事情

第一阶段暂时不做：

1. 不把前端改成请求 FastAPI。
2. 不把分页逻辑迁移到后端。
3. 不实现用户登录、收藏、书签和提醒。
4. 不实现完整评分系统。
5. 不实现向量数据库或语义搜索。
6. 不改变现有 Markdown 报告格式。

---

## 4. 数据库选型

第一阶段推荐使用：

```text
PostgreSQL + SQLAlchemy
```

暂时可选：

```text
Alembic
```

后续阶段再加入：

```text
FastAPI + Pydantic
```

### 4.1 PostgreSQL

选择 PostgreSQL 的原因：

1. 已经在本地配置并验证可连接。
2. 支持 JSONB，适合保存 LLM 输出的结构化中英文总结。
3. 后续可以扩展 `pgvector`。
4. 适合长期保存日报、历史项目和趋势数据。

### 4.2 SQLAlchemy

SQLAlchemy 用于：

1. 管理数据库连接。
2. 定义数据模型。
3. 在当前 Python pipeline 中写入数据。

### 4.3 Alembic

Alembic 用于数据库迁移。它适合长期维护，但第一阶段如果想快速落地，可以先用 SQLAlchemy 建表，等表结构稳定后再接入 Alembic。

---

## 5. Phase 1 设计目标

第一阶段只解决四件事：

1. 保存每次运行记录。
2. 保存每日 Markdown 报告。
3. 保存当天报告中入选的 Articles、News、GitHub Projects。
4. 记录日报和入选内容之间的关系。

第一阶段的核心原则：

```text
数据库记录已经生成出来的结果
不反过来驱动当前 pipeline
```

也就是说，当前代码仍然先完成采集、总结和报告生成，然后把最终结果同步进数据库。

---

## 6. Phase 1 核心表

第一阶段建议使用 6 张表：

```text
runs
reports
articles
news
github_repositories
report_items
```

其中：

| 表名 | 作用 |
|---|---|
| runs | 记录每次 Agent 运行状态 |
| reports | 保存每日 Markdown 日报 |
| articles | 保存入选论文或技术文章 |
| news | 保存入选新闻 |
| github_repositories | 保存入选 GitHub 项目 |
| report_items | 记录某一天日报里展示了哪些内容 |

---

## 7. 表结构设计

### 7.1 runs 表

`runs` 表用于记录每次 Agent 执行情况。

```sql
CREATE TABLE runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL DEFAULT 'daily',
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    report_date DATE,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,

    articles_count INTEGER NOT NULL DEFAULT 0,
    news_count INTEGER NOT NULL DEFAULT 0,
    github_count INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,
    metadata JSONB
);
```

说明：

1. `report_date` 对应日报日期。
2. `status` 可使用 `running`、`success`、`failed`。
3. `metadata` 用于保存模型名称、配置快照、运行耗时等补充信息。

---

### 7.2 reports 表

`reports` 表用于保存每日完整 Markdown 日报。这个表应该在第一阶段就实现，因为日报是当前项目最重要的最终产物。

```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),

    report_date DATE NOT NULL UNIQUE,
    title TEXT,
    content_markdown TEXT NOT NULL,
    output_path TEXT,

    dashboard_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

说明：

1. `content_markdown` 保存完整日报内容。
2. `output_path` 保存本地 Markdown 文件路径，例如 `outputs/daily_ai_report_2026-06-12.md`。
3. `dashboard_payload` 可保存当天用于前端展示的结构化数据快照。
4. `report_date` 设置唯一，避免同一天重复插入多个日报。

---

### 7.3 articles 表

`articles` 表用于保存入选日报的论文或技术文章。

当前项目的 Articles 主要来自 arXiv，因此第一阶段可以优先兼容论文数据。

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,
    authors JSONB,
    abstract TEXT,

    source VARCHAR(100) DEFAULT 'arXiv',
    source_type VARCHAR(50) DEFAULT 'paper',
    external_id VARCHAR(255),
    url TEXT NOT NULL UNIQUE,

    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    summary_data JSONB,
    raw_data JSONB,

    total_score FLOAT DEFAULT 0,
    category VARCHAR(100),
    tags JSONB
);
```

说明：

1. `summary_data` 保存 LLM 生成的结构化中英文总结。
2. 不建议只用一个 `summary TEXT`，否则会丢失当前已有的多字段总结。
3. `external_id` 可保存 arXiv id，后续用于处理 arXiv 不同版本。
4. `total_score` 当前默认 0，暂时不参与真实评分。

`summary_data` 示例：

```json
{
  "one_sentence_summary": "...",
  "chinese_summary": "...",
  "research_problem": "...",
  "chinese_research_problem": "...",
  "core_method": "...",
  "chinese_core_method": "...",
  "innovation": "...",
  "chinese_innovation": "...",
  "why_it_matters": "...",
  "chinese_why_it_matters": "...",
  "learning_value": "...",
  "chinese_learning_value": "..."
}
```

---

### 7.4 news 表

`news` 表用于保存入选日报的 AI 新闻。

```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,
    source VARCHAR(100),
    source_type VARCHAR(50) DEFAULT 'rss',
    external_id VARCHAR(255),
    url TEXT NOT NULL UNIQUE,

    content TEXT,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    company VARCHAR(100),
    category VARCHAR(100),

    summary_data JSONB,
    raw_data JSONB,

    total_score FLOAT DEFAULT 0,
    tags JSONB
);
```

说明：

1. 当前 News 多数来自 RSS，`content` 通常是 RSS summary，不一定是完整正文。
2. `external_id` 可保存 RSS guid。
3. `summary_data` 保存中英文结构化总结。
4. `total_score` 当前默认 0，后续评分系统完成后再使用。

`summary_data` 示例：

```json
{
  "one_sentence_summary": "...",
  "chinese_summary": "...",
  "what_happened": "...",
  "chinese_what_happened": "...",
  "why_it_matters": "...",
  "chinese_why_it_matters": "...",
  "impact": "...",
  "chinese_impact": "...",
  "related_technologies": ["LLM", "Agent"]
}
```

---

### 7.5 github_repositories 表

`github_repositories` 表用于保存入选日报的 GitHub 项目。

```sql
CREATE TABLE github_repositories (
    id SERIAL PRIMARY KEY,

    full_name VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    owner VARCHAR(255),
    description TEXT,
    url TEXT NOT NULL UNIQUE,

    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    language VARCHAR(100),
    topics JSONB,

    repo_created_at TIMESTAMPTZ,
    repo_updated_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    summary_data JSONB,
    raw_data JSONB,

    total_score FLOAT DEFAULT 0,
    tags JSONB
);
```

说明：

1. `full_name` 是 GitHub 项目的核心唯一字段，例如 `langchain-ai/langchain`。
2. `stars` 会变化，所以这里保存的是最新值。
3. 如果以后要看 star 历史趋势，需要增加 snapshot 表。
4. 第一阶段也可以在 `report_items.snapshot_data` 里保存当天 stars 快照。

`summary_data` 示例：

```json
{
  "one_sentence_summary": "...",
  "chinese_summary": "...",
  "main_features": "...",
  "chinese_main_features": "...",
  "technical_highlights": "...",
  "chinese_technical_highlights": "...",
  "learning_value": "...",
  "chinese_learning_value": "...",
  "recommended_for": "...",
  "chinese_recommended_for": "...",
  "possible_use_cases": "...",
  "chinese_possible_use_cases": "..."
}
```

---

### 7.6 report_items 表

`report_items` 是第一阶段非常关键的一张表。

它用于记录某一天的日报具体展示了哪些内容，以及它们在日报里的顺序。

```sql
CREATE TABLE report_items (
    id SERIAL PRIMARY KEY,

    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,

    item_type VARCHAR(50) NOT NULL,
    item_id INTEGER NOT NULL,

    section VARCHAR(50) NOT NULL,
    rank INTEGER NOT NULL,

    score_snapshot FLOAT DEFAULT 0,
    published_at_snapshot TIMESTAMPTZ,
    snapshot_data JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (report_id, item_type, item_id)
);
```

说明：

1. `item_type` 可使用 `article`、`news`、`github_repository`。
2. `item_id` 对应具体内容表中的 id。
3. `section` 对应日报模块，例如 `articles`、`news`、`github_projects`。
4. `rank` 保存当天报告中的排序。
5. `snapshot_data` 保存当天展示时的快照，例如 GitHub stars、标题、摘要等。

为什么需要这张表：

1. 同一个 GitHub 项目可能多天入选。
2. 同一篇论文可能在不同日期被展示。
3. GitHub stars 会变化，需要保存当天快照。
4. Dashboard 的历史视图需要知道每天报告中具体选中了哪些内容。

---

## 8. 排序与分页策略

当前前端已经实现：

1. Dashboard 每个分类只展示最新的 4 个。
2. Articles、News、GitHub 页面最多每页展示 10 条。
3. 支持前端分页。
4. 当前没有真实评分系统，所以暂时按时间排序。

因此第一阶段数据库不需要负责前端分页。

第一阶段推荐排序规则：

```text
score_snapshot DESC
published_at_snapshot DESC
created_at DESC
```

但因为当前 `score_snapshot` 默认为 0，所以实际效果等价于：

```text
published_at_snapshot DESC
created_at DESC
```

后续 FastAPI 阶段再实现：

```text
GET /api/articles?page=1&page_size=10
GET /api/news?page=1&page_size=10
GET /api/github-projects?page=1&page_size=10
```

---

## 9. 去重与更新策略

### 9.1 Canonical 数据去重

| 类型 | 推荐唯一字段 |
|---|---|
| Articles | `url`，后续可增加 `external_id` |
| News | `url`，后续可增加 `external_id` |
| GitHub Projects | `full_name` |
| Reports | `report_date` |

### 9.2 Upsert 原则

第一阶段写入数据库时使用 upsert：

```text
如果内容不存在，则插入。
如果内容已存在，则更新动态字段和 summary_data。
```

GitHub 项目适合更新：

1. `stars`
2. `forks`
3. `repo_updated_at`
4. `collected_at`
5. `summary_data`

Articles 和 News 适合更新：

1. `title`
2. `published_at`
3. `summary_data`
4. `raw_data`
5. `collected_at`

---

## 10. 数据库写入时机

第一阶段建议在 `main.py` 现有流程末尾写入数据库。

推荐流程：

```text
1. 采集 papers / news / github repos
2. LLM 筛选和总结
3. 生成 Markdown report
4. 保存 Markdown report 到 outputs/
5. 将本次 run、report、items 写入数据库
```

数据库写入失败时，建议：

```text
第一阶段先记录错误，但不影响 Markdown 报告生成
```

这样可以保证日报能力稳定。

---

## 11. 建议项目结构

第一阶段只新增 `database/` 目录。

```text
AI-Intelligence-Agent/
├── main.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   └── repository.py
├── tools/
├── agents/
├── prompts/
├── frontend-react/
├── outputs/
└── tests/
```

暂时不新增：

```text
api/
```

等 Phase 4 再增加 FastAPI。

---

## 12. 配置设计

### 12.1 本地环境

`.env` 中使用：

```env
DATABASE_URL=postgresql://aiden:your_password@localhost:5432/ai_research_agent
```

也可以使用：

```env
DATABASE_URL=postgresql+psycopg2://aiden:your_password@localhost:5432/ai_research_agent
```

SQLAlchemy 两种格式都可以识别。为了明确驱动，后续可以统一成 `postgresql+psycopg2://`。

### 12.2 Docker 环境

如果应用在 Docker 容器里运行，`localhost` 指的是容器自身，不是宿主机。

如果 PostgreSQL 运行在宿主机，可以使用：

```env
DATABASE_URL=postgresql+psycopg2://aiden:your_password@host.docker.internal:5432/ai_research_agent
```

如果 PostgreSQL 也放进 `docker-compose.yml`，则可以使用服务名：

```env
DATABASE_URL=postgresql+psycopg2://postgres:your_password@postgres:5432/ai_research_agent
```

第一阶段可以先保持本地 PostgreSQL，不急着把数据库放进 Docker Compose。

---

## 13. 依赖设计

当前第一阶段需要：

```text
sqlalchemy
psycopg2-binary
python-dotenv
```

可选：

```text
alembic
```

暂时不需要：

```text
fastapi
uvicorn
pydantic
```

除非开始做 Phase 4 后端 API。

---

## 14. 索引设计

第一阶段建议添加以下索引：

```sql
CREATE INDEX idx_reports_report_date ON reports(report_date DESC);
CREATE INDEX idx_report_items_report_id ON report_items(report_id);
CREATE INDEX idx_report_items_section_rank ON report_items(section, rank);

CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_news_published_at ON news(published_at DESC);
CREATE INDEX idx_github_stars ON github_repositories(stars DESC);
```

唯一索引由表结构中的 `UNIQUE` 字段提供：

1. `reports.report_date`
2. `articles.url`
3. `news.url`
4. `github_repositories.full_name`
5. `github_repositories.url`

---

## 15. 第一阶段实现顺序

推荐按下面顺序实现：

1. 创建 `database/db.py`，读取 `DATABASE_URL` 并创建 SQLAlchemy engine。
2. 创建 `database/models.py`，定义 6 张核心表。
3. 创建 `database/repository.py`，封装 upsert 和保存日报的方法。
4. 增加一个初始化表结构的方法。
5. 在 `main.py` 报告生成完成后调用数据库保存逻辑。
6. 写测试验证数据库保存逻辑。
7. 运行一次完整日报，确认 Markdown 报告和数据库写入正常。

第一阶段不改：

1. React 前端的数据接入方式
2. Dashboard 的分页逻辑
3. 报告 Markdown 格式

---

## 16. Phase 1 完成标准

第一阶段完成后，应该满足：

1. `.env` 中的 `DATABASE_URL` 可以正常连接 PostgreSQL。
2. 程序可以创建数据库表。
3. 每次运行会产生一条 `runs` 记录。
4. 每日 Markdown 报告会保存到 `reports` 表。
5. 当天入选的 Articles 会保存到 `articles` 表。
6. 当天入选的 News 会保存到 `news` 表。
7. 当天入选的 GitHub Projects 会保存到 `github_repositories` 表。
8. `report_items` 能记录日报和内容之间的关系。
9. 重复运行同一天报告不会无限插入重复数据。
10. 数据库写入失败时，不影响 Markdown 报告文件生成。

---

## 17. Phase 2：原始数据缓存与减少 LLM 调用

Phase 2 的目标是让数据库开始参与采集和总结过程。

可以新增能力：

1. 采集后先检查数据库是否已有相同 URL 或 full_name。
2. 如果已有 `summary_data`，可以跳过重复 LLM 总结。
3. 保存更多未入选的候选内容。
4. 给每次候选内容保存 `run_id`，方便后续复盘为什么没入选。

可能新增表：

```text
candidate_items
```

或者在现有内容表中增加：

```text
selection_status
last_seen_at
seen_count
```

---

## 18. Phase 3：评分、标签和趋势

Phase 3 再实现真正的评分系统。

可以增加：

1. `relevance_score`
2. `novelty_score`
3. `impact_score`
4. `learning_value_score`
5. `popularity_score`
6. `total_score`

也可以增加标签表：

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE item_tags (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,
    item_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL REFERENCES tags(id)
);
```

在这个阶段，Dashboard 才真正改成：

```text
评分优先排序
时间排序第二
```

---

## 19. Phase 4：FastAPI 与动态前端

Phase 4 才考虑让前端从 API 读取数据库。

可增加接口：

```text
GET /api/dashboard
GET /api/articles?page=1&page_size=10
GET /api/news?page=1&page_size=10
GET /api/github-projects?page=1&page_size=10
GET /api/reports
GET /api/reports/{report_date}
```

这时后端分页才有意义。

原因是当数据量增长后，前端不应该加载全部历史数据。当前 React 前端仍使用本地 mock data，正式数据分页应在 FastAPI 接入时完成。

---

## 20. Phase 5：长期扩展

后续可以继续扩展：

1. `github_repository_snapshots`：保存 GitHub star 历史。
2. `item_embeddings`：保存向量，用于语义搜索。
3. `user_preferences`：保存用户关注主题。
4. `bookmarks`：支持收藏。
5. `alerts`：支持重要主题提醒。

这些功能都不属于当前 MVP 数据库阶段。

---

## 21. 当前推荐结论

当前最合适的数据库方案是：

```text
先做 Phase 1：数据库持久化
不重写前端
不引入 FastAPI
不改变 Markdown 报告
不提前做复杂评分
```

第一阶段完成后，项目会从“每天生成文件”升级为“每天生成文件，同时沉淀结构化历史数据”。

这一步风险最低，也最符合当前项目状态。
