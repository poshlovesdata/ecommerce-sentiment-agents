# Presentation Handoff

Course: COSC878 - Web and Social Media Analytics

Project title: An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria

Production dashboard: https://dashboard.poshlovesdata.dev

Repository: https://github.com/poshlovesdata/ecommerce-sentiment-agents.git

## Purpose

This document gives a presentation-building agent enough context to create a 10-minute class presentation and demo. The presentation should explain the research problem, the implemented system, the methodology, the deployed dashboard, and the most important findings.

The tone should be academic but practical: this is a research implementation, not just a coding project.

## Core Framing

Frame the problem as e-commerce consumer behavior analytics.

Jumia Nigeria is the case study platform, not the entire problem domain. The mobile phone accessories category was selected because it has many product reviews and aspect-rich consumer comments about battery life, charging speed, build quality, delivery, price value, and general product performance.

Central argument:

> Star ratings and whole-review sentiment are too coarse for understanding e-commerce consumer behavior. Aspect-based analysis gives a more useful view because it identifies what consumers liked or disliked about specific product and service attributes.

## System Summary

The project implements an end-to-end analytics pipeline:

```text
Jumia Nigeria mobile accessories pages
  -> product discovery
  -> review scraping
  -> raw CSV/JSON batches
  -> deduplicated master dataset
  -> rules and LLM processing
  -> aspect-level sentiment dataset
  -> Streamlit dashboard
  -> Docker/Traefik deployment on VPS
```

Main technologies:

- Python, Requests, BeautifulSoup for scraping.
- Pydantic models for structured data contracts.
- PydanticAI, LangGraph, and OpenAI for the multi-agent LLM pipeline.
- NLTK/VADER for baseline sentiment.
- Pandas for processing and dataset assembly.
- Streamlit and Plotly for the dashboard.
- Docker Compose, Traefik, GitHub Actions, and VPS deployment.

## Multi-Agent Method

The implemented pipeline has three conceptual agents:

1. Cleaner/Router
   - Cleans noisy review text.
   - Infers product category.
   - Handles short, informal review language.

2. Aspect Extractor
   - Finds specific aspects in review text.
   - Examples: Battery life, Build quality, Charging speed, Price value, Delivery speed.
   - Captures evidence spans from the review.

3. Contextual Classifier
   - Assigns positive, negative, neutral, or mixed sentiment to each aspect.
   - Uses VADER as a baseline comparison.
   - Uses LLM reasoning for contextual interpretation.

The project has two processing modes:

- `rules`: deterministic, cheap, full-dataset processing.
- `llm`: contextual multi-agent processing on a stratified sample.

This design balances broad coverage with OpenAI API cost.

## Final Verified Dataset

Use these numbers in slides:

| Metric | Value |
| --- | ---: |
| Unique reviews | 4,964 |
| Products | 98 |
| Aspect-level rows | 6,582 |
| Unique aspects | 59 |
| Average contextual score | 0.33 |
| Average star rating | 3.73 |
| Review date range | March 27, 2023 to June 12, 2026 |

Pipeline coverage:

| Pipeline | Aspect Rows | Reviews | Products | Aspects |
| --- | ---: | ---: | ---: | ---: |
| Rules | 6,207 | 4,964 | 98 | 8 |
| LLM stratified sample | 375 | 300 | 61 | 59 |

Important caveat:

Do not say the LLM processed all reviews. The LLM processed a 300-review stratified sample. The rules pipeline processed the full dataset.

## Key Results

Overall sentiment:

| Sentiment | Rows |
| --- | ---: |
| Positive | 4,546 |
| Negative | 1,249 |
| Neutral | 601 |
| Mixed | 186 |

Top aspects:

| Aspect | Rows |
| --- | ---: |
| General product experience | 2,094 |
| Battery life | 1,409 |
| Product performance | 1,017 |
| Build quality | 782 |
| Charging speed | 590 |
| Price value | 352 |
| Portability | 234 |
| Delivery speed | 44 |

Aspect insights:

