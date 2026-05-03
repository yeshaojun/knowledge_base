# Organizer Agent - Markdown 整理输出能力

## Parent

基于 `speces/agent-prd.md` 需求拆分

## What to build

实现 Organizer Agent 的 Markdown 整理输出功能：
- 读取已标注的分析数据
- 整理成结构化 Markdown 报告
- 存储到 `knowledge/articles/`

## Acceptance criteria

- [ ] 实现分析数据读取和聚合逻辑
- [ ] 生成 Markdown 格式报告，包含：
  - 日期摘要
  - 按分类分组展示
  - Top 项目推荐
  - 趋势洞察
- [ ] 支持 JSON 和 Markdown 双格式输出
- [ ] 文件命名符合规范：`{date}-{source}-report.md`
- [ ] 单元测试覆盖格式化逻辑

## Blocked by

- Issue #002 (Analyzer 三维度标签分析能力) - 需要分析数据

## Technical Notes

参考：
- `.opencode/agents/organizer.md` - 角色定义
- `knowledge/articles/index.json` - 现有索引格式
