import logging

import httpx
from app.config import settings
from app.schemas import Article

logger = logging.getLogger(__name__)


def fetch_articles(query: str, max_results: int = 10) -> list[Article]:
    if not settings.gnews_base_url:
        raise ValueError("GNEWS_BASE_URL is not configured")
    if not settings.gnews_api_key:
        raise ValueError("GNEWS_API_KEY is not configured")

    params = {
        "q": query,
        "max": max_results,
        "lang": "en",
        "apikey": settings.gnews_api_key
    }

    logger.debug("Calling GNews API: url=%r query=%r max=%d",
                 settings.gnews_base_url, query, max_results)
    response = httpx.get(settings.gnews_base_url, params=params, timeout=30.0)
    logger.info("GNews API response status=%d for query=%r",
                response.status_code, query)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("articles", []):
        articles.append(
            Article(
                title=item.get("title", ""),
                description=item.get("description", ""),
                url=item.get("url", ""),
                source=item.get("source", {}).get("name") if isinstance(
                    item.get("source"), dict) else item.get("source"),
                published_at=item.get("publishedAt", "")
            )
        )

    logger.info("Parsed %d article(s) from GNews response", len(articles))
    return articles
