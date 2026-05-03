# 编码规范 v0.2

## 变更历史

- **v0.2** (2025-05-03): 整合完整规范体系：格式化、测试、CI、依赖、错误处理、Git、维护流程
- **v0.1** (2025-05-03): 初始版本

---

## 1. 格式化与风格

### Python

- **格式化工具**：`ruff format`（统一使用，放弃 black）
- **Lint 工具**：`ruff check`
- **类型检查**：`mypy`（警告级别）
- **代码风格**：PEP 8

### TypeScript（未来规划）

用于管理后台开发。

- **框架**：Next.js（App Router）
- **strict mode**：开启
- **类型定义**：放在 `src/types/`

---

## 2. 文档字符串

### 必须写文档

- 模块公开函数（非 `_` 前缀）
- 类公开方法（非 `_` 前缀）
- 类定义本身

### 允许省略

- 私有方法（`_` 前缀）
- 模块内部函数（`_` 前缀）
- 简单 property（getter/setter）
- `__init__` 方法（类文档已覆盖）

### 最低要求

- 一句话描述函数做什么
- 如果有参数/返回值，必须说明
- 如果会抛出异常，必须说明

### 示例

```python
# ✅ 简单函数，一句话即可
def format_timestamp(dt: datetime) -> str:
    """将 datetime 转换为 ISO 8601 格式字符串。"""

# ✅ 复杂函数，完整文档
def fetch_trending(limit: int = 30) -> list[dict]:
    """从 GitHub Trending 采集 AI 项目数据。
    
    Args:
        limit: 返回项目数量，默认 30。
    
    Returns:
        项目列表，每个元素包含 name、url、description、stars 等字段。
    
    Raises:
        NetworkError: 网络请求失败时抛出。
    """
```

---

## 3. 魔法字符串

### 分类处理

| 类型 | 示例 | 是否允许 | 如何处理 |
|------|------|----------|----------|
| **配置常量** | 文件路径、API URL | ✅ 允许 | 提取到 `constants.py` 或配置文件 |
| **领域枚举** | status: "pending" | ❌ 禁止裸字符串 | 用 `Enum` 或 `Literal` 类型 |
| **用户文本** | 日志、UI 文字、错误消息 | ✅ 允许 | 建议集中管理（i18n 预留） |

### 示例

```python
# ❌ 禁止
status = "pending"
category = "agent_framework"

# ✅ 正确
from enum import Enum

class ArticleStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISTRIBUTED = "distributed"

status = ArticleStatus.PENDING
```

---

## 4. 债务标记

### 分类

| 类型 | 标签 | 处理方式 |
|------|------|----------|
| **债务标记** | TODO, FIXME, XXX, HACK | 禁止进入 main，必须在合并前解决或转为 Issue |
| **说明标记** | NOTE, WARNING, INFO | 允许，是代码文档的一部分 |

### 例外处理

紧急 hotfix 可临时绕过，但必须：
1. 创建 GitHub Issue 追踪债务
2. 在代码中注释：`# FIXME(#123): 临时绕过，待修复`
3. 3 个工作日内修复

---

## 5. 测试规范

### 覆盖率要求

- **目标**：核心模块覆盖率 ≥ 80%
- **计算范围**：`agents/`、`skills/`，排除：
  - `__init__.py`
  - `config.py` / `settings.py`
  - `scripts/`
  - `main.py`

### 必须测试

- 数据转换逻辑
- 业务规则（状态流转、验证）
- 工具函数（时间格式化、文本处理）

### 允许豁免

- 外部 API 调用（用 mock 或集成测试）
- LLM 调用（用 mock 或单独的集成测试套件）
- 纯数据模型（无逻辑）

---

## 6. CI 规范

### PR 检查（阻断合并）

1. `ruff format --check` → 格式不通过，阻断
2. `ruff check` → 代码质量问题，阻断
3. `pytest` → 测试失败，阻断

### PR 检查（仅警告）

