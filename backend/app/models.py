from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True)
    article_url = Column(String(2048), unique=True, nullable=False, index=True)
    article_title = Column(String(1024), nullable=False)
    article_description = Column(Text, nullable=True)
    article_source = Column(String(512), nullable=True)
    article_published_at = Column(String(64), nullable=True)
    summary = Column(Text, nullable=False)
    sentiment = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
