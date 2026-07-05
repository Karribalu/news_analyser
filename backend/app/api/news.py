import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas import SearchResponse
from app.services.news import fetch_articles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


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
        logger.exception("Unexpected error during news search for query=%r", q)
        raise HTTPException(
            status_code=502, detail=f"News API error: {str(exc)}")
