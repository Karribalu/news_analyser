import logging

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas import SearchResponse
from app.services.news import fetch_articles, fetch_headlines

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


def _handle_httpx_error(exc: Exception, context: str) -> HTTPException:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
        logger.warning("%s: GNews rate limit hit", context)
        return HTTPException(
            status_code=429,
            detail="News API rate limit reached. Please wait a moment and try again.",
        )
    logger.exception("%s: unexpected error", context)
    return HTTPException(status_code=502, detail=f"News API error: {exc}")


@router.get("/headlines", response_model=SearchResponse)
def get_headlines(category: str = Query("general")):
    logger.info("Headlines request: category=%r", category)
    try:
        articles = fetch_headlines(category)
        logger.info("Headlines returned %d article(s)", len(articles))
        return SearchResponse(articles=articles)
    except ValueError as exc:
        logger.error("Headlines configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise _handle_httpx_error(exc, "get_headlines")


@router.get("", response_model=SearchResponse)
def search_news(
    q: str = Query(..., min_length=1, max_length=200),
    max_results: int = Query(10, ge=1, le=20)
):
    logger.info("News search: query=%r max_results=%d", q, max_results)
    try:
        articles = fetch_articles(q, max_results)
        logger.info(
            "News search returned %d article(s) for query=%r", len(articles), q)
        return SearchResponse(articles=articles)
    except ValueError as exc:
        logger.error("News search configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise _handle_httpx_error(exc, f"search_news query={q!r}")
