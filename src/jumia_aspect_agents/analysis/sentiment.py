"""Baseline sentiment scoring utilities."""

import re
from functools import cached_property

from loguru import logger

from jumia_aspect_agents.models.nlp import BaselineSentiment, SentimentLabel


POSITIVE_WORDS = {
    "amazing",
    "best",
    "durable",
    "excellent",
    "fast",
    "good",
    "great",
    "last",
    "long",
    "love",
    "lovely",
    "nice",
    "okay",
    "ok",
    "portable",
    "quality",
    "recommend",
    "strong",
    "superb",
    "works",
}

NEGATIVE_WORDS = {
    "bad",
    "break",
    "broke",
    "damage",
    "fake",
    "faulty",
    "low",
    "poor",
    "slow",
    "weak",
    "worse",
    "worst",
}


class BaselineSentimentAnalyzer:
    """VADER baseline with a tiny lexical fallback when the VADER lexicon is absent."""

    @cached_property
    def vader(self):
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer

            return SentimentIntensityAnalyzer()
        except LookupError:
            logger.warning(
                "NLTK VADER lexicon is not installed; using fallback lexical baseline. "
                "Run `python -m nltk.downloader vader_lexicon` for full VADER scoring."
            )
            return None

    def score(self, text: str) -> BaselineSentiment:
        """Score text with VADER when available, otherwise use a simple fallback."""

        if self.vader is not None:
            scores = self.vader.polarity_scores(text)
            compound = float(scores["compound"])
            return BaselineSentiment(
                label=self._label_from_compound(compound),
                compound=compound,
                positive=float(scores["pos"]),
                neutral=float(scores["neu"]),
                negative=float(scores["neg"]),
            )

        return self._fallback_score(text)

    def _fallback_score(self, text: str) -> BaselineSentiment:
        tokens = re.findall(r"[a-z']+", text.lower())
        if not tokens:
            return BaselineSentiment(label="neutral", compound=0.0, neutral=1.0)

        positive_hits = sum(token in POSITIVE_WORDS for token in tokens)
        negative_hits = sum(token in NEGATIVE_WORDS for token in tokens)
        total_hits = positive_hits + negative_hits

        if total_hits == 0:
            return BaselineSentiment(label="neutral", compound=0.0, neutral=1.0)

        compound = (positive_hits - negative_hits) / total_hits
        positive = positive_hits / len(tokens)
        negative = negative_hits / len(tokens)
        neutral = max(0.0, 1.0 - positive - negative)
        return BaselineSentiment(
            label=self._label_from_compound(compound),
            compound=compound,
            positive=positive,
            neutral=neutral,
            negative=negative,
        )

    def _label_from_compound(self, compound: float) -> SentimentLabel:
        if compound >= 0.05:
            return "positive"
        if compound <= -0.05:
            return "negative"
        return "neutral"
