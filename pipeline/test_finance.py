import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from model_client import create_client, chat_with_retry

async def test_finance_analysis():
    client = create_client()
    
    test_items = [
        {
            "title": "美股三大指数创新高，科技股领涨",
            "description": "标普500指数和纳斯达克指数延续涨势，科技股表现强劲。英伟达、苹果、微软等大型科技股涨幅明显。",
            "source": "财经新闻"
        },
        {
            "title": "美联储维持利率不变，暗示年内降息",
            "description": "美联储宣布维持联邦基金利率目标区间在5.25%-5.50%不变，但表示年内可能降息三次。",
            "source": "宏观经济"
        },
        {
            "title": "AI初创公司融资10亿美元，估值突破百亿",
            "description": "某AI基础设施初创公司完成新一轮融资，由顶级VC领投，公司估值达到120亿美元。",
            "source": "投资新闻"
        }
    ]
    
    prompt_template = """分析以下内容并提供：
1. 中文摘要（50-100字，精炼概括核心价值）
2. 价值评分（1-10分）：
   - 技术类：创新性、实用性、成熟度
   - 财经类：投资价值、市场影响、信息质量
   - 研究类：学术价值、方法创新、结论可靠性
3. 3-5个相关标签
4. 分类：从 [llm, agent, tool, research, application, finance, news] 中选一个
5. 重要性：从 [high, medium, low] 中选一个

标题：{title}
描述：{description}
来源：{source}

请用JSON格式回复：
{{"summary": "中文摘要...", "score": N, "tags": [...], "category": "...", "importance": "..."}}"""

    for item in test_items:
        prompt = prompt_template.format(**item)
        messages = [{"role": "user", "content": prompt}]
        
        response = await chat_with_retry(client, messages, max_retries=2)
        
        print(f"\n{'='*60}")
        print(f"标题: {item['title']}")
        print(f"{'='*60}")
        print(response.content)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_finance_analysis())
