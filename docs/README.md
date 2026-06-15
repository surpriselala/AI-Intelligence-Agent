# AI Intelligence Agent Documentation

本文档目录用于管理 AI Intelligence Agent 的产品文档、版本开发报告和迭代记录。

当前项目已经进入 MVP 阶段，后续每一次较大的功能迭代都应该新建一个版本目录，并在目录内保存该版本的 PRD、开发报告、测试记录和发布说明。

---

## 1. 文档目录结构

```text
docs/
├── README.md
├── versioning_guide.md
├── templates/
│   ├── prd_template.md
│   ├── development_report_template.md
│   └── release_notes_template.md
└── versions/
    └── mvp/
        ├── prd.md
        ├── development_report.md
        └── release_notes.md
```

---

## 2. 当前版本

当前版本：

```text
MVP
```

MVP 文档：

```text
docs/versions/mvp/prd.md
docs/versions/mvp/development_report.md
docs/versions/mvp/release_notes.md
```

---

## 3. MVP 过程文档归属

当前已有开发过程文档已经归档到 MVP 版本目录：

```text
DEVELOPMENT.md
DATABASE_DESIGN.md
docs/versions/mvp/development_notes/article_fetching_development.md
docs/versions/mvp/development_notes/paper_summary_development.md
docs/versions/mvp/development_notes/github_development.md
docs/versions/mvp/development_notes/news_development.md
docs/versions/mvp/development_notes/frontend_backend_optimization.md
docs/versions/mvp/development_notes/frontend_react_revision_report.md
```

这些文档可以视为 MVP 阶段的详细过程记录。后续版本的过程文档也建议放到对应版本目录下。

---

## 4. 后续版本建议

后续版本建议使用以下命名：

```text
docs/versions/v0.2-fastapi-api/
docs/versions/v0.3-react-api-integration/
docs/versions/v0.4-scoring-system/
docs/versions/v0.5-user-features/
```

每个版本目录建议包含：

```text
prd.md
development_report.md
release_notes.md
test_report.md
```

---

## 5. 文档维护原则

1. 每个版本单独开目录，不覆盖旧版本文档。
2. PRD 写“要做什么”和“为什么做”。
3. 开发报告写“实际做了什么”和“遇到的问题”。
4. 发布说明写“用户能感知到什么变化”。
5. 测试报告写“如何验证”和“还剩什么风险”。
6. 旧文档只归档，不频繁回改，避免历史记录失真。
