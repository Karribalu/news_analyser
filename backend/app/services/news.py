import httpx
from app.config import settings
from app.schemas import Article


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

    response = httpx.get(settings.gnews_base_url, params=params, timeout=30.0)
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
    return articles
