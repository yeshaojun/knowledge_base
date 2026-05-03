import { $ } from "bun"
import type { Plugin } from "@opencode-ai/plugin"

export const plugin: Plugin = {
  name: "validate",
  hooks: {
    "tool.execute.after": async (input, output) => {
      const toolName = input.tool

      if (toolName !== "write" && toolName !== "edit") {
        return
      }

      const filePath = input.args?.file_path || input.args?.filePath

      if (!filePath || typeof filePath !== "string") {
        return
      }

      if (!filePath.includes("knowledge/articles/")) {
        return
      }

      if (!filePath.endsWith(".json")) {
        return
      }

      console.log(`[validate] Detecting JSON write: ${filePath}`)

      try {
        const result = await $`python3 hooks/validate_json.py ${filePath}`.nothrow()

        if (result.exitCode === 0) {
          console.log(`[validate] ✅ Validation passed: ${filePath}`)
        } else {
          console.error(`[validate] ❌ Validation failed: ${filePath}`)
          console.error(result.stderr.toString())
        }
      } catch (error) {
        console.error(`[validate] Error running validation: ${error}`)
      }
    },
  },
}
