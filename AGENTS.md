# AI 知识库助手 - Agent 协作规范

## 项目概述

自动化 AI 技术情报采集与分发系统。从 GitHub Trending 和 Hacker News 持续采集 AI/LLM/Agent 领域动态，经 AI 分析后结构化存储为 JSON，支持 Telegram/飞书多渠道分发，帮助技术团队高效追踪前沿动态。

---

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 语言 | Python 3.12 | 类型提示 + asyncio |
| Agent 框架 | LangGraph | 状态机编排，支持多 Agent 协作 |
| AI 接口 | OpenCode + 国产大模型 | DeepSeek/Qwen/GLM-4 等 |
| 爬虫框架 | OpenClaw | 声明式爬虫，支持 JS 渲染 |
| 存储 | JSON 文件 | knowledge/raw/ 和 knowledge/articles/ |
| 分发 | Telegram Bot API / 飞书开放平台 | 支持富文本、Markdown |

---

## 编码规范

> 📖 完整规范详见 [docs/coding-standards.md](./docs/coding-standards.md)

### 核心规则

- **格式化**: `ruff format`
- **类型注解**: 所有公开函数必须有类型注解
- **文档字符串**: Google 风格，中文描述
- **日志**: 使用 `logging` 模块，禁用 `print()`

### 示例

```python
def fetch_trending(limit: int = 30) -> list[dict[str, Any]]:
    """从 GitHub Trending 采集 AI 项目数据。
    
    Args:
        limit: 返回项目数量，默认 30。
    
    Returns:
        项目列表，每个元素包含 name、url、description、stars 等字段。
    
    Raises:
        NetworkError: 网络请求失败时抛出。
    """
    logger.info(f"开始采集 GitHub Trending，限制 {limit} 条")
    # ...
```

---

## 项目结构

```
knowledge_base/
├── .opencode/
│   ├── agents/              # Agent 定义
│   │   ├── collector.py     # 采集 Agent
│   │   ├── analyzer.py      # 分析 Agent
│   │   └── formatter.py     # 格式化 Agent
│   ├── skills/              # Agent 技能模块
│   │   ├── github_trending.py
│   │   ├── hacker_news.py
│   │   └── content_analysis.py
│   └── config/
│       └── settings.py      # 配置管理
├── knowledge/
│   ├── raw/                 # 原始采集数据
│   │   └── 2025-05-03_github_ai.json
│   └── articles/            # 结构化知识条目
│       └── 2025-05-03_articles.json
├── speces/
│   └── project-vision.md    # 项目愿景
├── tests/                   # 测试用例
├── scripts/                 # 工具脚本
├── AGENTS.md                # 本文件
└── pyproject.toml           # 项目配置
```

---

## 知识条目 JSON 格式

### 原始采集数据 (`knowledge/raw/*.json`)
```json
{
  "fetch_id": "gh_20250503_001",
  "source": "github_trending",
  "fetched_at": "2025-05-03T14:30:00+08:00",
  "items": [
    {
      "name": "modelscope/agentscope",
      "url": "https://github.com/modelscope/agentscope",
      "description": "Multi-agent framework for LLM applications",
      "stars": 4500,
      "language": "Python",
      "forks": 320
    }
  ]
}
```

