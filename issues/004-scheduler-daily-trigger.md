# 调度器 - 每日定时触发

## Parent

基于 `speces/agent-prd.md` 需求拆分

## What to build

实现调度器，每天 UTC 0:00 触发完整采集流程：
- 触发 Collector → Analyzer → Organizer 串行执行
- 使用 Task 工具委派子 Agent
- 流程状态追踪

## Acceptance criteria

- [ ] 实现基于 cron 或 GitHub Actions 的定时触发
- [ ] 串行执行流程：collector → analyzer → organizer
- [ ] 使用 Task 工具委派子 Agent（遵循 Agent 调用规范）
- [ ] 执行日志记录
- [ ] 失败时发送告警（可选：Telegram/飞书）
- [ ] 文档：配置说明和运维手册

## Blocked by

- Issue #001 (Collector GitHub Trending 采集能力)
- Issue #002 (Analyzer 三维度标签分析能力)
- Issue #003 (Organizer Markdown 整理输出能力)

## Technical Notes

技术选型建议：
- GitHub Actions + schedule trigger
- 或 LangGraph 状态机编排
- 或简单 shell script + cron

参考：
- `AGENTS.md` - Agent 调用规范
