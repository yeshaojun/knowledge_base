#!/usr/bin/env python3
"""Knowledge base automation pipeline.

Four-step pipeline: Collect → Analyze → Organize → Save.

Usage:
    python pipeline/pipeline.py --sources github,rss --limit 20
    python pipeline/pipeline.py --sources github --limit 5 --dry-run
    python pipeline/pipeline.py --verbose
"""

import argparse
import asyncio
import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from model_client import create_client, chat_with_retry
except ImportError:
    from pipeline.model_client import create_client, chat_with_retry

logger = logging.getLogger(__name__)


@dataclass
class RawItem:
    """Raw collected item."""

    title: str
    url: str
    source: str
    source_type: str
    description: str = ""
    collected_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Article:
    """Processed article."""

    id: str
    title: str
    source_url: str
    source_type: str
    summary: str
    tags: list[str]
    category: str
    importance: str
    status: str
    created_at: str
    updated_at: str
    distributed_to: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_RAW_DIR = BASE_DIR / "knowledge" / "raw"
KNOWLEDGE_ARTICLES_DIR = BASE_DIR / "knowledge" / "articles"
KNOWLEDGE_ANALYSIS_DIR = BASE_DIR / "knowledge" / "analysis"
RSS_CONFIG_PATH = BASE_DIR / "pipeline" / "rss_sources.yaml"

GITHUB_SEARCH_QUERY = "ai OR llm OR machine-learning OR agent language:Python"
GITHUB_API_BASE = "https://api.github.com"

