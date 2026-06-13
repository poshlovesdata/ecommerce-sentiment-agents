# Results Analysis for Research Paper

Generated from production dashboard dataset on June 13, 2026.

Production dashboard: https://dashboard.poshlovesdata.dev

Dataset analyzed:

```text
data/processed/jumia_reviews_processed_latest.csv
```

## Executive Summary

The deployed dashboard is working and currently presents a merged dataset containing both broad deterministic rules output and a smaller LLM sample. The merged dataset contains:

- 4,964 unique reviews.
- 98 unique products.
- 6,320 aspect-level rows.
- 22 unique aspects.
- Average contextual sentiment score: 0.35.
- Average star rating: 3.78 stars.
- Review date range: March 27, 2023 to June 12, 2026.

The results support the central argument of the paper: e-commerce review analytics becomes more informative when reviews are decomposed into product/service aspects instead of being treated only as star ratings or whole-review sentiment.

## Dashboard Verification

The dashboard loaded successfully at:

```text
https://dashboard.poshlovesdata.dev
```

Observed dashboard components:

- Dataset selector.
- Pipeline filter with `llm` and `rules`.
- Product, aspect, sentiment, rating, and date filters.
- KPI cards.
- Contextual Sentiment chart.
- Aspect Mentions chart.
- Aspect Sentiment Matrix.
- VADER vs Contextual chart.
- Star Rating vs Aspect Score chart.
- Review Timeline chart.
- Review Evidence table.

The dashboard currently defaults to the merged production latest dataset:

```text
Production latest - jumia_reviews_processed_latest.csv
```

## Pipeline Coverage

The merged dataset includes two pipeline modes:

| Pipeline Mode | Aspect Rows | Unique Reviews | Unique Products | Unique Aspects | Avg Score | Avg Star Rating |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rules | 6,207 | 4,964 | 98 | 8 | 0.35 | 3.78 |
| llm | 113 | 100 | 2 | 20 | 0.28 | 4.07 |

Interpretation:

- The rules pipeline provides the broad quantitative view across nearly the full scraped dataset.
- The LLM pipeline provides a smaller qualitative/contextual sample.
- The LLM sample is not yet representative of all products because it covers only 2 products. It should be described as a limited LLM sample, not as the full dataset.
- The fact that LLM found 20 aspects from 100 reviews while rules found 8 aspects from 4,964 reviews suggests the LLM is more expressive and granular, but also less standardized.

Recommended paper wording:

> The deterministic rules pipeline was used to process the full scraped dataset for broad descriptive analytics, while the LLM pipeline was applied to a smaller sample to evaluate contextual aspect extraction and classification behavior. This design balanced analytical coverage with LLM processing cost.

## Overall Sentiment Distribution

Across all merged aspect rows:

| Sentiment | Rows |
| --- | ---: |
| positive | 4,466 |
| negative | 1,110 |
| neutral | 589 |
| mixed | 155 |

The dashboard therefore shows a generally positive review environment, but with meaningful negative and mixed feedback. This is important because average star ratings alone would understate the presence of aspect-specific dissatisfaction.

By pipeline:

| Pipeline | Positive | Neutral | Mixed | Negative |
| --- | ---: | ---: | ---: | ---: |
| rules | 4,398 (70.9%) | 582 (9.4%) | 140 (2.3%) | 1,087 (17.5%) |
| llm | 68 (60.2%) | 7 (6.2%) | 15 (13.3%) | 23 (20.4%) |

Interpretation:

- The rules pipeline classifies most aspect rows as positive.
- The LLM sample produces a higher share of mixed sentiment than rules: 13.3% vs 2.3%.
- This supports the argument that contextual LLM analysis is better suited to detecting mixed or nuanced review statements.

## Most Mentioned Aspects

Top aspect mentions:

| Aspect | Rows |
| --- | ---: |
| General product experience | 2,057 |
| Battery life | 1,344 |
| Product performance | 959 |
| Build quality | 778 |
| Charging speed | 561 |
| Price value | 335 |
| Portability | 227 |
| Delivery speed | 43 |
| Comfort | 3 |
| Quality | 1 |
| Color variety | 1 |
| Customer service | 1 |

Interpretation:

- General product experience is the most common category because many Jumia reviews are short, such as "good", "nice", or "bad".
- Among more specific aspects, battery life is the strongest consumer concern.
- Product performance, build quality, and charging speed are also central to mobile accessory satisfaction.
- Delivery speed appears less often than product-related aspects in the current dataset, but still appears as a service-related aspect.

Recommended paper wording:

> The dominance of battery life, product performance, build quality, and charging speed reflects the functional nature of mobile accessories. Consumers in this market appear to evaluate products primarily by whether they last, work reliably, charge quickly, and provide value for money.

## Aspect-Specific Sentiment

Aspect sentiment summary:

