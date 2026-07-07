import json
import logging
import re
from openai import OpenAI
from app.config import settings
from app.schemas import Article, Sentiment

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)


def analyze_article(article: Article) -> dict:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    prompt = f""" You are a helpful news assistant. Read the article below and produce a JSON object with exactly two keys:
- "summary": a concise 6-7 sentence summary of the article.
- "sentiment": one of "positive", "neutral", or "negative" based on the overall tone of the article.

Respond with ONLY valid JSON. Do not include markdown code fences or any extra text.

Title: {article.title}
Content: {article.content or article.description or "N/A"}

"""
    logger.info("Sending article to OpenAI: model=%r title=%r",
                settings.openai_model, article.title)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You summarize news articles and classify sentiment. Always return valid JSON."},            {
                "role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=300
    )
    logger.debug("OpenAI raw response: %s",
                 response.choices[0].message.content)

    content = response.choices[0].message.content or "{}"
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "",
                     content.strip(), flags=re.MULTILINE)

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse OpenAI response as JSON: %s", content)
        raise ValueError(
            f"OpenAI response was not valid JSON: {content}") from exc

    summary = result.get("summary", "").strip()
    raw_sentiment = result.get("sentiment", "neutral").strip().lower()

    if raw_sentiment not in {s.value for s in Sentiment}:
        logger.warning(
            "Unexpected sentiment value %r — defaulting to 'neutral'", raw_sentiment)
        raw_sentiment = "neutral"

    sentiment = Sentiment(raw_sentiment)
    logger.info("Analysis complete: sentiment=%r for title=%r",
                sentiment.value, article.title)

    return {"summary": summary, "sentiment": sentiment}