1. `mypy` → 类型问题，警告但不阻断
2. 覆盖率 < 80% → 警告但不阻断

### Main 分支额外检查

1. 覆盖率 < 80% → 阻断部署

---

## 7. 依赖管理

### 添加依赖流程

1. 搜索是否已有类似功能的现有依赖
2. 评估：维护状态、Star 数、Issue 响应速度
3. 添加到对应分组：
   - `dependencies`：生产依赖
   - `dev-dependencies`：开发/测试依赖
4. Commit 时包含：`uv.lock` 变更

### 版本策略

- 生产依赖：`>=x.y.z,<x+1.0.0`（允许 minor/patch 更新）
- 开发依赖：固定版本 `==x.y.z`
- 每月检查安全更新：`uv audit`

### 许可证限制

- ✅ 允许：MIT, Apache-2.0, BSD
- ⚠️ 审查：LGPL
- ❌ 禁止：GPL, AGPL

### 依赖审查

- 新依赖必须说明用途
- 核心依赖需在 `AGENTS.md` 技术栈表格中记录

---

## 8. 错误处理

### 自定义异常体系

```
KnowledgeBaseError（基类）
├── FetchError（采集相关）
│   ├── NetworkError
│   └── RateLimitError
├── AnalyzeError（分析相关）
│   ├── LLMError
│   └── ParseError
└── DistributeError（分发相关）
```

### 异常传播原则

- Agent 边界向上传播：Collector → 调度器
- 跨系统边界记录日志：外部 API 调用
- 用户可见错误本地化：管理后台 UI

### 重试策略

| 错误类型 | 重试策略 |
|----------|----------|
| 网络错误 | 指数退避重试（最多 3 次） |
| 速率限制 | 等待后重试 |
| LLM 错误 | 重试 1 次（成本考虑） |
| 解析错误 | 不重试（数据问题） |

---

## 9. Git 规范

### 分支策略

```
main（受保护）
  ↑
feature/* ← PR（必须 1 个 approve）
hotfix/* ← PR（紧急修复）
```

### 分支命名

- `feature/add-hacker-news-source`
- `fix/rate-limit-handling`
- `docs/update-coding-standards`

### Commit Message

格式：`<type>(<scope>): <description>`

**类型**：
- `feat`：新功能
- `fix`：修复 bug
- `docs`：文档变更
- `style`：代码格式（不影响功能）
- `refactor`：重构
- `test`：测试相关
- `chore`：构建/工具/依赖

**范围**：
- `collector` | `analyzer` | `formatter` | `config`

**示例**：
```bash
feat(collector): add Hacker News data source
fix(analyzer): handle empty response from LLM
docs: update coding standards
```

### PR 规范

**标题格式**：同 commit message

**描述模板**：
```markdown
## What
做了什么

## Why
为什么做

## Test
如何测试
```

**合并要求**：
- 需要 1 个 approve 才能合并
- 合并前 squash commits（可选）

---

## 10. 规范维护

### 修改流程

1. 提 Issue 讨论变更内容
2. 创建 PR 修改规范文档
3. 至少 1 人 Review + Approve
4. 合并后在团队群通知

### 版本管理

- **小改动**（澄清、示例）：不升级版本
- **新增规则**：minor 版本升级（v0.1 → v0.2）
- **重大变更**（删除规则、改变强制力）：major 版本升级（v0.x → v1.0）

### 新人 Onboarding

- 项目 README 链接到规范文档
- PR 模板包含规范检查清单

---

## 11. 强制力与执行

### 工具强制（不可绕过）

- `ruff format` → CI 阻断
- `ruff check` → CI 阻断
- `pytest` → CI 阻断

### Code Review 强制（PR 审查清单）

- [ ] 类型注解完整
- [ ] 文档字符串完整
- [ ] 无领域魔法字符串
- [ ] 无债务标记

### 债务管理

- 每周 Review 打开的技术债务 Issue
- 每月统计债务数量趋势