| Aspect | Rows | Positive | Negative | Neutral | Mixed | Avg Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| General product experience | 2,057 | 81.5% | 9.5% | 8.3% | 0.7% | 0.488 |
| Battery life | 1,344 | 58.5% | 23.9% | 11.7% | 6.0% | 0.225 |
| Product performance | 959 | 69.8% | 20.8% | 7.9% | 1.6% | 0.313 |
| Build quality | 778 | 67.6% | 25.6% | 3.0% | 3.9% | 0.294 |
| Charging speed | 561 | 56.3% | 21.9% | 20.1% | 1.6% | 0.186 |
| Price value | 335 | 88.1% | 6.9% | 3.3% | 1.8% | 0.487 |
| Portability | 227 | 71.8% | 16.7% | 11.0% | 0.4% | 0.313 |
| Delivery speed | 43 | 58.1% | 11.6% | 30.2% | 0.0% | 0.258 |

Interpretation:

- Price value is the most positive major aspect, with 88.1% positive sentiment.
- Battery life has high volume but also substantial dissatisfaction: 23.9% negative and 6.0% mixed.
- Build quality shows the highest negative share among major aspects: 25.6%.
- Charging speed has the lowest average score among major aspects at 0.186, with a relatively high neutral share.
- These patterns suggest that consumers may be generally satisfied with value, but more critical about durability, battery reliability, and charging performance.

Paper insight:

> A high number of positive general comments does not eliminate operational weaknesses. The aspect matrix shows that battery life, build quality, and charging speed require closer vendor attention because they combine high mention frequency with notable negative sentiment.

## VADER vs Contextual Sentiment

VADER and contextual sentiment mostly agree when contextual sentiment is not mixed:

- Non-mixed rows: 6,165.
- Agreement rows: 5,648.
- Agreement rate: 91.6%.
- Disagreement rate: 8.4%.

Crosstab:

| VADER Label | Context Mixed | Context Negative | Context Neutral | Context Positive |
| --- | ---: | ---: | ---: | ---: |
| negative | 52 | 861 | 0 | 100 |
| neutral | 24 | 102 | 583 | 162 |
| positive | 79 | 147 | 6 | 4,204 |

Interpretation:

- VADER performs reasonably well for many short review snippets.
- However, VADER cannot represent mixed sentiment.
- VADER sometimes misclassifies local or context-dependent comments because it relies on surface lexical cues.
- The LLM examples show better contextual reasoning in cases where positive words appear alongside negative product evidence.

Useful examples for discussion:

1. Review text: "good but do not last long Use a stronger material to produce it"
   - Aspect: Build quality.
   - VADER: positive.
   - LLM contextual sentiment: negative.
   - Interpretation: VADER reacts to "good" and "stronger", while the LLM recognizes durability dissatisfaction.

2. Review text: "The thread keep lossing Make the thread better"
   - Aspect: Thread quality.
   - VADER: positive.
   - LLM contextual sentiment: negative.
   - Interpretation: VADER misreads "better" positively, while contextual classification recognizes a complaint.

3. Review text: "perfect No body has complain to me about it And I love the way it was package"
   - VADER: negative.
   - LLM contextual sentiment: positive.
   - Interpretation: VADER appears to react to "No" and "complain"; the LLM understands the phrase as satisfaction.

Recommended paper wording:

> The VADER baseline was useful for comparison but limited in detecting mixed sentiment and localized phrasing. Contextual classification improved interpretability by considering the relationship between the aspect evidence and the surrounding review text.

## Star Ratings vs Aspect Sentiment

The dataset contains mismatches between star ratings and aspect sentiment:

- High rating, negative or mixed aspect rows: 226 rows across 181 unique reviews.
- Low rating, positive aspect rows: 320 rows across 275 unique reviews.

Interpretation:

- Some 4- or 5-star reviews still contain negative or mixed aspect-level feedback.
- Some 1- or 2-star reviews still contain positive aspect-level remarks.
- This supports the central claim that star ratings are too coarse for consumer behavior analytics.

Examples:

1. A 5-star review says the product is a "good buy" but the material gets rough easily.
   - Aspect: Build quality.
   - Contextual sentiment: mixed.
   - Insight: High rating masks a durability issue.

2. A 5-star review says the earbuds last long but have "no bass".
   - Aspect: Battery life and/or product performance.
   - Contextual sentiment: mixed.
   - Insight: Consumers can be satisfied overall while still identifying feature-level weaknesses.

3. A 4-star review says the thumb sleeves are "not too dependable in long gameplay" and become less responsive due to sweat.
   - Aspect: Responsiveness.
   - LLM contextual sentiment: negative.
   - Insight: Moderate-to-high rating can still contain strong use-case complaints.

Paper insight:

> Aspect-level modeling reveals hidden dissatisfaction inside otherwise positive star ratings. This is especially useful for vendors because it identifies the specific product attributes that require improvement.

## Rules vs LLM Comparison

Rules pipeline:

- Broad coverage.
- 4,964 unique reviews.
- 98 products.
- 6,207 aspect rows.
- 8 standardized aspect types.
- Useful for stable charts and broad descriptive analysis.

