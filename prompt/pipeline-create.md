请帮我编写一个 Python 模块 pipeline/model_client.py，作为统一的 LLM 调用客户端：

需求：

1. 支持 DeepSeek、Qwen、OpenAI 三种模型提供商
2. 通过环境变量切换：LLM_PROVIDER（默认 deepseek）、对应的 API_KEY
3. 使用 httpx 直接调用 OpenAI 兼容 API（不依赖 openai SDK）
4. 用抽象基类 LLMProvider 定义接口，OpenAICompatibleProvider 实现
5. 统一返回 LLMResponse dataclass，包含 content 和 Usage 用量统计
6. 包含带重试的 chat_with_retry() 函数（3次，指数退避）和 60 秒超时
7. 包含 Token 消耗估算和成本计算函数（USD 计价）
8. 包含 quick_chat() 便捷函数，一句话调用 LLM
9. 最后有 if __name__ == "__main__" 的测试代码

编码规范：遵循 PEP 8，Google 风格 docstring，使用 logging 不用 print


请帮我编写 pipeline/pipeline.py，一个四步知识库自动化流水线：

需求：
1. Step 1: 采集（Collect）— 从 GitHub Search API 和 RSS 源采集 AI 相关内容
2. Step 2: 分析（Analyze）— 调用 LLM 对每条内容进行摘要/评分/标签分析
3. Step 3: 整理（Organize）— 去重 + 格式标准化 + 校验
4. Step 4: 保存（Save）— 将文章保存为独立 JSON 文件到 knowledge/articles/

CLI 设计：
- python pipeline/pipeline.py --sources github,rss --limit 20   # 完整流水线
- python pipeline/pipeline.py --sources github --limit 5         # 只采集 GitHub
- python pipeline/pipeline.py --sources rss --limit 10           # 只采集 RSS
- python pipeline/pipeline.py --sources github --limit 5 --dry-run  # 干跑模式
- python pipeline/pipeline.py --verbose                          # 详细日志

关键约束：
- 采集层用 httpx 发 HTTP 请求，RSS 用简易正则解析
- 分析层调用 model_client 的 chat_with_retry()（需要 API Key）
- 采集数据存入 knowledge/raw/，最终文章存入 knowledge/articles/
- model_client 在同目录下，用 from model_client import create_provider, chat_with_retry

编码规范：遵循 PEP 8，用 argparse 解析参数，用 pathlib 处理路径

