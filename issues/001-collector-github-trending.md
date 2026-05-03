# Collector Agent - GitHub Trending 采集能力

## Parent

基于 `speces/agent-prd.md` 需求拆分

## What to build

实现 Collector Agent 的 GitHub Trending Top 50 采集功能：
- 从 GitHub Trending 页面抓取 Top 50 项目
- 过滤 AI/LLM/Agent 相关项目（关键词匹配）
- 返回结构化 JSON 结果（不写入文件）

## Acceptance criteria

- [ ] 实现基于 WebFetch 或 API 的 GitHub Trending 数据抓取
- [ ] 过滤逻辑：保留 AI 相关项目（关键词：AI, LLM, Agent, GPT, Claude 等）
- [ ] 输出格式符合 `knowledge/raw/*.json` 定义
- [ ] 条目数量：Top 50，过滤后保留 ≥ 15 条
- [ ] 遵守 `robots.txt`，添加请求间隔（防封禁）
- [ ] 单元测试覆盖核心逻辑

## Blocked by

None - can start immediately

## Technical Notes

参考：
- `.opencode/agents/collector.md` - 角色定义
- `AGENTS.md` - Agent 调用规范
- `knowledge/raw/github-trending-2026-05-03.json` - 现有示例数据
