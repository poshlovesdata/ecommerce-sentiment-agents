"""LangGraph orchestration for the multi-agent NLP pipeline."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TypedDict

import pandas as pd
from langgraph.graph import END, START, StateGraph
from loguru import logger

from jumia_aspect_agents.agents.llm import PydanticAIAgentRunner
from jumia_aspect_agents.agents.rules import (
    RuleBasedAspectExtractor,
    RuleBasedCleanerRouter,
    RuleBasedContextualClassifier,
    combine_review_text,
)
from jumia_aspect_agents.analysis.sentiment import BaselineSentimentAnalyzer
from jumia_aspect_agents.config import settings
from jumia_aspect_agents.models.nlp import (
    AspectExtractionResult,
    AspectMention,
    AspectSentiment,
    CleanedReview,
    PipelineMode,
    ProcessedAspectRecord,
)
from jumia_aspect_agents.models.reviews import RawReview
from jumia_aspect_agents.utils.io import write_records_csv_json


class ReviewPipelineState(TypedDict, total=False):
    """State passed between LangGraph nodes for one review."""

    review_id: str
    raw_review: RawReview
    cleaned_review: CleanedReview
    extracted_aspects: AspectExtractionResult
    aspect_sentiments: list[AspectSentiment]


class AspectSentimentPipeline:
    """Process raw Jumia reviews into aspect-level sentiment rows."""

    def __init__(self, *, mode: PipelineMode = "rules") -> None:
        self.mode = mode
        self.baseline = BaselineSentimentAnalyzer()
        self.cleaner = RuleBasedCleanerRouter()
        self.extractor = RuleBasedAspectExtractor()
        self.classifier = RuleBasedContextualClassifier(self.baseline)
        self.llm = PydanticAIAgentRunner() if mode == "llm" else None
        self.graph = self._build_graph()

    def process_file(
        self,
        input_path: Path,
        *,
        output_dir: Path = settings.processed_data_dir,
        limit: int | None = None,
    ) -> tuple[list[ProcessedAspectRecord], Path, Path]:
        """Load raw reviews, process them, and write processed CSV/JSON."""

        reviews = load_raw_reviews(input_path)
        if limit is not None:
            reviews = reviews[:limit]

        records: list[ProcessedAspectRecord] = []
        logger.info("Processing {} raw reviews in {} mode", len(reviews), self.mode)

        for index, review in enumerate(reviews, start=1):
            logger.info("Processing review {}/{}", index, len(reviews))
            review_records = self.process_review(review)
            records.extend(review_records)

        stem = input_path.stem.replace("raw", "processed")
        output_csv = output_dir / f"{stem}_{self.mode}.csv"
        output_json = output_dir / f"{stem}_{self.mode}.json"
        write_records_csv_json(records, csv_path=output_csv, json_path=output_json)
        logger.success("Wrote {} processed aspect rows", len(records))
        return records, output_csv, output_json

    def process_review(self, review: RawReview) -> list[ProcessedAspectRecord]:
        """Process one raw review through the LangGraph workflow."""

        review_id = make_review_id(review)
        state = self.graph.invoke({"review_id": review_id, "raw_review": review})
        return flatten_state_to_records(state, mode=self.mode)

    def _build_graph(self):
        workflow = StateGraph(ReviewPipelineState)
        workflow.add_node("cleaner_router", self._cleaner_router_node)
        workflow.add_node("aspect_extractor", self._aspect_extractor_node)
        workflow.add_node("contextual_classifier", self._contextual_classifier_node)
        workflow.add_edge(START, "cleaner_router")
        workflow.add_edge("cleaner_router", "aspect_extractor")
        workflow.add_edge("aspect_extractor", "contextual_classifier")
        workflow.add_edge("contextual_classifier", END)
        return workflow.compile()

    def _cleaner_router_node(self, state: ReviewPipelineState) -> ReviewPipelineState:
        raw_review = state["raw_review"]
        review_id = state["review_id"]
        if self.llm is not None:
            cleaned = self.llm.clean_review(review_id, raw_review)
        else:
            cleaned = self.cleaner.run(review_id, raw_review)
        return {"cleaned_review": cleaned}

    def _aspect_extractor_node(self, state: ReviewPipelineState) -> ReviewPipelineState:
        cleaned = state["cleaned_review"]
        if self.llm is not None:
            extracted = self.llm.extract_aspects(cleaned)
        else:
            extracted = self.extractor.run(cleaned)
        return {"extracted_aspects": dedupe_aspects(extracted)}

    def _contextual_classifier_node(self, state: ReviewPipelineState) -> ReviewPipelineState:
        cleaned = state["cleaned_review"]
        extracted = state["extracted_aspects"]
        sentiments: list[AspectSentiment] = []

        for aspect in extracted.aspects:
            baseline = self.baseline.score(aspect.evidence or cleaned.cleaned_text)
            if self.llm is not None:
                sentiment = self.llm.classify_aspect(
                    cleaned,
                    aspect.model_dump(mode="json"),
                    baseline,
                )
            else:
                sentiment = self.classifier.run(cleaned, aspect)
            sentiments.append(sentiment)

        return {"aspect_sentiments": sentiments}


def load_raw_reviews(input_path: Path) -> list[RawReview]:
    """Load raw review records from CSV or JSON."""

    if input_path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(input_path)
    elif input_path.suffix.lower() == ".json":
        dataframe = pd.read_json(input_path)
    else:
        raise ValueError(f"Unsupported input file type: {input_path.suffix}")

    dataframe = dataframe.where(pd.notna(dataframe), None)
    return [RawReview.model_validate(row) for row in dataframe.to_dict(orient="records")]


def dedupe_aspects(extracted: AspectExtractionResult) -> AspectExtractionResult:
    """Keep the highest-confidence mention for each aspect/category pair."""

    aspects_by_key: dict[tuple[str, str], AspectMention] = {}
    for aspect in extracted.aspects:
        key = (aspect.aspect.strip().lower(), aspect.aspect_category.strip().lower())
        existing = aspects_by_key.get(key)
        if existing is None or aspect.confidence > existing.confidence:
            aspects_by_key[key] = aspect

    return AspectExtractionResult(
        review_id=extracted.review_id,
        aspects=list(aspects_by_key.values()),
    )


def make_review_id(review: RawReview) -> str:
    """Create a stable deterministic ID for a raw review."""

    text = "|".join(
        [
            review.product_url,
            review.sku or "",
            review.review_title or "",
            review.review_body or "",
            review.review_date or "",
            review.reviewer_name or "",
        ]
    )
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def flatten_state_to_records(
    state: ReviewPipelineState,
    *,
    mode: PipelineMode,
) -> list[ProcessedAspectRecord]:
    """Convert final graph state into dashboard-friendly rows."""

    raw = state["raw_review"]
    cleaned = state["cleaned_review"]
    sentiments = state["aspect_sentiments"]
    review_text = combine_review_text(raw.review_title, raw.review_body)
    records: list[ProcessedAspectRecord] = []

    for sentiment in sentiments:
        baseline = sentiment.baseline_sentiment
        records.append(
            ProcessedAspectRecord(
                review_id=state["review_id"],
                product_name=raw.product_name,
                product_url=raw.product_url,
                sku=raw.sku,
                review_title=raw.review_title,
                review_body=raw.review_body,
                review_text=review_text,
                star_rating=raw.star_rating,
                review_date=raw.review_date,
                reviewer_name=raw.reviewer_name,
                verified_purchase=raw.verified_purchase,
                source_url=raw.source_url,
                scraped_at=raw.scraped_at.isoformat() if raw.scraped_at else None,
                product_category=cleaned.product_category,
                cleaned_text=cleaned.cleaned_text,
                aspect=sentiment.aspect,
                aspect_category=sentiment.aspect_category,
                aspect_evidence=sentiment.evidence,
                aspect_confidence=_aspect_confidence(state, sentiment.aspect),
                vader_label=baseline.label,
                vader_compound=baseline.compound,
                vader_positive=baseline.positive,
                vader_neutral=baseline.neutral,
                vader_negative=baseline.negative,
                contextual_sentiment=sentiment.sentiment,
                contextual_sentiment_score=sentiment.sentiment_score,
                contextual_rationale=sentiment.rationale,
                pipeline_mode=mode,
            )
        )

    return records


def _aspect_confidence(state: ReviewPipelineState, aspect_name: str) -> float:
    extracted = state["extracted_aspects"]
    for aspect in extracted.aspects:
        if aspect.aspect == aspect_name:
            return aspect.confidence
    return 0.0
