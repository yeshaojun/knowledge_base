---
name: tech-summary
description: 当需要对采集的技术内容进行深度分析总结时使用此技能
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
---

# 技术内容深度分析技能

## 使用场景

当用户需要：
- 对采集的技术项目进行深度分析
- 提取技术亮点和价值评估
- 发现技术趋势和新兴概念
- 生成结构化的知识总结

## 执行步骤

### 1. 读取最新采集文件

从 `knowledge/raw/` 目录读取最新的采集文件：
- 使用 Glob 查找匹配 `github-trending-*.json` 或 `hacker-news-*.json` 的文件
- 按时间戳排序，选择最新文件
- 解析 JSON 内容，提取 items 数组

### 2. 逐条深度分析

对每个项目进行分析，生成：

**摘要**（<=50 字）
- 精炼概括项目核心价值
- 突出差异化特点
- 避免空泛描述

**技术亮点**（2-3 个）
- 用事实说话：具体功能、性能数据、创新点
- 避免主观判断，如"很强大"、"非常好"
- 格式：`功能/特性 + 具体表现/数据`

**评分**（1-10 分）+ 理由

| 分数段 | 含义 | 标准 |
|--------|------|------|
| 9-10 | 改变格局 | 开创性技术、可能颠覆现有范式、行业里程碑 |
| 7-8 | 直接有帮助 | 可立即应用于生产、解决实际痛点、成熟度高 |
| 5-6 | 值得了解 | 有参考价值、但需进一步验证、适用场景有限 |
| 1-4 | 可略过 | 同质化严重、缺乏创新、维护状态不佳 |

**标签建议**（3-5 个）
- 技术领域: `llm`, `agent`, `rag`, `fine-tuning`
- 应用场景: `code-generation`, `data-analysis`, `workflow-automation`
- 成熟度: `production-ready`, `experimental`, `research`

### 3. 趋势发现

从整体项目集合中发现：

**共同主题**
- 多个项目涉及的技术方向
- 出现 2 次以上的关键词聚类

**新概念**
- 首次出现或关注度上升的技术概念
- 命名新颖、范式创新的方案

**输出格式**
```markdown
## 趋势发现

### 共同主题
- **多智能体协作**: 3 个项目采用 multi-agent 架构
- **RAG 优化**: 2 个项目专注检索增强生成

### 新兴概念
- **Agentic Workflow**: 自主决策的工作流编排
- **Model Context Protocol**: 统一的模型上下文标准
```

### 4. 输出分析结果 JSON

保存到: `knowledge/analysis/analysis-YYYY-MM-DD.json`

## 评分约束

**重要**：在 15 个项目中：
- 9-10 分项目：不超过 2 个
- 7-8 分项目：不超过 5 个
- 保持评分分布的合理性，避免分数膨胀

## 注意事项

- 评分需客观公正，严格按标准执行
- 技术亮点必须有事实支撑，拒绝空话
- 摘要控制在 50 字以内，确保精炼
- 标签建议遵循预定义分类，避免随意创造
- 如项目信息不足，标注 `insufficient_data` 而非猜测

## 输出格式

```json
{
  "source_file": "github-trending-2025-05-03.json",
  "analyzed_at": "2025-05-03T16:00:00+08:00",
  "skill": "tech-summary",
  "total_items": 15,
  "analysis": [
    {
      "name": "modelscope/agentscope",
      "url": "https://github.com/modelscope/agentscope",
      "summary": "阿里开源多智能体协作框架，支持分布式部署与可视化编排。",
      "highlights": [
        "可视化工作流设计器，拖拽式 Agent 编排",
        "内置 50+ 工具调用，支持自定义扩展",
        "分布式部署，支持千级并发 Agent"
      ],
      "score": 8,
      "score_reason": "生产可用的多智能体方案，工具生态完善，但文档以中文为主，国际化不足",
      "suggested_tags": ["multi-agent", "workflow", "distributed", "production-ready"],
      "original_stars": 4500,
      "original_language": "Python"
    }
  ],
  "trends": {
    "common_themes": [
      {
        "theme": "多智能体协作",
        "count": 3,
        "projects": ["agentscope", "langgraph", "crewai"]
      }
    ],
    "emerging_concepts": [
      {
        "concept": "Agentic Workflow",
        "description": "自主决策的工作流编排，Agent 可根据上下文动态调整执行路径",
        "first_seen": "2025-04-15"
      }
    ]
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source_file` | string | ✅ | 分析的原始文件名 |
| `analyzed_at` | string | ✅ | ISO 8601 格式分析时间 |
| `skill` | string | ✅ | 技能标识 `tech-summary` |
| `total_items` | number | ✅ | 分析项目总数 |
| `analysis` | array | ✅ | 项目分析结果 |
| `analysis[].summary` | string | ✅ | 摘要，<=50 字 |
| `analysis[].highlights` | array | ✅ | 技术亮点，2-3 条，事实说话 |
| `analysis[].score` | number | ✅ | 评分 1-10 |
| `analysis[].score_reason` | string | ✅ | 评分理由，50-100 字 |
| `analysis[].suggested_tags` | array | ✅ | 标签建议，3-5 个 |
| `trends` | object | ✅ | 趋势发现结果 |
| `trends.common_themes` | array | ✅ | 共同主题列表 |
| `trends.emerging_concepts` | array | ✅ | 新兴概念列表 |
