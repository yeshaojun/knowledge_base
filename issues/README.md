# Issues 创建说明

## 仓库信息

- **仓库**: https://github.com/yeshaojun/knowledge_base
- **创建时间**: 2026-05-03
- **Issue 数量**: 8 个

---

## Issue 清单

| # | 标题 | 类型 | 阻塞项 |
|---|------|------|--------|
| 001 | Collector Agent - GitHub Trending 采集能力 | AFK | 无 |
| 002 | Analyzer Agent - 三维度标签分析能力 | AFK | #001 |
| 003 | Organizer Agent - Markdown 整理输出能力 | AFK | #002 |
| 004 | 调度器 - 每日定时触发 | AFK | #001, #002, #003 |
| 005 | 数据传递机制设计 | HITL | 无 |
| 006 | 错误处理策略 - 上游失败处理 | HITL | #004 |
| 007 | 重跑策略与幂等性 | AFK | #004, #006 |
| 008 | 进度追踪与监控 | AFK | #004 |

---

## 手动发布步骤

由于 GitHub CLI 不可用，请手动创建 issues：

### 方法一：GitHub 网页创建

1. 访问 https://github.com/yeshaojun/knowledge_base/issues/new
2. 复制 `issues/001-collector-github-trending.md` 内容
3. 标题：`Collector Agent - GitHub Trending 采集能力`
4. 粘贴内容到描述框
5. 点击 "Submit new issue"
6. 重复步骤 1-5，创建其余 7 个 issues

### 方法二：使用 gh CLI（如已安装）

```bash
# 认证
gh auth login

# 创建 issues
cd /Users/andy/study/knowledge_base

gh issue create --title "Collector Agent - GitHub Trending 采集能力" --body-file issues/001-collector-github-trending.md --label "needs-triage"
gh issue create --title "Analyzer Agent - 三维度标签分析能力" --body-file issues/002-analyzer-three-dimension-tags.md --label "needs-triage"
gh issue create --title "Organizer Agent - Markdown 整理输出能力" --body-file issues/003-organizer-markdown-output.md --label "needs-triage"
gh issue create --title "调度器 - 每日定时触发" --body-file issues/004-scheduler-daily-trigger.md --label "needs-triage"
gh issue create --title "数据传递机制设计" --body-file issues/005-data-transfer-mechanism.md --label "needs-triage"
gh issue create --title "错误处理策略 - 上游失败处理" --body-file issues/006-error-handling-upstream-failure.md --label "needs-triage"
gh issue create --title "重跑策略与幂等性" --body-file issues/007-rerun-idempotency.md --label "needs-triage"
gh issue create --title "进度追踪与监控" --body-file issues/008-progress-tracking-monitoring.md --label "needs-triage"
```

---

## 依赖关系图

```
#001 (Collector)
    ↓
#002 (Analyzer)
    ↓
#003 (Organizer)
    ↓
#004 (调度器)
    ↓
#006 (错误处理) ← #005 (数据传递设计) [并行]
    ↓              ↓
#007 (重跑策略)
    ↓
#008 (监控)

#005 独立，可并行启动
```

---

## 执行顺序建议

### Sprint 1: 核心能力
1. #005 数据传递机制设计 (HITL) - 先决策
2. #001 Collector 采集能力 (AFK)
3. #002 Analyzer 分析能力 (AFK)
4. #003 Organizer 整理能力 (AFK)

### Sprint 2: 调度与健壮性
5. #004 调度器 (AFK)
6. #006 错误处理策略 (HITL)
7. #007 重跑与幂等性 (AFK)

### Sprint 3: 可观测性
8. #008 进度追踪与监控 (AFK)

---

## 文件位置

```
knowledge_base/
└── issues/
    ├── 001-collector-github-trending.md
    ├── 002-analyzer-three-dimension-tags.md
    ├── 003-organizer-markdown-output.md
    ├── 004-scheduler-daily-trigger.md
    ├── 005-data-transfer-mechanism.md
    ├── 006-error-handling-upstream-failure.md
    ├── 007-rerun-idempotency.md
    └── 008-progress-tracking-monitoring.md
```
