"""Tests for app.services.openai.analyze_article."""
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import Article, Sentiment
from app.services.openai import analyze_article


ARTICLE = Article(title="Test Article", url="https://example.com/article")
VALID_JSON = '{"summary": "A great summary.", "sentiment": "positive"}'


def test_analyze_article_success():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = VALID_JSON

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["summary"] == "A great summary."
    assert result["sentiment"] == Sentiment.Positive


def test_analyze_article_neutral_sentiment():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"summary": "Boring news.", "sentiment": "neutral"}'

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["sentiment"] == Sentiment.Neutral


def test_analyze_article_negative_sentiment():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"summary": "Bad news.", "sentiment": "negative"}'

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["sentiment"] == Sentiment.Negative


def test_analyze_article_strips_markdown_fences():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "```json\n" + VALID_JSON + "\n```"

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["summary"] == "A great summary."


def test_analyze_article_unknown_sentiment_defaults_to_neutral():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"summary": "Meh.", "sentiment": "UNKNOWN_GARBAGE"}'

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["sentiment"] == Sentiment.Neutral


def test_analyze_article_empty_json_uses_defaults():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "{}"

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["summary"] == ""
    assert result["sentiment"] == Sentiment.Neutral


def test_analyze_article_null_content_uses_defaults():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = None

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        result = analyze_article(ARTICLE)

    assert result["summary"] == ""


def test_analyze_article_invalid_json_raises_value_error():
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "not json at all"

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        with pytest.raises(ValueError, match="not valid JSON"):
            analyze_article(ARTICLE)


def test_analyze_article_raises_when_no_api_key(monkeypatch):
    monkeypatch.setattr("app.services.openai.settings.openai_api_key", "")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        analyze_article(ARTICLE)


def test_analyze_article_passes_correct_model(monkeypatch):
    monkeypatch.setattr("app.services.openai.settings.openai_model", "gpt-test-model")
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = VALID_JSON

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        analyze_article(ARTICLE)

    assert mock_client.chat.completions.create.call_args.kwargs["model"] == "gpt-test-model"


def test_analyze_article_includes_title_in_prompt():
    article = Article(title="Unique Article Headline XYZ", url="https://example.com/article")
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = VALID_JSON

    with patch("app.services.openai.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_completion
        analyze_article(article)

    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    user_message = next(m for m in messages if m["role"] == "user")
    assert "Unique Article Headline XYZ" in user_message["content"]
