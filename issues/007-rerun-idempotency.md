# 重跑策略与幂等性

## Parent

基于 `speces/agent-prd.md` 开放问题拆分

## What to build

实现重跑机制，保证幂等性：
- 支持手动触发重跑
- 不重复采集已存在的数据
- 不重复分析已处理的条目

## Acceptance criteria

- [ ] 实现基于 `fetch_id` 的去重机制
- [ ] 实现基于 `analyzed_at` 的幂等性检查
- [ ] 支持指定日期范围重跑
- [ ] 支持强制覆盖模式（可选）
- [ ] 重跑日志记录：记录重跑原因和范围
- [ ] 单元测试覆盖幂等性逻辑

## Blocked by

- Issue #004 (调度器每日定时触发)
- Issue #006 (错误处理策略)

## Technical Notes

**幂等性实现**：

```python
# Collector 幂等性
def fetch_trending(date: str):
    existing = read_raw_file(date)
    if existing and not force:
        return existing  # 已存在，不重复采集
    # 采集逻辑...

# Analyzer 幂等性
def analyze_items(date: str):
    raw = read_raw_file(date)
    analyzed_ids = get_analyzed_ids(date)
    items_to_analyze = [i for i in raw if i['id'] not in analyzed_ids]
    # 只分析未处理的条目...
```

**重跑命令示例**：
```bash
# 重跑指定日期
python -m knowledge_base.collector --date 2026-05-01 --force

# 重跑日期范围
python -m knowledge_base.scheduler --start 2026-05-01 --end 2026-05-03
```