LLM pipeline:

- Smaller sample due to cost.
- 100 unique reviews.
- 2 products.
- 113 aspect rows.
- 20 aspect types.
- Better at nuanced classifications and more specific aspect labels.

Interpretation:

- Rules are better for cost-effective full-dataset coverage.
- LLM is better for nuance, mixed sentiment, and detailed rationales.
- The combined approach is useful for a research prototype: broad rules-based analysis establishes market patterns, while LLM sampling demonstrates the value of contextual multi-agent reasoning.

Important limitation:

The current LLM sample is not stratified. It covers only 2 products because the first 100 raw master reviews were processed. The paper should avoid making broad LLM-only claims across all 98 products. A future improvement would sample reviews across product categories and rating levels.

Recommended future-work wording:

> Future experiments should use stratified LLM sampling across product types, star ratings, and review dates to make contextual LLM results more representative of the entire scraped dataset.

Implementation note:

This limitation can now be addressed with:

```bash
python scripts/sample_raw_reviews.py --sample-size 300
python scripts/run_pipeline.py \
  --input data/raw/jumia_reviews_raw_llm_stratified_sample.csv \
  --mode llm
python scripts/merge_processed.py \
  --input data/processed/jumia_reviews_processed_master_rules.csv \
  --input data/processed/jumia_reviews_processed_llm_stratified_sample_llm.csv \
  --publish-latest
```

After this run, regenerate this analysis because LLM coverage, aspect counts, and VADER/contextual comparisons will change.

## Consumer Behavior Insights

The analysis suggests the following consumer behavior patterns in the Jumia Nigeria mobile accessories case study:

1. Consumers frequently use short general evaluations, such as simple positive or negative comments, which explains the high "General product experience" count.
2. Functional performance matters most. Battery life, charging speed, product performance, and build quality dominate aspect mentions.
3. Price value is strongly positive, suggesting many buyers consider the products acceptable for their cost.
4. Battery life and build quality remain important pain points despite overall positive sentiment.
5. Star ratings alone are insufficient because negative feature-level evidence appears inside high-rated reviews.
6. VADER is useful as a baseline but misses mixed or context-specific interpretations.
7. The LLM sample shows that agentic analysis can produce richer rationales and more granular aspects, though at higher cost.

## Suggested Results Section Narrative

The results can be written in this order:

1. Present the dataset size: 4,964 reviews, 98 products, 6,320 aspect rows.
2. Explain that the dataset combines a full rules-based run and a 100-review LLM sample.
3. Show overall sentiment distribution, emphasizing the dominance of positive sentiment but presence of negative/mixed rows.
4. Discuss top aspects: general product experience, battery life, product performance, build quality, charging speed, price value.
5. Analyze aspect-specific sentiment and identify battery life/build quality/charging speed as key areas of dissatisfaction.
6. Compare VADER and contextual sentiment, noting 91.6% agreement on non-mixed rows but important disagreement examples.
7. Discuss star-rating mismatch examples to show why aspect-based analytics is necessary.
8. Conclude that the multi-agent framework improves interpretability by converting unstructured reviews into aspect-level evidence.

## Figures and Tables to Include

Recommended dashboard screenshots:

1. Full dashboard top section showing KPI cards, Contextual Sentiment, and Aspect Mentions.
2. Aspect Sentiment Matrix.
3. VADER vs Contextual chart.
4. Star Rating vs Aspect Score chart.
5. Review Evidence table showing examples.

Recommended tables:

1. Dataset summary table.
2. Top aspect mentions table.
3. Aspect-specific sentiment percentages.
4. VADER vs contextual sentiment crosstab.
5. Examples of star rating/aspect sentiment mismatch.

## Cautions for the Paper

- Do not claim the LLM output covers the entire scraped dataset. It is a 100-review sample.
- Do not claim demographic behavior because reviewer demographics are unavailable.
- Do not overgeneralize from Jumia Nigeria to all e-commerce platforms without framing it as a case study.
- Do not treat rules and LLM outputs as identical methods. They serve different methodological roles.
- Mention that raw scrape data may contain duplicates across scrape batches, but the master dataset deduplicates by `review_id`.

## One-Paragraph Result Summary

The deployed system processed 4,964 unique Jumia Nigeria mobile accessories reviews into 6,320 aspect-level sentiment rows across 98 products. The merged dashboard dataset combines a broad rules-based run with a smaller 100-review LLM sample. Overall sentiment was predominantly positive, but aspect-level analysis exposed meaningful dissatisfaction around battery life, build quality, and charging speed. Price value was the most positively perceived major aspect, while build quality had the highest negative share among high-volume aspects. VADER agreed with contextual sentiment on 91.6% of non-mixed rows, but failed to represent mixed opinions and sometimes misread context-dependent phrases. Star-rating comparison showed that 181 high-rated reviews still contained negative or mixed aspect-level feedback, confirming that aggregate ratings alone are insufficient for consumer behavior analytics.
