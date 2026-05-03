---
name: finance-analysis
description: 当需要对采集的财经新闻进行深度分析总结时使用此技能。触发词：财经分析、市场分析、投资分析、财报解读、行业动态、宏观经济
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
---
# 财经内容深度分析技能

## 使用场景

当用户需要：

- 对采集的财经新闻进行深度分析
- 提取投资价值和风险因素
- 发现市场趋势和行业动态
- 生成结构化的财经知识总结

## 执行步骤

### 1. 读取最新采集文件

从 `knowledge/raw/` 目录读取最新的财经采集文件：

- 使用 Glob 查找匹配 `finance-*.json` 或 `rss-finance-*.json` 的文件
- 按时间戳排序，选择最新文件
- 解析 JSON 内容，提取 items 数组

### 2. 逐条深度分析

对每条财经内容进行分析，生成：

**摘要**（<=60 字）

- 精炼概括核心信息
- 突出关键数据和影响
- 使用中文描述
- 包含时间要素（如"Q3营收增长20%"）

**关键信息**（2-4 个）

- 具体数据：营收、利润、增长率、估值等
- 事件影响：政策变化、行业格局、公司动态
- 市场反应：股价变动、机构观点、资金流向
- 格式：`数据/事件 + 具体数值/影响`

**投资评估**（1-10 分）+ 理由

| 分数段 | 含义     | 标准                                           |
| ------ | -------- | ---------------------------------------------- |
| 9-10   | 重大机会 | 政策红利、行业拐点、公司重大利好、系统性机会   |
| 7-8    | 值得关注 | 行业趋势明确、公司基本面改善、结构性机会       |
| 5-6    | 一般了解 | 常规新闻、短期波动、缺乏确定性                 |
| 1-4    | 可忽略   | 炒作成分大、信息不实、影响有限                 |

**风险提示**（0-3 个）

- 政策风险：监管变化、政策收紧
- 市场风险：估值过高、流动性风险
- 公司风险：业绩下滑、管理层变动
- 行业风险：竞争加剧、技术颠覆

**标签建议**（3-5 个）

- 内容类型: `macro`, `industry`, `company`, `policy`, `earnings`
- 市场类型: `a-share`, `us-stock`, `hk-stock`, `crypto`, `commodity`
- 行业分类: `tech`, `consumer`, `finance`, `healthcare`, `energy`, `ai`
- 影响程度: `major`, `moderate`, `minor`
- 时效性: `breaking`, `daily`, `weekly`

### 3. 市场趋势发现

从整体内容集合中发现：

**行业热点**

- 多条内容涉及的行业方向
- 出现 2 次以上的行业关键词聚类

**资金流向**

- 主力资金关注的板块
- 机构调研/增持的方向

**风险预警**

- 重复提及的风险因素
- 负面信息集中的领域

**政策动向**

- 监管政策变化趋势
- 行业政策导向

**输出格式**

```markdown
## 市场趋势发现

### 行业热点
- **AI 产业**: 3 条内容涉及，政策支持+资金涌入
- **新能源**: 2 条内容涉及，补贴政策调整

### 资金流向
- 科技板块：北向资金净流入 50 亿
- 消费板块：机构调研活跃度上升

### 风险预警
- 房地产：多家房企债务风险暴露
- 加密货币：监管政策不确定性

### 政策动向
- 科技：芯片自主可控政策加码
- 金融：跨境支付监管趋严
```

### 4. 输出分析结果 JSON

保存到: `knowledge/analysis/finance-analysis-YYYY-MM-DD.json`

## 评分约束

**重要**：在 N 条内容中：

- 9-10 分内容：不超过 10%
- 7-8 分内容：不超过 30%
- 保持评分分布的合理性，避免分数膨胀
- 客观评分，不受标题情绪影响

## 财经内容类型判断

| 类型   | 识别特征                           | 分析重点                     |
| ------ | ---------------------------------- | ---------------------------- |
| 宏观   | GDP、CPI、利率、汇率、政策         | 对市场整体影响               |
| 行业   | 行业报告、板块动态、产业链         | 行业格局变化、投资机会       |
| 公司   | 财报、业绩、并购、人事变动         | 公司基本面、估值合理性       |
| 政策   | 监管文件、政策发布、法规变化       | 政策影响范围、受益/受损方    |
| 观点   | 机构研报、专家评论、投资策略       | 观点逻辑性、历史准确率       |

## 数据提取规则

**财务数据**

- 营收：识别 "营收"、"收入"、"销售额" + 数字 + 单位
- 利润：识别 "净利润"、"毛利润"、"EBITDA" + 数字
- 增长率：识别 "增长"、"同比"、"环比" + 百分比
- 估值：识别 "PE"、"PB"、"市值"、"估值" + 数字

**市场数据**

