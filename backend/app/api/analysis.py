import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.repositories.analysis import AnalysisRepository
from app.schemas import AnalyzeRequest, AnalysisResponse
from app.services.openai import analyze_article

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def analyze(req: AnalyzeRequest,
            repo: AnalysisRepository = Depends(get_analysis_repository)):
    logger.info("Analyze request for article url=%r", req.article.url)
    existing = repo.get_by_url(req.article.url)
    if existing:
        logger.info("Cache hit for url=%r (id=%s)",
                    req.article.url, existing.id)
        return existing

    logger.info(
        "No cached analysis found; calling OpenAI for url=%r", req.article.url)
    try:
        ai_result = analyze_article(req.article)
    except ValueError as exc:
        logger.error("OpenAI configuration error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception(
            "Unexpected error from OpenAI for url=%r", req.article.url)
        raise HTTPException(
            status_code=502, detail=f"OpenAI API error: {str(exc)}")

    result = repo.create(
        req.article, ai_result["summary"], ai_result["sentiment"])
    logger.info("Analysis created with id=%s for url=%r",
                result.id, req.article.url)
    return result


@router.get("", response_model=List[AnalysisResponse])
def list_analysis(repo: AnalysisRepository = Depends(get_analysis_repository)):
    results = repo.list_all()
    logger.info("Listing all analyses: %d record(s) returned", len(results))
    return results


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    repo: AnalysisRepository = Depends(get_analysis_repository)
):
    logger.info("Delete request for analysis id=%s", analysis_id)
    analysis = repo.get_by_id(analysis_id)
    if not analysis:
        logger.warning("Analysis id=%s not found", analysis_id)
        raise HTTPException(status_code=404, detail="Analysis not found")

    repo.delete(analysis)
    logger.info("Analysis id=%s deleted", analysis_id)
    return {"message": "Analysis deleted"}
