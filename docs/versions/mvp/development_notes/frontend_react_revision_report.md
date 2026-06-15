# React Frontend Revision Report

本文档用于记录当前 React 前端第一版与目标设计之间的差异，并明确下一轮修改方向。

当前 React 版本已经完成基础框架：

```text
1. 使用 React + Vite + TypeScript
2. 拆分 Sidebar / Topbar / StatCard / ContentCard / Pagination 等组件
3. Dashboard、Articles、News、GitHub Projects 页面可以切换
4. 搜索、关键词筛选、分页逻辑已经具备
```

但根据最新设计反馈，当前实现还没有达到目标视觉和交互标准，需要进行一轮修正。

---

## 1. 目标设计基准

后续 React 前端应以用户给出的第一张设计图为主要参考。

目标设计特点：

```text
1. 页面整体更轻、更干净
2. 主体内容留白更自然
3. 卡片之间有明确间距，不应贴合过紧
4. Dashboard 信息密度适中，但不能显得拥挤
5. 关键词筛选和搜索框是两套独立交互
6. 页面导航应使用前端路由，而不是纯 state 切换
```

图标暂时不是重点，可以后续再统一调整。

---

## 2. 当前版本主要问题

### 2.1 主体卡片贴合过紧，缺少美感

当前 React 版本中，Dashboard 三个主面板的视觉效果偏紧：

```text
Articles / News / GitHub Projects 三列之间虽然有 gap
但面板内部 item 之间主要靠 border 分割
卡片自身缺少独立容器感
内容区域显得像表格列表，而不是精致 Dashboard 卡片
```

目标设计中，每个 item 更像一个独立的小卡片：

```text
1. 每条内容之间有明确间距
2. item 自身有轻微 border / background / radius
3. 面板内部有 padding
4. item 不应该直接顶住 panel 边界
5. 卡片之间的呼吸感要强一些
```

下一轮修改方向：

```text
1. .item-list 改成带 gap 的 grid
2. .panel 内部增加内容 padding
3. .content-card 改成独立 card 样式
4. 移除或弱化 item 之间的硬分割线
5. Dashboard 三列的 panel 高度和内部间距向目标图靠近
```

建议样式方向：

```css
.item-list {
  display: grid;
  gap: 12px;
  padding: 16px;
}

.content-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 14px;
}
```

---

### 2.2 Overview 区域位置不符合目标设计

当前 React 版本中：

```text
顶部筛选栏在 Overview 上方
Overview 和 stats 被压缩成一个比较紧的横向区域
```

目标设计中顺序应该更接近：

```text
Topbar
Overview card
Filter bar
Dashboard content panels
```

也就是说，筛选栏应该在 Overview 下方，而不是紧贴标题区域。

下一轮修改方向：

```text
1. Dashboard 页面中显示 Overview
2. FilterBar 移到 Overview 下方
3. Archive 页面可以保留 FilterBar，但不需要显示 Overview
4. Dashboard 页面主体内容整体向目标图靠拢
```

---

### 2.3 关键词筛选不应该同步搜索框

当前实现中，点击关键词筛选会调用：

```text
handleQueryChange(filter)
```

这导致：

```text
点击 Multimodal 后，搜索框也自动填入 Multimodal
```

这个交互不符合日常使用习惯。

搜索框和关键词筛选应该是两套独立状态：

```text
searchQuery: 用户主动输入的搜索内容
activeTopic: 用户点击的快捷主题
```

二者可以共同影响筛选结果，但不应该互相覆盖 UI。

正确交互应该是：

```text
1. 用户输入搜索框，只改变 searchQuery
2. 用户点击 LLM / Agent / RAG / Multimodal，只改变 activeTopic
3. 搜索框内容不被快捷主题自动填充
4. 点击 All 清空 activeTopic，但不清空 searchQuery
5. 后续可以扩展 LangChain、OpenAI、Claude、vLLM 等主题
```

下一轮修改方向：

```ts
const [searchQuery, setSearchQuery] = useState("");
const [activeTopic, setActiveTopic] = useState("All");
```

筛选逻辑改成：

```text
先按 searchQuery 搜索
再按 activeTopic 过滤
```

或：

```text
searchQuery 和 activeTopic 同时作为过滤条件
```

但 UI 上必须保持：

```text
关键词按钮不会写入搜索框
```

---

### 2.4 当前前端没有路由

当前 React 版本使用：

```ts
const [activeView, setActiveView] = useState<ViewKey>("dashboard");
```

这可以完成页面切换，但不是现代 React 前端常见方式。

问题：

```text
1. 浏览器地址栏不会变化
2. 无法直接访问 /articles /news /github-projects
3. 刷新页面会回到 dashboard
4. 浏览器前进后退不可用
5. 后续接详情页、报告页会变麻烦
```

下一轮修改方向：

引入 React Router。

推荐依赖：

```text
react-router-dom
```

