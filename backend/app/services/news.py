import logging
import time

import httpx
from app.config import settings
from app.schemas import Article

logger = logging.getLogger(__name__)

# In-memory cache: (category, page, page_size) -> (articles, total, fetched_at_monotonic)
_headlines_cache: dict[tuple[str, int, int],
                       tuple[list[Article], int, float]] = {}
_HEADLINES_TTL = 30 * 60  # 30 minutes


def fetch_headlines(
    category: str = "general",
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Article], int]:
    if not settings.gnews_headlines_url:
        raise ValueError("GNEWS_HEADLINES_URL is not configured")
    if not settings.gnews_api_key:
        raise ValueError("GNEWS_API_KEY is not configured")

    now = time.monotonic()
    cache_key = (category, page, page_size)
    cached = _headlines_cache.get(cache_key)
    if cached and now - cached[2] < _HEADLINES_TTL:
        logger.info("Headlines cache hit for category=%r page=%d page_size=%d (age=%.0fs)",
                    category, page, page_size, now - cached[2])
        return cached[0], cached[1]

    params = {
        "category": category,
        "lang": "en",
        "max": page_size,
        "page": page,
        "apikey": settings.gnews_api_key,
    }

    logger.debug("Calling GNews headlines API: url=%r category=%r page=%d",
                 settings.gnews_headlines_url, category, page)
    response = httpx.get(settings.gnews_headlines_url,
                         params=params, timeout=30.0)
    logger.info("GNews headlines response status=%d category=%r",
                response.status_code, category)
    response.raise_for_status()
    data = response.json()

    total_articles = data.get("totalArticles", 0)
    articles = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                title=item.get("title", ""),
                description=item.get("description", ""),
                content=item.get("content", ""),
                image=item.get("image") or None,
                url=item.get("url", ""),
                source=item.get("source", {}).get("name") if isinstance(
                    item.get("source"), dict) else item.get("source"),
                published_at=item.get("publishedAt", "")
            )
        )

    logger.info("Parsed %d headline(s) from GNews response (totalArticles=%d)",
                len(articles), total_articles)
    _headlines_cache[cache_key] = (articles, total_articles, now)
    return articles, total_articles


def fetch_articles(
    query: str,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Article], int]:
    if not settings.gnews_base_url:
        raise ValueError("GNEWS_BASE_URL is not configured")
    if not settings.gnews_api_key:
        raise ValueError("GNEWS_API_KEY is not configured")

    params = {
        "q": query,
        "max": page_size,
        "page": page,
        "lang": "en",
        "apikey": settings.gnews_api_key
    }

    logger.debug("Calling GNews API: url=%r query=%r max=%d page=%d",
                 settings.gnews_base_url, query, page_size, page)
    response = httpx.get(settings.gnews_base_url, params=params, timeout=30.0)
    logger.info("GNews API response status=%d for query=%r",
                response.status_code, query)
    response.raise_for_status()
    data = response.json()

    total_articles = data.get("totalArticles", 0)
    articles = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                title=item.get("title", ""),
                description=item.get("description", ""),
                content=item.get("content", ""),
                image=item.get("image") or None,
                url=item.get("url", ""),
                source=item.get("source", {}).get("name") if isinstance(
                    item.get("source"), dict) else item.get("source"),
                published_at=item.get("publishedAt", "")
            )
        )

    logger.info("Parsed %d article(s) from GNews response (totalArticles=%d)",
                len(articles), total_articles)
    return articles, total_articles
