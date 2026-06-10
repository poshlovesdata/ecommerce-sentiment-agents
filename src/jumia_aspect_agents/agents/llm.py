"""PydanticAI agent definitions for the multi-agent NLP pipeline."""

import json
import os

from pydantic_ai import Agent

from jumia_aspect_agents.config import settings
from jumia_aspect_agents.models.nlp import (
    AspectExtractionResult,
    AspectSentiment,
    BaselineSentiment,
    CleanedReview,
)
from jumia_aspect_agents.models.reviews import RawReview


CLEANER_INSTRUCTIONS = """
You are Agent 1 in a consumer review analytics pipeline.
Clean the raw Jumia Nigeria review text without changing its meaning.
Normalize obvious abbreviations or noisy spelling where helpful.
Infer the mobile accessory product category, such as power_bank, charger,
earbuds_or_headphones, phone_case, screen_protector, cable, or mobile_accessory.
Return only the structured output requested by the schema.
"""

ASPECT_EXTRACTOR_INSTRUCTIONS = """
You are Agent 2 in an aspect-based sentiment pipeline.
Given a cleaned review, extract concrete product or service aspects discussed.
Prefer specific aspects such as Battery life, Charging speed, Build quality,
Portability, Price value, Delivery speed, Product performance, Packaging, or
Customer service. Use short evidence spans from the review.
If the review is very short, return one General product experience aspect.
Return only the structured output requested by the schema.
"""

CLASSIFIER_INSTRUCTIONS = """
You are Agent 3 in an aspect-based sentiment pipeline.
Classify sentiment for one isolated aspect using the review context, the aspect
evidence, and the supplied baseline sentiment. The final sentiment must be one
of positive, negative, neutral, or mixed.
Pay attention to Nigerian/informal review language and mixed opinions.
Return only the structured output requested by the schema.
"""


class PydanticAIAgentRunner:
    """Run the three PydanticAI agents with typed outputs."""

    def __init__(self, model_name: str | None = None) -> None:
        if settings.openai_api_key and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        self.model_name = model_name or _pydantic_ai_model_name(settings.openai_model)
        model_settings = {"temperature": settings.llm_temperature}
        self.cleaner = Agent(
            self.model_name,
            output_type=CleanedReview,
            instructions=CLEANER_INSTRUCTIONS,
            model_settings=model_settings,
        )
        self.extractor = Agent(
            self.model_name,
            output_type=AspectExtractionResult,
            instructions=ASPECT_EXTRACTOR_INSTRUCTIONS,
            model_settings=model_settings,
        )
        self.classifier = Agent(
            self.model_name,
            output_type=AspectSentiment,
            instructions=CLASSIFIER_INSTRUCTIONS,
            model_settings=model_settings,
        )

    def clean_review(self, review_id: str, review: RawReview) -> CleanedReview:
        prompt = {
            "review_id": review_id,
            "product_name": review.product_name,
            "review_title": review.review_title,
            "review_body": review.review_body,
            "star_rating": review.star_rating,
        }
        result = self.cleaner.run_sync(json.dumps(prompt, ensure_ascii=False))
        return result.output

    def extract_aspects(self, cleaned: CleanedReview) -> AspectExtractionResult:
        result = self.extractor.run_sync(cleaned.model_dump_json())
        return result.output

    def classify_aspect(
        self,
        cleaned: CleanedReview,
        aspect_payload: dict,
        baseline: BaselineSentiment,
    ) -> AspectSentiment:
        prompt = {
            "cleaned_review": cleaned.model_dump(mode="json"),
            "aspect": aspect_payload,
            "baseline_sentiment": baseline.model_dump(mode="json"),
        }
        result = self.classifier.run_sync(json.dumps(prompt, ensure_ascii=False))
        return result.output


def _pydantic_ai_model_name(model_name: str) -> str:
    """Normalize OpenAI model names for PydanticAI."""

    if ":" in model_name:
        return model_name
    return f"openai-chat:{model_name}"
