# Versioning Guide

本文档定义 AI Intelligence Agent 后续版本文档的管理方式。

---

## 1. 版本命名规则

推荐格式：

```text
v主版本.次版本-版本主题
```

示例：

```text
v0.2-fastapi-api
v0.3-react-api-integration
v0.4-scoring-system
v0.5-user-preferences
```

当前 MVP 使用特殊目录名：

```text
mvp
```

---

## 2. 新版本目录模板

每次开始新版本时，在 `docs/versions/` 下创建新目录：

```text
docs/versions/v0.2-fastapi-api/
├── prd.md
├── development_report.md
├── release_notes.md
└── test_report.md
```

如果版本较大，可以增加：

```text
api_design.md
database_migration.md
frontend_design.md
deployment_notes.md
```

---

## 3. 版本文档生命周期

### 3.1 开发前

先写：

```text
prd.md
```

内容包括：

1. 背景
2. 目标
3. 功能范围
4. 不做什么
5. 验收标准
6. 风险

### 3.2 开发中

持续更新：

```text
development_report.md
```

内容包括：

1. 实现进度
2. 修改文件
3. 决策记录
4. 遇到的问题
5. 暂时保留的技术债

### 3.3 开发完成后

补充：

```text
release_notes.md
test_report.md
```

内容包括：

1. 用户可见变化
2. 技术变化
3. 运行方式变化
4. 测试命令
5. 已知问题

---

## 4. 版本推进原则

1. 一个版本只解决一个主要方向。
2. 避免在同一版本里同时重写前端、后端、数据库和部署。
3. 每个版本结束后必须能运行。
4. 如果需求变化很大，开新版本目录，不在旧版本文档里硬改。
5. 文档要记录真实决策，不只记录最终结果。

---

## 5. 建议版本路线

```text
MVP
已完成固定工作流、日报生成、数据库持久化、React 前端框架。

v0.2-fastapi-api
增加 FastAPI，从 PostgreSQL 提供 Dashboard API。

v0.3-react-api-integration
React 前端接入 FastAPI，替代 mock data。

v0.4-scoring-system
增加评分系统，支持评分优先排序。

v0.5-docker-production
完善 Docker Compose，拆分 agent / api / frontend / postgres。

v0.6-user-workflow
增加收藏、书签、提醒和用户偏好。
```