ANALYSIS_PROMPT = """分析以下内容并提供：
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


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def generate_id(source: str, date: Optional[datetime] = None) -> str:
    """Generate unique article ID."""
    if date is None:
        date = datetime.now(timezone.utc)
    date_str = date.strftime("%Y%m%d")
    hash_input = f"{source}{date.isoformat()}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:3]
    return f"{source.split('/')[0] if '/' in source else source}-{date_str}-{hash_suffix}"


def parse_rss_feed(xml_content: str, source_name: str) -> list[RawItem]:
    """Parse RSS feed with regex (no external library)."""
    items = []

    item_pattern = re.compile(r"<item>(.*?)</item>", re.DOTALL)
    title_pattern = re.compile(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", re.DOTALL)
    link_pattern = re.compile(r"<link>(.*?)</link>", re.DOTALL)
    desc_pattern = re.compile(
        r"<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>",
        re.DOTALL,
    )

    for match in item_pattern.finditer(xml_content):
        item_xml = match.group(1)

        title_match = title_pattern.search(item_xml)
        title = ""
        if title_match:
            title = title_match.group(1) or title_match.group(2) or ""
            title = title.strip()

        link_match = link_pattern.search(item_xml)
        url = link_match.group(1).strip() if link_match else ""

        desc_match = desc_pattern.search(item_xml)
        description = ""
        if desc_match:
            description = desc_match.group(1) or desc_match.group(2) or ""
            description = re.sub(r"<[^>]+>", "", description).strip()

        if title and url:
            items.append(
                RawItem(
                    title=title,
                    url=url,
                    source=source_name,
                    source_type="rss",
                    description=description[:500],
                    collected_at=datetime.now(timezone.utc).isoformat(),
                )
            )

    return items


async def collect_from_github(limit: int, client: httpx.AsyncClient) -> list[RawItem]:
    """Collect items from GitHub Search API."""
    logger.info(f"Collecting from GitHub (limit: {limit})")

    items = []
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": GITHUB_SEARCH_QUERY,
        "sort": "stars",
        "order": "desc",
        "per_page": min(limit, 100),
    }
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "KnowledgeBaseBot/1.0",
    }

    try:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        for repo in data.get("items", [])[:limit]:
            items.append(
                RawItem(
                    title=repo["full_name"],
                    url=repo["html_url"],
                    source="github",
                    source_type="github_search",
                    description=repo.get("description", "") or "",
                    collected_at=datetime.now(timezone.utc).isoformat(),
                    metadata={
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language", ""),
                        "forks": repo.get("forks_count", 0),
                    },
                )
            )

        logger.info(f"Collected {len(items)} items from GitHub")
    except Exception as e:
        logger.error(f"GitHub collection failed: {e}")

    return items


async def collect_from_rss(limit: int, client: httpx.AsyncClient) -> list[RawItem]:
    """Collect items from RSS feeds."""
    logger.info(f"Collecting from RSS feeds (limit: {limit})")

    import yaml

    items = []

    try:
        with open(RSS_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load RSS config: {e}")
        return items

    enabled_sources = [s for s in config.get("sources", []) if s.get("enabled", False)]

    items_per_source = max(1, limit // max(len(enabled_sources), 1))

    for source in enabled_sources:
        if len(items) >= limit:
            break

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            }

            response = await client.get(
                source["url"],
                timeout=15.0,
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()

            feed_items = parse_rss_feed(response.text, source["name"])
            items.extend(feed_items[:items_per_source])

            logger.info(f"Collected {len(feed_items)} from {source['name']}")
        except asyncio.TimeoutError:
            logger.warning(f"RSS feed {source['name']} timeout")
        except httpx.HTTPStatusError as e:
            logger.warning(f"RSS feed {source['name']} HTTP {e.response.status_code}")
        except Exception as e:
            logger.warning(f"RSS feed {source['name']} failed: {type(e).__name__}: {e}")

        await asyncio.sleep(0.5)

    logger.info(f"Collected {len(items)} items from RSS feeds")
    return items[:limit]


async def analyze_item(item: RawItem, llm_client: Any, dry_run: bool) -> Optional[Article]:
    """Analyze item with LLM."""
    if dry_run:
        logger.debug(f"Dry-run: skipping analysis for {item.url}")
        return Article(
            id=generate_id(item.source),
            title=item.title,
            source_url=item.url,
            source_type=item.source_type,
            summary=item.description[:100] or "No summary",
            tags=["ai", "auto"],
            category="application",
            importance="medium",
            status="draft",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            metadata=item.metadata,
        )

    prompt = ANALYSIS_PROMPT.format(
        title=item.title,
        description=item.description[:500],
        source=item.source,
    )

    try:
        messages = [{"role": "user", "content": prompt}]
        response = await chat_with_retry(llm_client, messages, max_retries=2)

        content = response.content.strip()

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            analysis = {
                "summary": item.description[:100] or "No summary",
                "score": 5,
                "tags": ["ai"],
                "category": "application",
                "importance": "medium",
            }

        return Article(
            id=generate_id(item.source),
            title=item.title,
            source_url=item.url,
            source_type=item.source_type,
            summary=analysis.get("summary", item.description[:100] or "No summary"),
            tags=analysis.get("tags", ["ai"]),
            category=analysis.get("category", "application"),
            importance=analysis.get("importance", "medium"),
            status="draft",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                **item.metadata,
                "score": analysis.get("score", 5),
            },
        )
    except Exception as e:
        logger.error(f"Analysis failed for {item.url}: {e}")
        return None


def organize_items(articles: list[Article]) -> list[Article]:
    """Deduplicate and validate articles."""
    logger.info("Organizing articles (dedup + validation)")

    seen_urls = set()
    unique_articles = []

    for article in articles:
        if article.source_url in seen_urls:
            logger.debug(f"Duplicate: {article.source_url}")
            continue

        if len(article.summary) < 20:
            logger.debug(f"Summary too short: {article.source_url}")
            article.summary = f"Content from {article.title}"

        if len(article.tags) < 1:
            article.tags = ["ai"]

        article.tags = article.tags[:7]

        seen_urls.add(article.source_url)
        unique_articles.append(article)

    logger.info(f"Organized: {len(unique_articles)} unique articles")
    return unique_articles


def save_raw_items(items: list[RawItem], dry_run: bool) -> None:
    """Save raw items to knowledge/raw/."""
    if dry_run:
        logger.info("Dry-run: skipping raw data save")
        return

    if not items:
        return

    KNOWLEDGE_RAW_DIR.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_raw.json"
    filepath = KNOWLEDGE_RAW_DIR / filename

    existing_items = []
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_items = data.get("items", [])
        except Exception:
            pass

    new_items = [asdict(item) for item in items]

    all_items = existing_items + new_items

    output = {
        "fetch_id": f"raw_{date_str.replace('-', '')}",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "items_count": len(all_items),
        "items": all_items,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(new_items)} raw items to {filepath}")


def save_articles(articles: list[Article], dry_run: bool) -> int:
    """Save articles to knowledge/articles/YYYY-MM-DD/."""
    if dry_run:
        logger.info("Dry-run: skipping articles save")
        return 0

    if not articles:
        return 0

    KNOWLEDGE_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    saved_count = 0
    for article in articles:
        date_str = datetime.now().strftime("%Y-%m-%d")

        if article.created_at:
            try:
                dt = datetime.fromisoformat(article.created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        date_dir = KNOWLEDGE_ARTICLES_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{article.id}.json"
        filepath = date_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(article), f, ensure_ascii=False, indent=2)

        saved_count += 1

    logger.info(f"Saved {saved_count} articles to {KNOWLEDGE_ARTICLES_DIR}")
    return saved_count


def save_analysis(articles: list[Article], raw_items: list[RawItem], dry_run: bool) -> None:
    """Save analysis result to knowledge/analysis/."""
    if dry_run:
        logger.info("Dry-run: skipping analysis save")
        return

    if not articles:
        return

    KNOWLEDGE_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"analysis-{date_str}.json"
    filepath = KNOWLEDGE_ANALYSIS_DIR / filename

    analysis_result = {
        "source_file": f"raw-{date_str}.json",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "skill": "pipeline-auto",
        "total_items": len(articles),
        "analysis": [
            {
                "name": article.title,
                "url": article.source_url,
                "summary": article.summary,
                "score": article.metadata.get("score", 5),
                "suggested_tags": article.tags,
                "category": article.category,
                "importance": article.importance,
            }
            for article in articles
        ],
    }

    categories_count = {}
    for article in articles:
        cat = article.category or "unknown"
        categories_count[cat] = categories_count.get(cat, 0) + 1

    analysis_result["trends"] = {
        "category_distribution": categories_count,
        "high_importance_count": sum(1 for a in articles if a.importance == "high"),
        "avg_score": sum(a.metadata.get("score", 5) for a in articles) / len(articles) if articles else 0,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved analysis to {filepath}")


async def run_pipeline(
    sources: list[str],
    limit: int,
    dry_run: bool,
    verbose: bool,
) -> dict[str, Any]:
    """Execute the full pipeline."""
    stats = {
        "collected": 0,
        "analyzed": 0,
        "organized": 0,
        "saved": 0,
        "errors": [],
    }

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        raw_items: list[RawItem] = []

        if "github" in sources:
            github_items = await collect_from_github(limit, http_client)
            raw_items.extend(github_items)

        if "rss" in sources:
            rss_items = await collect_from_rss(limit, http_client)
            raw_items.extend(rss_items)

        stats["collected"] = len(raw_items)

        if not raw_items:
            logger.warning("No items collected")
            return stats

        save_raw_items(raw_items, dry_run)

        llm_client = None if dry_run else create_client()

        articles: list[Article] = []

        try:
            for item in raw_items:
                article = await analyze_item(item, llm_client, dry_run)
                if article:
                    articles.append(article)
                    stats["analyzed"] += 1
        finally:
            if llm_client:
                await llm_client.close()

        organized = organize_items(articles)
        stats["organized"] = len(organized)

        saved = save_articles(organized, dry_run)
        stats["saved"] = saved

        save_analysis(organized, raw_items, dry_run)

    return stats


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Knowledge base automation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline/pipeline.py --sources github,rss --limit 20
  python pipeline/pipeline.py --sources github --limit 5 --dry-run
  python pipeline/pipeline.py --verbose
        """,
    )

    parser.add_argument(
        "--sources",
        type=str,
        default="github,rss",
        help="Data sources: github, rss, or both (default: github,rss)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum items to collect per source (default: 20)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving or API calls",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    sources = [s.strip().lower() for s in args.sources.split(",")]

    valid_sources = {"github", "rss"}
    invalid = set(sources) - valid_sources
    if invalid:
        logger.error(f"Invalid sources: {invalid}")
        return 1

    logger.info("=" * 60)
    logger.info("Knowledge Base Pipeline")
    logger.info("=" * 60)
    logger.info(f"Sources: {sources}")
    logger.info(f"Limit: {args.limit}")
    logger.info(f"Dry-run: {args.dry_run}")
    logger.info(f"Verbose: {args.verbose}")
    logger.info("=" * 60)

    stats = asyncio.run(run_pipeline(
        sources=sources,
        limit=args.limit,
        dry_run=args.dry_run,
        verbose=args.verbose,
    ))

    logger.info("=" * 60)
    logger.info("Pipeline Complete")
    logger.info("=" * 60)
    logger.info(f"Collected: {stats['collected']}")
    logger.info(f"Analyzed:  {stats['analyzed']}")
    logger.info(f"Organized: {stats['organized']}")
    logger.info(f"Saved:     {stats['saved']}")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
