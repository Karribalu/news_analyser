import logging
import math

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas import PaginatedArticleResponse
from app.services.news import fetch_articles, fetch_headlines

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])

_DEFAULT_PAGE_SIZE = 10


def _handle_httpx_error(exc: Exception, context: str) -> HTTPException:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
        logger.warning("%s: GNews rate limit hit", context)
        return HTTPException(
            status_code=429,
            detail="News API rate limit reached. Please wait a moment and try again.",
        )
    logger.exception("%s: unexpected error", context)
    return HTTPException(status_code=502, detail=f"News API error: {exc}")


@router.get("/headlines", response_model=PaginatedArticleResponse)
def get_headlines(
    category: str = Query("general"),
    page: int = Query(1, ge=1),
    page_size: int = Query(_DEFAULT_PAGE_SIZE, ge=1, le=20),
):
    logger.info("Headlines request: category=%r page=%d page_size=%d",
                category, page, page_size)
    try:
        articles, total = fetch_headlines(category, page, page_size)
        total_pages = max(1, math.ceil(total / page_size))
        logger.info(
            "Headlines returned %d article(s) (page %d, total=%d)",
            len(articles), page, total,
        )
        return PaginatedArticleResponse(
            articles=articles,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except ValueError as exc:
        logger.error("Headlines configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise _handle_httpx_error(exc, "get_headlines")


@router.get("", response_model=PaginatedArticleResponse)
def search_news(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(_DEFAULT_PAGE_SIZE, ge=1, le=20),
):
    logger.info("News search: query=%r page=%d page_size=%d",
                q, page, page_size)
    try:
        articles, total = fetch_articles(q, page, page_size)
        total_pages = max(1, math.ceil(total / page_size))
        logger.info(
            "News search returned %d article(s) for query=%r (page %d, total=%d)",
            len(articles), q, page, total,
        )
        return PaginatedArticleResponse(
            articles=articles,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except ValueError as exc:
        logger.error("News search configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise _handle_httpx_error(exc, f"search_news query={q!r}")
