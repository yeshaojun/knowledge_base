#!/usr/bin/env python3
"""Fetch GitHub Trending repositories filtered by topics.

Usage:
    python fetch_trending.py [--topics TOPICS] [--limit LIMIT]

Examples:
    # Default: top 50, filter ai/llm/agent/ml
    python fetch_trending.py

    # Custom topics
    python fetch_trending.py --topics "ai,ml,deep-learning"

    # Custom limit
    python fetch_trending.py --limit 30
"""

import argparse
import json
import logging
import sys
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

GITHUB_TRENDING_URL = "https://github.com/trending"
DEFAULT_TOPICS = ["ai", "llm", "agent", "ml", "machine-learning"]
DEFAULT_LIMIT = 50
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 1
USER_AGENT = "KnowledgeBaseBot/1.0"

TOPIC_KEYWORDS = [
    "ai",
    "artificial-intelligence",
    "llm",
    "large-language-model",
    "agent",
    "agents",
    "ml",
    "machine-learning",
    "deep-learning",
    "neural-network",
    "nlp",
    "natural-language-processing",
    "computer-vision",
    "gpt",
    "transformer",
    "pytorch",
    "tensorflow",
    "langchain",
    "openai",
    "claude",
    "chatbot",
    "rag",
    "reinforcement-learning",
    "diffusion",
    "stable-diffusion",
]


def extract_topics_from_description(description: str) -> list[str]:
    description_lower = description.lower()
    found_topics = []

    for keyword in TOPIC_KEYWORDS:
        if keyword in description_lower:
            found_topics.append(keyword)

    return found_topics


def fetch_trending_page() -> str | None:
    """Fetch GitHub Trending HTML page.

    Returns:
        HTML content string, or None on failure.
    """
    headers = {"User-Agent": USER_AGENT}

    try:
        logger.info(f"Fetching {GITHUB_TRENDING_URL}")
        response = requests.get(
            GITHUB_TRENDING_URL,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch trending page: {e}")
        return None


def parse_repository(article: Any) -> dict[str, Any] | None:
    """Parse a single repository from HTML article element.

    Args:
        article: BeautifulSoup element for repository article.

    Returns:
        Repository dict with name, url, stars, topics, description.
        Returns None if parsing fails.
    """
    try:
        h2_tag = article.find("h2")
        if not h2_tag:
            return None

        repo_link = h2_tag.find("a")
        if not repo_link:
            return None

        repo_path = repo_link.get("href", "").strip("/")
        if not repo_path:
            return None

        repo_url = f"https://github.com/{repo_path}"

        desc_tag = article.find("p", class_="col-9")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        stars = 0
        stars_link = article.find("a", href=lambda x: x and "stargazers" in x)
        if stars_link:
            stars_text = stars_link.get_text(strip=True).replace(",", "")
            if "k" in stars_text.lower():
                stars = int(float(stars_text.lower().replace("k", "")) * 1000)
            else:
                try:
                    stars = int(stars_text)
                except ValueError:
                    stars = 0

        topics = extract_topics_from_description(description)

        return {
            "name": repo_path,
            "url": repo_url,
            "stars": stars,
            "topics": topics,
            "description": description,
        }
    except Exception as e:
        logger.error(f"Failed to parse repository: {e}")
        return None


def filter_by_topics(
    repos: list[dict[str, Any]],
    topics: list[str],
) -> list[dict[str, Any]]:
    """Filter repositories by topics (case-insensitive OR logic).

    Args:
        repos: List of repository dicts.
        topics: List of topics to filter by.

    Returns:
        Filtered list of repositories.
    """
    if not topics:
        return repos

    topics_lower = [t.lower() for t in topics]
    filtered = []

    for repo in repos:
        repo_topics = [t.lower() for t in repo.get("topics", [])]
        description_lower = repo.get("description", "").lower()

        matches_topic = any(topic in repo_topics for topic in topics_lower)
        matches_desc = any(topic in description_lower for topic in topics_lower)

        if matches_topic or matches_desc:
            filtered.append(repo)

    return filtered


def fetch_trending(
    topics: list[str] | None = None,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    """Fetch GitHub Trending repositories filtered by topics.

    Args:
        topics: List of topics to filter by. None uses defaults.
        limit: Maximum number of repositories to return.

    Returns:
        List of repository dicts. Empty list on failure.
    """
    if topics is None:
        topics = DEFAULT_TOPICS

    html = fetch_trending_page()
    if not html:
        logger.error("Failed to fetch trending page, returning empty list")
        return []

    try:
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("article", class_="Box-row")
        logger.info(f"Found {len(articles)} repositories on trending page")
    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        return []

    repos = []
    for article in articles:
        repo = parse_repository(article)
        if repo:
            repos.append(repo)

    logger.info(f"Successfully parsed {len(repos)} repositories")

    filtered_repos = filter_by_topics(repos, topics)
    logger.info(
        f"Filtered to {len(filtered_repos)} repositories "
        f"matching topics: {topics}"
    )

    result = filtered_repos[:limit]
    logger.info(f"Returning {len(result)} repositories (limit: {limit})")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub Trending repositories filtered by topics"
    )
    parser.add_argument(
        "--topics",
        type=str,
        default=",".join(DEFAULT_TOPICS),
        help="Comma-separated list of topics to filter by",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of repositories to return",
    )

    args = parser.parse_args()

    topics = [t.strip().lower() for t in args.topics.split(",") if t.strip()]

    repos = fetch_trending(topics=topics, limit=args.limit)

    print(json.dumps(repos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