推荐路由：

```text
/                  Dashboard
/articles          Articles archive
/news              News archive
/github-projects   GitHub projects archive
/reports           Reports list
/reports/:date     Report detail
```

第一轮只需要实现：

```text
/
/articles
/news
/github-projects
```

后续 FastAPI 接入后再做：

```text
/reports
/reports/:date
```

侧边栏改造：

```text
使用 NavLink 替代 button + onClick
通过 pathname 判断 active 状态
```

View all 改造：

```text
使用 Link 跳转，而不是 setActiveView
```

---

### 2.5 当前 mock data 过滤效果容易造成空状态误解

因为当前使用 mock data，且关键词和搜索框共用状态，所以会出现：

```text
点击 Multimodal 后进入 GitHub Projects 页面
列表显示 No items found
```

这不是数据为空，而是筛选状态过度影响了列表。

下一轮修改方向：

```text
1. 搜索和 topic 独立
2. Archive 页面清楚展示当前过滤条件
3. 如果为空，空状态需要说明是过滤后无结果，而不是数据库没数据
4. mock data 中补充更多覆盖 LLM / Agent / RAG / Multimodal 的项目数据
```

建议空状态文案：

```text
No matching items found.
```

而不是：

```text
No items found.
```

---

## 3. 下一轮修改范围

下一轮不需要接 FastAPI，先修正 React 前端自身。

应该修改：

```text
frontend-react/src/App.tsx
frontend-react/src/styles.css
frontend-react/src/components/Sidebar.tsx
frontend-react/src/components/ContentSection.tsx
frontend-react/src/components/ContentCard.tsx
frontend-react/src/pages/DashboardPage.tsx
frontend-react/src/pages/ArchivePage.tsx
frontend-react/src/api/mockData.ts
```

应该新增：

```text
react-router-dom
frontend-react/src/components/FilterBar.tsx
frontend-react/src/layouts/AppLayout.tsx
```

可以暂时不改：

```text
FastAPI
database
main.py
旧 frontend/
```

---

## 4. 推荐修改顺序

### Step 1：引入路由

```text
安装 react-router-dom
用 BrowserRouter 包裹 App
新增 AppLayout
使用 Routes / Route 定义页面
Sidebar 使用 NavLink
View all 使用 Link
```

完成后应该支持：

```text
http://127.0.0.1:5173/
http://127.0.0.1:5173/articles
http://127.0.0.1:5173/news
http://127.0.0.1:5173/github-projects
```

---

### Step 2：拆分搜索和主题筛选

新增两个状态：

```ts
searchQuery
activeTopic
```

搜索框只控制：

```text
searchQuery
```

主题按钮只控制：

```text
activeTopic
```

点击主题按钮后：

```text
搜索框内容不变
```

---

### Step 3：调整 Dashboard 结构顺序

目标顺序：

```text
Topbar
Overview
FilterBar
Dashboard panels
```

Archive 页面顺序：

```text
Topbar
FilterBar
Page heading
Archive list
Pagination
```

---

### Step 4：优化卡片间距和面板美感

重点调整：

```text
1. panel 内部 padding
2. item-list gap
3. content-card border radius
4. content-card 独立边框
5. 减弱大面积阴影
6. Dashboard 三列之间留白更自然
```

参考目标图，内容卡片应该是：

```text
轻边框
浅背景
圆角 8px
卡片间隔 10-14px
不要靠 border-bottom 强行分割
```

---

### Step 5：补充 mock data

为了测试筛选效果，需要 mock data 覆盖更多关键词：

```text
LLM
Agent
RAG
Multimodal
LangChain
OpenAI
Claude
vLLM
Transformers
```

这样点击不同主题时不会轻易出现误导性的空状态。

---

## 5. 修改完成标准

下一轮修改完成后，应满足：

```text
1. 页面视觉更接近目标设计图 1
2. Dashboard 主体卡片不再贴合过紧
3. 内容 item 有独立卡片感
4. 搜索框只用于搜索
5. 关键词按钮不会自动填充搜索框
6. 支持前端路由
7. 浏览器刷新后仍停留在当前页面
8. 浏览器前进后退可用
9. /articles /news /github-projects 可以直接访问
10. npm run build 通过
```

---

## 6. 暂不处理内容

本轮暂时不处理：

```text
1. 图标最终视觉统一
2. FastAPI 数据接入
3. 数据库 API 查询
4. 报告详情页
5. 用户登录
6. 收藏 / 书签 / 提醒功能
```

这些放到路由和前端视觉稳定之后再做。

---

## 7. 结论

当前 React 第一版完成了“框架迁移”，但还没有完成“体验对齐”。

下一步应该优先修正：

```text
1. 视觉间距和卡片美感
2. 搜索与主题筛选的状态分离
3. React Router 路由化
```

这三个问题解决后，React 前端才适合作为后续 FastAPI 数据接入的基础。