### 结构化知识条目 (`knowledge/articles/*.json`)
```json
{
  "id": "kb_20250503_001",
  "title": "AgentScope：阿里开源多智能体框架",
  "source_url": "https://github.com/modelscope/agentscope",
  "source_type": "github_trending",
  "summary": "阿里巴巴开源的多智能体协作框架，支持分布式部署和工作流编排...",
  "key_points": [
    "支持多 Agent 协作与通信",
    "内置工具调用和 RAG 支持",
    "可视化工作流设计器"
  ],
  "tags": ["agent", "multi-agent", "alibaba", "open-source"],
  "category": "agent_framework",
  "importance": "high",
  "status": "pending",
  "created_at": "2025-05-03T14:35:00+08:00",
  "updated_at": "2025-05-03T14:35:00+08:00",
  "distributed_to": [],
  "metadata": {
    "stars": 4500,
    "language": "Python",
    "license": "Apache-2.0"
  }
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识，格式: `kb_YYYYMMDD_NNN` |
| `title` | string | ✅ | 标题，简洁明确 |
| `source_url` | string | ✅ | 原始链接 |
| `source_type` | string | ✅ | 来源类型: `github_trending` / `hacker_news` |
| `summary` | string | ✅ | 摘要，50-200 字 |
| `key_points` | array | ❌ | 关键要点，3-5 条 |
| `tags` | array | ✅ | 标签，3-7 个 |
| `category` | string | ✅ | 分类: `llm` / `agent` / `tool` / `research` |
| `importance` | string | ✅ | 重要性: `high` / `medium` / `low` |
| `status` | string | ✅ | 状态: `pending` / `reviewed` / `distributed` |
| `created_at` | string | ✅ | ISO 8601 格式时间戳 |
| `updated_at` | string | ✅ | ISO 8601 格式时间戳 |
| `distributed_to` | array | ✅ | 分发渠道记录 |
| `metadata` | object | ❌ | 额外元数据 |

---

## Agent 角色概览

| Agent 角色 | 职责 | 输入 | 输出 | 关键技能 |
|------------|------|------|------|----------|
| **Collector** | 数据采集 | 采集配置 | `knowledge/raw/*.json` | GitHub API、HN API、反爬处理 |
| **Analyzer** | 内容分析 | 原始 JSON | `knowledge/articles/*.json` | LLM 调用、内容理解、标签提取 |
| **Formatter** | 分发格式化 | 知识条目 JSON | 渠道消息（Markdown/富文本） | 模板渲染、渠道适配 |

### Agent 协作流程
```
Collector (采集) 
    ↓ raw/*.json（只返回数据，不写入）
Organizer (存储)
    ↓ 写入 raw/*.json
Analyzer (分析)
    ↓ articles/*.json
Organizer (存储)
    ↓ 写入 articles/*.json
Formatter (格式化)
    ↓ 渠道消息
[Telegram / 飞书]
```

### Agent 调用规范

**必须通过 Task 工具委派子 Agent**，不能由 Sisyphus 直接扮演角色。

```typescript
// ✅ 正确：Task 委派
task(
  category="unspecified-high",
  load_skills=[],
  run_in_background=false,
  prompt="读取 .opencode/agents/collector.md 作为角色定义。
          执行采集任务：搜集本周 GitHub Trending 和 Hacker News AI 领域热门项目。
          返回结构化 JSON 结果（不要写入文件）。"
)

// ❌ 错误：Sisyphus 直接扮演
// Sisyphus 拥有完整工具权限，不受角色定义的权限限制
// 会导致 Collector 越权写入文件
```

**原因**：
- 子 Agent 受角色定义的权限限制
- Sisyphus 拥有完整工具权限，直接扮演会越权
- 集中写入由 Organizer 负责，保证数据流边界清晰

---

## 红线（绝对禁止）

### 数据安全
- ❌ **禁止提交 API Key、Token 到 Git**（使用 `.env` + `.gitignore`）
- ❌ **禁止采集个人隐私数据**（邮箱、手机号、真实姓名）
- ❌ **禁止存储用户敏感信息**

### 代码质量
- ❌ **禁止裸 `print()`** → 必须用 `logging`
- ❌ **禁止裸 `except:`** → 必须明确异常类型
- ❌ **禁止硬编码配置** → 使用配置文件或环境变量
- ❌ **禁止绕过类型检查** → 禁用 `# type: ignore`

### 采集规范
- ❌ **禁止高频请求** → 遵守 `robots.txt`，添加请求间隔
- ❌ **禁止伪造 User-Agent** → 使用合法标识
- ❌ **禁止绕过付费墙** → 仅采集公开内容

### 数据处理
- ❌ **禁止篡改原始数据** → `raw/` 目录只追加不修改
- ❌ **禁止删除未归档数据** → 至少保留 30 天
- ❌ **禁止未审核直接分发** → status 必须为 `reviewed` 才能分发

### 协作规范
- ❌ **禁止直接修改 `main` 分支** → 必须通过 PR 合并
- ❌ **禁止无测试提交** → 核心功能必须有单元测试
- ❌ **禁止提交未格式化代码** → 运行 `ruff format`

---

## 快速开始

```bash
# 安装依赖
uv sync

# 运行采集
uv run python -m knowledge_base.collector

# 运行分析
uv run python -m knowledge_base.analyzer

# 运行分发
uv run python -m knowledge_base.formatter
```

---

## 参考资料

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [OpenClaw 文档](https://github.com/openclaw/openclaw)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [飞书开放平台](https://open.feishu.cn/)
