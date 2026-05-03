# Analyzer Agent - 三维度标签分析能力

## Parent

基于 `speces/agent-prd.md` 需求拆分

## What to build

实现 Analyzer Agent 的三维度标签分析功能：
- 读取 `knowledge/raw/` 中的采集数据
- 为每条条目打三个维度标签：
  1. **分类标签**: llm / agent / tool / research
  2. **重要性标签**: high / medium / low（对应 7-10 / 5-6 / 1-4 分）
  3. **技术栈标签**: python, typescript, transformer, rag 等
- 返回结构化分析结果 JSON

## Acceptance criteria

- [ ] 实现基于 LLM 的内容分析逻辑
- [ ] 三维度标签定义清晰，符合 `analyzer.md` 规范
- [ ] 评分标准：1-10 分，附评分理由
- [ ] 中文摘要生成：50-200 字
- [ ] 输出格式符合 analyzer.md 定义
- [ ] 单元测试覆盖标签分类逻辑

## Blocked by

- Issue #001 (Collector GitHub Trending 采集能力) - 需要采集数据测试

## Technical Notes

参考：
- `.opencode/agents/analyzer.md` - 角色定义和评分标准
- `knowledge/articles/*.json` - 现有分析结果示例
