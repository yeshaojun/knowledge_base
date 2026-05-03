---
name: github-trending
description: 抓取 GitHub Trending 仓库并过滤 AI/LLM/Agent/ML 相关项目。触发词：GitHub trending、热门项目、热门仓库、trending、今天有什么热门、看看 GitHub 上有什么、AI 项目推荐、GitHub AI、检查 trending、抓 trending、获取热门项目、看看有什么新的、热门 repo。支持自定义主题过滤和数量限制，HTML 解析无需 API。
---

# GitHub Trending Fetcher

抓取 GitHub Trending 页面，过滤 AI 相关项目，输出结构化 JSON。

## Quick Start

```bash
# 默认：Top 50，过滤 ai/llm/agent/ml
skill-invoke github-trending

# 自定义主题
skill-invoke github-trending --topics "ai,ml,deep-learning"

# 自定义数量
skill-invoke github-trending --limit 30
```

## Output Format

```json
[
  {
    "name": "modelscope/agentscope",
    "url": "https://github.com/modelscope/agentscope",
    "stars": 4500,
    "topics": ["ai", "agent", "llm"],
    "description": "Multi-agent framework for LLM applications"
  }
]
```

## Workflows

### 1. 标准抓取流程

- [ ] 调用 `scripts/fetch_trending.py`
- [ ] HTML 解析 GitHub Trending 页面
- [ ] 过滤包含指定 topics 的仓库
- [ ] 输出 JSON 到 stdout
- [ ] 失败时返回空数组 `[]`

### 2. 自定义参数

```bash
# 指定主题
python scripts/fetch_trending.py --topics "ai,llm,agent,ml,machine-learning"

# 指定数量限制
python scripts/fetch_trending.py --limit 100

# 组合使用
python scripts/fetch_trending.py --topics "ai,llm" --limit 30
```

## Constraints

- **不调 GitHub API**：HTML 解析避免 rate limit
- **不存数据库**：仅输出到 stdout
- **不做去重**：由调用方处理
- **失败容错**：返回空数组，不抛异常

## Performance Requirements

- 单次执行 < 10s
- 输出必须通过 `schemas/output.json` 验证

## Validation

```bash
# 验证输出格式
skill-invoke github-trending | python -m json.tool

# 验证 schema
skill-invoke github-trending | check-json-schema schemas/output.json
```

## Error Handling

| 场景 | 行为 |
|------|------|
| 网络超时 | 返回 `[]`，记录日志 |
| HTML 解析失败 | 返回 `[]`，记录日志 |
| 无匹配仓库 | 返回 `[]`（正常情况） |

## Implementation Details

See [scripts/fetch_trending.py](scripts/fetch_trending.py) for implementation.

**关键技术点**：
- 使用 `requests` + `BeautifulSoup4` 解析 HTML
- 请求间隔 1s 避免触发反爬
- User-Agent 标识：`KnowledgeBaseBot/1.0`
- Topics 匹配：大小写不敏感，支持多主题 OR 逻辑
