import logging

from sqlalchemy.orm import Session

from app.models import Analysis
from app.schemas import Article, Sentiment

logger = logging.getLogger(__name__)


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_url(self, url: str) -> Analysis | None:
        logger.debug("DB lookup by url=%r", url)
        return self.db.query(Analysis).filter(Analysis.article_url == url).first()

    def get_by_id(self, analysis_id: str) -> Analysis | None:
        logger.debug("DB lookup by id=%s", analysis_id)
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def list_all(self) -> list[Analysis]:
        logger.debug("DB query: list all analyses")
        return self.db.query(Analysis).order_by(Analysis.created_at.desc()).all()

    def create(self, article: Article, summary: str, sentiment: Sentiment) -> Analysis:
        logger.info("Inserting new analysis for url=%r sentiment=%r",
                    article.url, sentiment)
        analysis = Analysis(
            article_url=article.url,
            article_title=article.title,
            article_description=article.description,
            article_source=article.source,
            article_published_at=article.published_at,
            summary=summary,
            sentiment=sentiment
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        logger.info("Analysis inserted with id=%s", analysis.id)
        return analysis

    def delete(self, analysis: Analysis) -> None:
        logger.info("Deleting analysis id=%s url=%r",
                    analysis.id, analysis.article_url)
        self.db.delete(analysis)
        self.db.commit()
        logger.info("Analysis id=%s deleted from DB", analysis.id)
