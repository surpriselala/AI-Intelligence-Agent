# Article Fetching Development Document

本文档用于记录 AI Intelligence Agent 第一阶段功能：从 arXiv 获取 AI 相关论文数据。

当前阶段只实现“文章获取”，不实现 LLM 总结、排序和报告美化。目标是先让数据稳定进入系统，为后续 paper agent 总结功能做准备。

---

## 1. 功能目标

本功能需要完成：

```text
输入：关键词 query，例如 "AI agent" 或 "large language model"
处理：调用 arXiv 数据源，获取最近相关论文
输出：结构化论文列表 list[dict]
```

期望输出格式：

```python
[
    {
        "title": "Paper title",
        "authors": ["Author A", "Author B"],
        "summary": "Paper abstract",
        "published_date": "2026-06-07",
        "url": "https://arxiv.org/abs/xxxx.xxxxx"
    }
]
```

---

## 2. 本阶段不做什么

为了保持 MVP 简单，本阶段暂时不做：

```text
1. 不调用 LLM
2. 不做论文重要性排序
3. 不做复杂去重
4. 不保存数据库
5. 不抓取 PDF 全文
6. 不做前端展示
7. 不做定时任务
```

这些功能后续可以在 paper agent、data/history 或 scheduler 模块中逐步加入。

---

## 3. 涉及文件

主要实现文件：

```text
tools/arxiv_tool.py
```

可能需要调整的文件：

```text
config.py
tests/test_arxiv_tool.py
requirements.txt
main.py
```

本阶段推荐只优先改：

```text
1. tools/arxiv_tool.py
2. tests/test_arxiv_tool.py
3. config.py
```

---

## 4. 推荐技术方案

### 4.1 arXiv Python SDK

推荐使用 `arxiv` 这个 Python 包。

原因：

```text
1. 比自己拼 arXiv API URL 更简单
2. 能直接拿到 title、authors、summary、published、entry_id
3. 适合 MVP 快速实现
4. 后续需要扩展排序和分类也方便
```

`requirements.txt` 中已经包含：

```text
arxiv
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 5. 开发流程

### Step 1: 明确函数接口

文件：

```text
tools/arxiv_tool.py
```

函数保持为：

```python
def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict]:
    ...
```

注意：

```text
1. 不要让外部模块依赖 arxiv SDK 的原始对象
2. 函数必须返回 list[dict]
3. 即使请求失败，也尽量返回空列表，而不是让整个 main.py 崩掉
```

---

### Step 2: 创建 arXiv Search

需要用到的技术：

```python
import arxiv
```

推荐搜索配置：

```python
search = arxiv.Search(
    query=query,
    max_results=max_results,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending,
)
```

说明：

```text
1. sort_by 使用 SubmittedDate，优先获取最新论文
2. sort_order 使用 Descending，最新的排前面
3. max_results 从 config.py 传入，避免写死
```

---

### Step 3: 使用 arXiv Client 获取结果

推荐使用：

```python
client = arxiv.Client()
results = client.results(search)
```

注意：

```text
1. client.results(search) 返回的是迭代器
2. 需要遍历结果并转成普通 dict
3. 不要把 SDK 对象直接返回给 agent
```

---

### Step 4: 解析论文字段

每篇论文需要解析成：

```python
{
    "title": result.title,
    "authors": [author.name for author in result.authors],
    "summary": result.summary,
    "published_date": result.published.date().isoformat(),
    "url": result.entry_id,
}
```

需要注意：

```text
1. title 可能包含换行，需要清理成单行
2. summary 可能包含多余空白，需要 strip
3. published 可能是 datetime，需要转成字符串
4. url 使用 entry_id，通常是 arXiv abstract 页面
```

推荐写一个内部辅助函数：

```python
def _normalize_text(value: str) -> str:
    return " ".join(value.split())
```

这样 title 和 summary 都可以统一处理。

---

### Step 5: 异常处理

需要处理：

```text
1. query 为空
2. max_results <= 0
3. arXiv 请求失败
4. 单条结果字段缺失
```

推荐策略：

```text
1. query 为空时直接返回 []
2. max_results <= 0 时直接返回 []
3. arXiv 请求失败时打印清晰错误，并返回 []
4. 单条结果解析失败时跳过该条
```

示例：

```python
try:
    ...
except Exception as error:
    print(f"Failed to search arXiv papers: {error}")
    return []
```

当前 MVP 可以先用 `print`，后续再替换成 `logging`。

---

## 6. 测试计划

测试文件：

```text
tests/test_arxiv_tool.py
```

### 6.1 不依赖网络的单元测试

优先写不依赖网络的测试，因为 CI 或本地网络可能不稳定。

建议测试：

```text
1. 空 query 返回 []
2. max_results 为 0 返回 []
3. 返回值类型是 list
```

示例：

```python
def test_empty_query_returns_empty_list():
    papers = search_arxiv_papers("", max_results=3)
    assert papers == []