- Price value was the strongest positive aspect: 88.1% positive.
- Battery life was highly discussed but had meaningful dissatisfaction: 25.8% negative and 6.2% mixed.
- Build quality had the highest negative share among major aspects: 26.0% negative.
- Charging speed had the lowest average score among major aspects: 0.180.
- VADER and contextual sentiment agreed on 90.0% of non-mixed rows.
- 191 high-rated reviews still contained negative or mixed aspect-level feedback.

## Recommended Slide Deck

Suggested 10-slide structure:

1. Title
   - Project title, course, name, date.

2. Problem
   - Star ratings hide the reasons behind satisfaction/dissatisfaction.
   - E-commerce reviews are noisy, short, and aspect-rich.

3. Research Questions
   - Which aspects do consumers discuss most?
   - How does aspect sentiment differ from star ratings?
   - How does contextual sentiment compare with VADER?

4. Dataset and Case Study
   - Jumia Nigeria mobile accessories.
   - 4,964 reviews, 98 products.
   - Public review data only.

5. Architecture
   - Scraper -> master dataset -> agents -> processed dataset -> dashboard -> VPS.
   - Use a simple pipeline diagram.

6. Multi-Agent NLP Pipeline
   - Cleaner/Router.
   - Aspect Extractor.
   - Contextual Classifier.
   - VADER baseline.

7. Dashboard Demo Preview
   - Show KPI cards and filters.
   - Mention deployment at dashboard.poshlovesdata.dev.

8. Findings
   - Top aspects.
   - Sentiment distribution.
   - Battery/build/charging pain points.

9. Why Aspect-Based Analysis Matters
   - Star rating mismatch.
   - VADER limitations.
   - Mixed sentiment examples.

10. Limitations and Conclusion
   - LLM sample, no demographics, Jumia case study only.
   - Conclusion: aspect-based multi-agent analytics is more informative than aggregate ratings.

## Screenshots to Capture

Capture these from https://dashboard.poshlovesdata.dev:

1. Top dashboard with KPI cards.
2. Contextual Sentiment and Aspect Mentions charts.
3. Aspect Sentiment Matrix.
4. VADER vs Contextual chart.
5. Star Rating vs Aspect Score chart.
6. Review Evidence table.

If screenshots are placed in the repo, save them under:

```text
reports/figures/
```

Suggested filenames:

```text
dashboard_kpis.png
sentiment_and_aspects.png
aspect_matrix.png
vader_vs_contextual.png
star_rating_vs_aspect_score.png
review_evidence.png
```

## Demo Flow

The live demo should be short and controlled:

1. Open https://dashboard.poshlovesdata.dev.
2. Point to KPI cards.
3. Show pipeline filter with `rules` and `llm`.
4. Show aspect mentions.
5. Show aspect sentiment matrix.
6. Filter to `Battery life` or `Build quality`.
7. Show VADER vs Contextual.
8. Show Review Evidence examples.
9. End with the research conclusion.

Do not spend time live-running the scraper or LLM pipeline during the presentation. Those are batch jobs and can take time. Mention that they are reproducible through Docker Compose.

## Important Talking Points

- The dashboard is deployed, not just local.
- The pipeline is reproducible with Docker.
- The system preserves raw data and deduplicates reviews.
- The rules pipeline gives broad coverage.
- The LLM pipeline gives deeper contextual reasoning.
- The VADER comparison provides a conventional baseline.
- The results show that star ratings can hide aspect-level dissatisfaction.

## Warnings

- Do not overclaim demographic findings. Reviewer demographics are unavailable.
- Do not say Jumia represents all e-commerce platforms. It is a case study.
- Do not say the LLM processed every review. It processed a 300-review stratified sample.
- Do not present VADER as wrong overall; it had 90.0% agreement on non-mixed rows, but it misses mixed/contextual nuance.
- Do not spend too long on implementation details. Keep the focus on research value.

## Source Documents

The presentation agent should read these first:

```text
docs/RESULTS_ANALYSIS.md
docs/RESEARCH_PAPER_HANDOFF.md
README.md
```