- 股价：识别 "股价"、"涨跌" + 百分比
- 成交：识别 "成交量"、"成交额"、"换手率"
- 资金：识别 "流入"、"流出"、"净买入" + 金额

**时间要素**

- 财报期：Q1/Q2/Q3/Q4 + 年份
- 事件日期：具体日期或 "今日"、"本周"
- 预期时间：指引、预测的时间范围

## 注意事项

- 区分事实与观点，事实优先
- 关注信息来源的可靠性
- 时效性对财经内容至关重要
- 避免投资建议，只做客观分析
- 如数据矛盾，标注 `data_conflict`
- 如信息不足，标注 `insufficient_data`

## 输出格式

```json
{
  "source_file": "finance-2025-05-03.json",
  "analyzed_at": "2025-05-03T16:00:00+08:00",
  "skill": "finance-analysis",
  "total_items": 15,
  "market_summary": {
    "hot_sectors": ["AI", "新能源"],
    "risk_alerts": ["房地产"],
    "policy_focus": ["科技自主可控"]
  },
  "analysis": [
    {
      "title": "英伟达Q1营收增长260%，AI芯片需求持续强劲",
      "url": "https://example.com/news/1",
      "source": "Bloomberg",
      "published_at": "2025-05-03T08:00:00+08:00",
      "summary": "英伟达Q1营收260亿美元，同比增260%，数据中心业务贡献超80%，AI芯片需求未见放缓迹象。",
      "key_info": [
        "Q1营收260亿美元，同比增长260%，超市场预期10%",
        "数据中心业务营收226亿美元，占比87%",
        "毛利率75.7%，同比提升15个百分点",
        "指引Q2营收280亿美元，继续超预期"
      ],
      "score": 9,
      "score_reason": "AI产业核心受益标的，业绩超预期且指引乐观，行业景气度持续，对科技板块有重大影响",
      "risks": [
        "估值处于历史高位，PE超过60倍",
        "竞争对手AMD、Intel加速追赶",
        "中国市场收入下滑风险"
      ],
      "suggested_tags": ["company", "us-stock", "ai", "semiconductor", "major"],
      "related_sectors": ["AI", "半导体", "云计算"],
      "investment_implication": "AI产业链景气度延续，关注国产替代机会"
    }
  ],
  "trends": {
    "hot_sectors": [
      {
        "sector": "AI",
        "count": 5,
        "sentiment": "positive",
        "key_drivers": ["业绩超预期", "政策支持", "应用落地"]
      }
    ],
    "capital_flow": [
      {
        "direction": "科技板块",
        "amount": "净流入50亿",
        "trend": "持续流入"
      }
    ],
    "risk_alerts": [
      {
        "area": "房地产",
        "risk_type": "信用风险",
        "severity": "high",
        "description": "多家房企债务展期，行业流动性压力持续"
      }
    ],
    "policy_changes": [
      {
        "policy": "芯片自主可控",
        "impact": "positive",
        "affected_sectors": ["半导体", "AI", "信创"]
      }
    ]
  }
}
```

### 字段说明

| 字段                              | 类型   | 必填 | 说明                         |
| --------------------------------- | ------ | ---- | ---------------------------- |
| `source_file`                     | string | ✅   | 分析的原始文件名             |
| `analyzed_at`                     | string | ✅   | ISO 8601 格式分析时间        |
| `skill`                           | string | ✅   | 技能标识 `finance-analysis`  |
| `total_items`                     | number | ✅   | 分析内容总数                 |
| `market_summary`                  | object | ✅   | 市场整体摘要                 |
| `market_summary.hot_sectors`      | array  | ✅   | 热门行业列表                 |
| `market_summary.risk_alerts`      | array  | ✅   | 风险预警列表                 |
| `market_summary.policy_focus`     | array  | ✅   | 政策关注点列表               |
| `analysis`                        | array  | ✅   | 内容分析结果                 |
| `analysis[].summary`              | string | ✅   | 摘要，<=60 字                |
| `analysis[].key_info`             | array  | ✅   | 关键信息，2-4 条，数据说话   |
| `analysis[].score`                | number | ✅   | 投资评估 1-10                |
| `analysis[].score_reason`         | string | ✅   | 评分理由，50-100 字          |
| `analysis[].risks`                | array  | ✅   | 风险提示，0-3 条             |
| `analysis[].suggested_tags`       | array  | ✅   | 标签建议，3-5 个             |
| `analysis[].related_sectors`      | array  | ✅   | 相关行业                     |
| `analysis[].investment_implication`| string | ✅   | 投资启示，一句话概括         |
| `trends`                          | object | ✅   | 趋势发现结果                 |
| `trends.hot_sectors`              | array  | ✅   | 行业热点                     |
| `trends.capital_flow`             | array  | ✅   | 资金流向                     |
| `trends.risk_alerts`              | array  | ✅   | 风险预警                     |
| `trends.policy_changes`           | array  | ✅   | 政策变化                     |
