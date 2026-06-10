"""Deterministic fallback agents for local/offline pipeline runs."""

import re

from jumia_aspect_agents.analysis.sentiment import BaselineSentimentAnalyzer
from jumia_aspect_agents.models.nlp import (
    AspectExtractionResult,
    AspectMention,
    AspectSentiment,
    CleanedReview,
    SentimentLabel,
)
from jumia_aspect_agents.models.reviews import RawReview


SLANG_NORMALIZATIONS = {
    "nd": "and",
    "bt": "but",
    "dat": "that",
    "dis": "this",
    "d": "the",
    "u": "you",
    "ur": "your",
    "kinda": "kind of",
    "kinder": "kind of",
    "bettry": "battery",
    "potable": "portable",
}

PRODUCT_CATEGORY_KEYWORDS = {
    "power_bank": ["power bank", "powerbank", "mah", "battery"],
    "charger": ["charger", "charging", "adapter", "type c", "usb"],
    "earbuds_or_headphones": ["earbud", "earpods", "headphone", "earpiece", "sound"],
    "phone_case": ["case", "cover", "pouch"],
    "screen_protector": ["screen", "protector", "glass"],
    "cable": ["cable", "cord"],
}

ASPECT_KEYWORDS = {
    "Battery life": {
        "category": "battery",
        "keywords": ["battery", "last", "mah", "charge your phone", "goes off"],
    },
    "Charging speed": {
        "category": "charging",
        "keywords": ["charging", "charge", "fast charge", "type c"],
    },
    "Build quality": {
        "category": "quality",
        "keywords": ["quality", "durable", "strong", "weak", "broke", "damage"],
    },
    "Portability": {
        "category": "design",
        "keywords": ["portable", "slim", "heavy", "light"],
    },
    "Price value": {
        "category": "price",
        "keywords": ["price", "cheap", "cost", "worth", "value"],
    },
    "Delivery speed": {
        "category": "delivery",
        "keywords": ["delivery", "delivered", "late", "slow", "rider"],
    },
    "Product performance": {
        "category": "performance",
        "keywords": ["works", "work", "serve", "serving", "performance", "ok", "okay"],
    },
}


class RuleBasedCleanerRouter:
    """Agent 1 fallback: clean review text and infer product category."""

    def run(self, review_id: str, review: RawReview) -> CleanedReview:
        text = combine_review_text(review.review_title, review.review_body)
        cleaned_text, normalized = normalize_review_text(text)
        product_category = infer_product_category(review.product_name, cleaned_text)

        return CleanedReview(
            review_id=review_id,
            original_text=text,
            cleaned_text=cleaned_text,
            product_category=product_category,
            normalized_terms=normalized,
            notes=["rule_based_cleaning"],
        )


class RuleBasedAspectExtractor:
    """Agent 2 fallback: extract likely aspects from keyword matches."""

    def run(self, cleaned: CleanedReview) -> AspectExtractionResult:
        text = cleaned.cleaned_text.lower()
        aspects: list[AspectMention] = []

        for aspect, config in ASPECT_KEYWORDS.items():
            for keyword in config["keywords"]:
                if keyword in text:
                    aspects.append(
                        AspectMention(
                            aspect=aspect,
                            aspect_category=config["category"],
                            evidence=extract_evidence(cleaned.cleaned_text, keyword),
                            confidence=0.72,
                        )
                    )
                    break

        if not aspects:
            aspects.append(
                AspectMention(
                    aspect="General product experience",
                    aspect_category="general",
                    evidence=cleaned.cleaned_text,
                    confidence=0.45,
                )
            )

        return AspectExtractionResult(review_id=cleaned.review_id, aspects=aspects)


class RuleBasedContextualClassifier:
    """Agent 3 fallback: classify aspect sentiment using local context and VADER baseline."""

    def __init__(self, baseline: BaselineSentimentAnalyzer | None = None) -> None:
        self.baseline = baseline or BaselineSentimentAnalyzer()

    def run(self, cleaned: CleanedReview, aspect: AspectMention) -> AspectSentiment:
        evidence = aspect.evidence or cleaned.cleaned_text
        baseline = self.baseline.score(evidence)
        sentiment, score, rationale = classify_with_context(evidence, baseline.label, baseline.compound)

        return AspectSentiment(
            review_id=cleaned.review_id,
            aspect=aspect.aspect,
            aspect_category=aspect.aspect_category,
            sentiment=sentiment,
            sentiment_score=score,
            evidence=evidence,
            rationale=rationale,
            baseline_sentiment=baseline,
        )


def combine_review_text(title: str | None, body: str | None) -> str:
    parts = [part.strip() for part in [title, body] if part and part.strip()]
    return " ".join(parts)


def normalize_review_text(text: str) -> tuple[str, list[str]]:
    text = re.sub(r"\s+", " ", text).strip()
    normalized_terms: list[str] = []

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        replacement = SLANG_NORMALIZATIONS.get(token.lower())
        if replacement is None:
            return token
        normalized_terms.append(f"{token}->{replacement}")
        return replacement

    cleaned = re.sub(r"\b[a-zA-Z']+\b", replace_token, text)
    return cleaned, normalized_terms


def infer_product_category(product_name: str, cleaned_text: str) -> str:
    text = f"{product_name} {cleaned_text}".lower()
    for category, keywords in PRODUCT_CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "mobile_accessory"


def extract_evidence(text: str, keyword: str, window: int = 80) -> str:
    lower_text = text.lower()
    index = lower_text.find(keyword.lower())
    if index < 0:
        return text[:window].strip()
    start = max(0, index - window // 2)
    end = min(len(text), index + len(keyword) + window // 2)
    return text[start:end].strip()


def classify_with_context(
    evidence: str,
    baseline_label: SentimentLabel,
    baseline_score: float,
) -> tuple[SentimentLabel, float, str]:
    text = evidence.lower()
    hard_negative_patterns = [
        "not good",
        "not strong",
        "not durable",
        "not working",
        "does not work",
        "did not work",
    ]
    negative_patterns = [
        *hard_negative_patterns,
        "bad",
        "weak",
        "low battery",
        "poor",
        "go off",
        "goes off",
        "not last",
        "doesn't last",
        "dont last",
    ]
    positive_patterns = [
        "last long",
        "last longer",
        "strong",
        "durable",
        "good",
        "nice",
        "love",
        "portable",
        "works",
    ]

    has_negative = any(pattern in text for pattern in negative_patterns)
    has_positive = any(pattern in text for pattern in positive_patterns)

    if any(pattern in text for pattern in hard_negative_patterns):
        return "negative", min(-0.2, baseline_score), "Rule-based context found negated quality cues."
    if has_negative and has_positive:
        return "mixed", 0.0, "Rule-based context found both positive and negative cues."
    if has_negative:
        return "negative", min(-0.2, baseline_score), "Rule-based context found negative cues."
    if has_positive:
        return "positive", max(0.2, baseline_score), "Rule-based context found positive cues."
    return baseline_label, baseline_score, "No stronger context cue found; baseline label retained."
