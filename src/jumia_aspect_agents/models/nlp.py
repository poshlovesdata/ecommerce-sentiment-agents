"""Data contracts for the aspect-based NLP pipeline."""

from typing import Literal

from pydantic import BaseModel, Field

SentimentLabel = Literal["positive", "negative", "neutral", "mixed"]
PipelineMode = Literal["rules", "llm"]


class CleanedReview(BaseModel):
    """Output of Agent 1: cleaned review text and product routing."""

    review_id: str
    original_text: str
    cleaned_text: str
    product_category: str
    normalized_terms: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AspectMention(BaseModel):
    """A single aspect discussed in a review."""

    aspect: str
    aspect_category: str
    evidence: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class AspectExtractionResult(BaseModel):
    """Output of Agent 2: aspects mentioned in the cleaned review."""

    review_id: str
    aspects: list[AspectMention] = Field(default_factory=list)


class BaselineSentiment(BaseModel):
    """VADER or fallback lexicon sentiment for the whole review/aspect text."""

    label: SentimentLabel
    compound: float = Field(ge=-1.0, le=1.0)
    positive: float = Field(default=0.0, ge=0.0, le=1.0)
    neutral: float = Field(default=0.0, ge=0.0, le=1.0)
    negative: float = Field(default=0.0, ge=0.0, le=1.0)


class AspectSentiment(BaseModel):
    """Output of Agent 3: contextual sentiment for one aspect."""

    review_id: str
    aspect: str
    aspect_category: str
    sentiment: SentimentLabel
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    evidence: str
    rationale: str
    baseline_sentiment: BaselineSentiment


class ProcessedAspectRecord(BaseModel):
    """Flattened row saved for analysis and dashboarding."""

    review_id: str
    product_name: str
    product_url: str
    sku: str | None = None
    review_title: str | None = None
    review_body: str | None = None
    review_text: str
    star_rating: int | None = None
    review_date: str | None = None
    reviewer_name: str | None = None
    verified_purchase: bool = False
    source_url: str
    scraped_at: str | None = None
    product_category: str
    cleaned_text: str
    aspect: str
    aspect_category: str
    aspect_evidence: str
    aspect_confidence: float
    vader_label: SentimentLabel
    vader_compound: float
    vader_positive: float
    vader_neutral: float
    vader_negative: float
    contextual_sentiment: SentimentLabel
    contextual_sentiment_score: float
    contextual_rationale: str
    pipeline_mode: PipelineMode
