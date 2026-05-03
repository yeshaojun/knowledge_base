请帮我编写一个 OpenCode TypeScript 插件 .opencode/plugins/validate.ts：

需求：

1. 监听 tool.execute.after 事件
2. 当 Agent 使用 write 或 edit 工具写入 knowledge/articles/*.json 时触发
3. 触发时调用 python3 hooks/validate_json.py <file_path>
4. 使用 Bun Shell API（$ 模板字符串）执行命令
5. 必须使用 .nothrow() 而非 .quiet()（.quiet() 会导致 OpenCode 卡死）
6. 必须用 try/catch 包裹所有 shell 调用（未捕获异常会阻塞 Agent）

关键 API：

- import type { Plugin } from "@opencode-ai/plugin"
- input.tool 是工具名（如 "write"、"edit"）
- input.args.file_path 或 input.args.filePath 是文件路径
