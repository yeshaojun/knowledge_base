请帮我创建 .opencode/agents/collector.md 文件，定义一个知识采集 Agent。

要求：

- 角色：AI 知识库助手的采集 Agent，从 GitHub Trending 和 Hacker News 采集技术动态
- 允许权限：Read, Grep, Glob, WebFetch（只看只搜不写）
- 禁止权限：Write, Edit, Bash（并说明为什么禁止）
- 工作职责：搜索采集、提取标题/链接/热度/摘要、初步筛选、按热度排序
- 输出格式：JSON 数组，每条含 title, url, source, popularity, summary
- 质量自查清单：条目>=15、信息完整、不编造、中文摘要



参考 .opencode/agents/collector.md 的格式，帮我创建另外两个 Agent 定义文件：

1. .opencode/agents/analyzer.md — 分析 Agent
   - 权限同 collector（Read/Grep/Glob/WebFetch，禁止 Write/Edit/Bash）
   - 职责：读取 knowledge/raw/ 的数据，写摘要、提亮点、打评分(1-10)、建议标签
   - 评分标准：9-10 改变格局，7-8 直接有帮助，5-6 值得了解，1-4 可略过

2. .opencode/agents/organizer.md — 整理 Agent
   - 权限：允许 Read/Grep/Glob/Write/Edit，禁止 WebFetch/Bash
   - 职责：去重检查、格式化为标准 JSON、分类存入 knowledge/articles/
   - 文件命名规范：{date}-{source}-{slug}.json