```

---

### 6.2 可选的真实网络测试

真实调用 arXiv 的测试可以先手动运行，不建议默认放进单元测试。

原因：

```text
1. 网络不稳定会导致测试失败
2. arXiv 可能限流
3. 本项目当前还在 MVP 初期
```

手动验证命令：

```bash
python -c "from tools.arxiv_tool import search_arxiv_papers; print(search_arxiv_papers('AI agent', 3))"
```

---

## 7. 和主流程的关系

实现完成后，`main.py` 中的流程会变成：

```text
main.py
   ↓
search_arxiv_papers()
   ↓
select_important_papers()
   ↓
summarize_paper()
   ↓
build_daily_report()
```

本阶段完成后，`select_important_papers()` 和 `summarize_paper()` 仍然可以是占位逻辑。

也就是说：

```text
本阶段只保证 papers 数据真实进入 pipeline。
```

---

## 8. 验收标准

文章获取功能完成后，需要满足：

```text
1. search_arxiv_papers("AI agent", 3) 能返回 list
2. 每个 paper 至少包含 title、authors、summary、published_date、url
3. query 为空时返回 []
4. max_results <= 0 时返回 []
5. arXiv 请求失败时不会导致 main.py 整体崩溃
6. python main.py 可以正常运行并生成 Markdown 报告
7. python -m unittest discover -s tests 可以通过
```

---

## 9. 后续扩展方向

文章获取完成后，下一步可以做：

```text
1. paper_agent.py 中实现 LLM 论文筛选
2. paper_agent.py 中实现 LLM 论文结构化总结
3. 增加关键词分组，例如 LLM、Agent、RAG、Multimodal
4. 增加去重逻辑，避免同一论文重复出现
5. 保存历史记录，避免每天重复推荐旧论文
6. 抓取 PDF 链接或 arXiv category
7. 增加日志系统
```

推荐下一步顺序：

```text
先实现 arXiv 获取
再实现 paper selection
最后实现 paper summary
```

---

## 10. 实现时的注意事项

```text
1. 保持函数返回结构稳定，后续 agent 和 report 都依赖它
2. 不要在 tools/arxiv_tool.py 中写 LLM 逻辑
3. 不要让 arXiv SDK 对象流入 agents 层
4. 网络失败时返回空列表，不要中断整个 workflow
5. 测试不要默认依赖真实网络
6. 先保证小闭环能跑通，再追求排序质量和总结质量
```

这个功能的核心不是“抓很多论文”，而是“稳定、结构化、可被后续模块消费地获取论文”。

----------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------

# 本次开发细节

本次开发完成了 `tools/arxiv_tool.py` 中的 arXiv 论文获取功能，并补充了对应的离线单元测试。

---

## 1. 修改文件

```text
tools/arxiv_tool.py
tests/test_arxiv_tool.py
developmentDoc/article_fetching_development.md
```

---

## 2. 新增和实现的函数

### 2.1 search_arxiv_papers()

位置：

```text
tools/arxiv_tool.py
```

函数签名：

```python
def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    ...
```

作用：

```text
根据传入的 query 搜索 arXiv，并返回结构化后的论文列表。
```

接收参数：

```text
query: str
    arXiv 搜索关键词或搜索表达式。
    示例："AI agent"、"large language model"、"AI agent OR RAG"

max_results: int
    最多返回多少篇论文。
    默认值是 10。
```

输出结果：

```python
[
    {
        "title": "Paper title",
        "authors": ["Author A", "Author B"],
        "summary": "Paper abstract",
        "published_date": "2026-06-07",
        "url": "https://arxiv.org/abs/xxxx.xxxxx"
    }
]
```

内部开发逻辑：

```text
1. 如果 query 为空，直接返回 []
2. 如果 max_results <= 0，直接返回 []
3. 延迟导入 arxiv 包
4. 创建 arxiv.Search
5. 使用 arxiv.Client().results(search) 获取结果
6. 遍历 arXiv SDK 返回对象
7. 用 _paper_to_dict() 转换成普通 dict
8. 如果单条论文解析失败，跳过该条
9. 如果整体搜索失败，打印错误并返回 []
```

使用到的技术：

```text
1. arxiv Python SDK
2. arxiv.Search
3. arxiv.Client
4. arxiv.SortCriterion.SubmittedDate
5. arxiv.SortOrder.Descending
```

为什么使用延迟导入：

```text
当前项目可能还没有安装 requirements.txt 中的依赖。
把 import arxiv 放在函数内部，可以避免 import tools.arxiv_tool 时直接报错。
这样测试和主流程在缺少 arxiv 包时仍然能运行，只是返回空列表。
```

---

### 2.2 _paper_to_dict()

位置：

```text
tools/arxiv_tool.py
```

函数签名：

```python
def _paper_to_dict(result: Any) -> dict[str, Any]:
    ...
