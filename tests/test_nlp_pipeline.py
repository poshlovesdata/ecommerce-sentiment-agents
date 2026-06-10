"""Tests for the aspect-based NLP pipeline."""

from datetime import datetime, timezone

from jumia_aspect_agents.agents.pipeline import (
    AspectSentimentPipeline,
    dedupe_aspects,
    make_review_id,
)
from jumia_aspect_agents.agents.rules import classify_with_context
from jumia_aspect_agents.models.nlp import AspectExtractionResult, AspectMention
from jumia_aspect_agents.models.reviews import RawReview


def make_review() -> RawReview:
    return RawReview(
        product_name="Ace Elec 20000 MAh Portable Power Bank",
        product_url="https://www.jumia.com.ng/product.html",
        sku="AC431EA7LKZHVNAFAMZ",
        review_title="Good battery",
        review_body="It lasts long but the delivery was slow",
        star_rating=4,
        review_date="09-06-2026",
        reviewer_name="Ada",
        verified_purchase=True,
        source_url="https://www.jumia.com.ng/catalog/productratingsreviews/sku/AC431EA7LKZHVNAFAMZ/",
        scraped_at=datetime.now(timezone.utc),
    )


def test_make_review_id_is_stable() -> None:
    review = make_review()

    assert make_review_id(review) == make_review_id(review)


def test_rules_pipeline_outputs_aspect_rows() -> None:
    pipeline = AspectSentimentPipeline(mode="rules")

    records = pipeline.process_review(make_review())

    aspects = {record.aspect for record in records}
    assert "Battery life" in aspects
    assert "Delivery speed" in aspects
    assert all(record.pipeline_mode == "rules" for record in records)
    assert all(record.review_id for record in records)


def test_negated_quality_phrase_is_negative() -> None:
    sentiment, score, rationale = classify_with_context("not strong Bad", "neutral", 0.0)

    assert sentiment == "negative"
    assert score < 0
    assert "negated" in rationale


def test_dedupe_aspects_keeps_one_aspect_category_pair() -> None:
    extracted = AspectExtractionResult(
        review_id="r1",
        aspects=[
            AspectMention(
                aspect="Product performance",
                aspect_category="general",
                evidence="lasts longer",
                confidence=0.5,
            ),
            AspectMention(
                aspect="Product performance",
                aspect_category="general",
                evidence="serving me well",
                confidence=0.8,
            ),
        ],
    )

    deduped = dedupe_aspects(extracted)

    assert len(deduped.aspects) == 1
    assert deduped.aspects[0].evidence == "serving me well"