```

作用：

```text
把 arXiv SDK 返回的单个 result 对象转换成项目内部使用的普通 dict。
```

接收参数：

```text
result: Any
    arXiv SDK 返回的论文对象。
    需要包含 title、authors、summary、published、entry_id 等字段。
```

输出结果：

```python
{
    "title": "Normalized paper title",
    "authors": ["Author A", "Author B"],
    "summary": "Normalized abstract",
    "published_date": "2026-06-07",
    "url": "https://arxiv.org/abs/xxxx.xxxxx"
}
```

字段映射关系：

```text
result.title -> title
result.authors -> authors
result.summary -> summary
result.published.date().isoformat() -> published_date
result.entry_id -> url
```

为什么需要这个函数：

```text
1. 隔离 arXiv SDK 原始对象
2. 保持 tools 层输出结构稳定
3. 让 agents 和 report 不需要知道 arXiv SDK 的字段细节
4. 方便单独测试字段解析逻辑
```

---

### 2.3 _normalize_text()

位置：

```text
tools/arxiv_tool.py
```

函数签名：

```python
def _normalize_text(value: str) -> str:
    ...
```

作用：

```text
清理论文标题和摘要中的多余空白、换行和 tab。
```

接收参数：

```text
value: str
    需要清理的原始文本。
```

输出结果：

```text
清理后的单行字符串。
```

示例：

```python
_normalize_text("A\n  B\tC")
# 输出："A B C"
```

为什么需要这个函数：

```text
arXiv 返回的 title 和 summary 有时包含换行或连续空格。
如果不清理，生成 Markdown 报告时可读性会变差。
```

---

## 3. 测试细节

测试文件：

```text
tests/test_arxiv_tool.py
```

本次补充的测试：

```text
1. test_empty_query_returns_empty_list
2. test_zero_max_results_returns_empty_list
3. test_search_arxiv_papers_returns_list
4. test_search_arxiv_papers_parses_sdk_results
5. test_normalize_text_collapses_whitespace
```

### 3.1 test_empty_query_returns_empty_list

作用：

```text
验证 query 为空时，函数返回 []。
```

输入：

```python
search_arxiv_papers("", max_results=3)
```

期望输出：

```python
[]
```

---

### 3.2 test_zero_max_results_returns_empty_list

作用：

```text
验证 max_results 为 0 时，函数返回 []。
```

输入：

```python
search_arxiv_papers("AI agent", max_results=0)
```

期望输出：

```python
[]
```

---

### 3.3 test_search_arxiv_papers_returns_list

作用：

```text
验证函数的基础返回类型始终是 list。
```

输入：

```python
search_arxiv_papers("AI agent", max_results=3)
```

期望输出：

```text
返回值类型是 list。
```

---

### 3.4 test_search_arxiv_papers_parses_sdk_results

作用：

```text
验证 arXiv SDK result 对象可以被正确转换成项目内部 dict。
```

使用的技术：

```text
1. unittest.mock.patch.dict
2. sys.modules 注入 fake arxiv module
3. types.SimpleNamespace 构造假 result 对象
```

为什么这样测试：

```text
默认单元测试不应该依赖真实网络。
通过 fake arxiv module 可以模拟 arXiv SDK 行为，并稳定测试字段解析逻辑。
```

---

### 3.5 test_normalize_text_collapses_whitespace

作用：

```text
验证 _normalize_text() 可以把换行、多个空格和 tab 清理成单个空格。
```

输入：

```python
_normalize_text("A\n  B\tC")
```

期望输出：

```python
"A B C"
```

---

## 4. 本次实现后的行为

当本地已经安装 `arxiv` 包并且网络可用时：

```text
search_arxiv_papers("AI agent", 3)
```

会真实请求 arXiv，并返回最多 3 篇最新相关论文。

当本地没有安装 `arxiv` 包时：

```text
函数会打印导入失败信息，并返回 []。
```

当 arXiv 请求失败时：

```text
函数会打印请求失败信息，并返回 []。
```

当某一条论文解析失败时：

```text
只跳过这一条，不影响其他论文。
```

---

## 5. 和后续功能的接口约定

后续 `agents/paper_agent.py` 可以直接消费 `search_arxiv_papers()` 的输出。

例如：

```python
papers = search_arxiv_papers("AI agent", max_results=10)
selected_papers = select_important_papers(papers, top_k=3)
paper_summaries = [summarize_paper(paper) for paper in selected_papers]
```

需要保持稳定的字段：

```text
title
authors
summary
published_date
url
```

后续如果要增加字段，推荐只新增，不删除或改名已有字段。

可以考虑新增的字段：

```text
pdf_url
primary_category
categories
updated_date
```

---

## 6. 本次开发的验收命令

```bash
python3 -m unittest discover -s tests
python3 -m compileall -q .
python3 main.py
```
