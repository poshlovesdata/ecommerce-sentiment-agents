# Research Paper Handoff

Course: COSC878 - Web and Social Media Analytics

Project title: An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria

Repository: https://github.com/poshlovesdata/ecommerce-sentiment-agents.git

Production dashboard: https://dashboard.poshlovesdata.dev

## Purpose of This Document

This document gives a paper-writing agent enough context to write the full research article without reading the entire development conversation. It summarizes the research problem, methodology, implemented system, engineering decisions, deployment setup, limitations, and where to find evidence in the repository.

The paper should be written as a research article for a Web and Social Media Analytics course, not as a software manual. The implementation exists to support the methodology, results, and reproducibility claims.

For paper-ready findings from the deployed dashboard, read:

```text
docs/RESULTS_ANALYSIS.md
```

## Research Problem

E-commerce platforms generate large volumes of consumer feedback through product reviews, ratings, and seller interactions. However, traditional analytics methods often reduce this feedback to aggregate star ratings or whole-review sentiment scores, which can obscure the specific product and service aspects shaping consumer satisfaction.

This study treats this as a broader e-commerce consumer behavior analytics problem. Jumia Nigeria is used as the case study because it is a major e-commerce platform in an emerging digital market and provides public review data for mobile phone accessories.

Example problem pattern:

- A product may receive a high star rating while the review text complains about delivery, durability, or packaging.
- A single review may contain mixed sentiment, such as positive battery life but negative charging speed.
- E-commerce reviews may include informal language, brief comments, spelling variations, and delivery or service concerns that simple lexicon methods struggle to interpret.
- In the Jumia Nigeria case, these issues may also include localized language patterns and market-specific delivery expectations.

The research therefore investigates whether a multi-agent LLM pipeline can produce more informative e-commerce consumer behavior analytics by separating review text into product/service aspects and assigning contextual sentiment per aspect.

## Research Objectives

Recommended objectives for the paper:

1. Collect e-commerce consumer review data using Jumia Nigeria's mobile phone accessories category as a case study.
2. Preserve raw review metadata, including title, body text, star rating, reviewer, date, product, source URL, and verification status where available.
3. Design a multi-agent aspect-based sentiment analysis pipeline using PydanticAI, LangGraph, and OpenAI.
4. Compare contextual LLM-based aspect sentiment with a VADER baseline.
5. Visualize consumer behavior patterns across product aspects, ratings, dates, and product categories.
6. Demonstrate that a reproducible analytics system can be deployed using Docker, GitHub Actions, and Traefik.

## Research Questions

Possible research questions:

1. Which product and service aspects are most frequently discussed in e-commerce mobile accessories reviews in the Jumia Nigeria case study?
2. How does aspect-level sentiment differ from overall star-rating interpretation?
3. Which aspects attract the highest positive or negative consumer sentiment?
4. How does contextual LLM sentiment compare with VADER baseline sentiment for short e-commerce reviews?
5. What practical consumer behavior insights can e-commerce vendors extract from aspect-based review analytics?

## Implemented System Overview

The project implements a full pipeline:

```text
E-commerce category pages, using Jumia Nigeria as case study
  -> product discovery
  -> product review page scraping
  -> raw CSV/JSON batches
  -> master raw dataset with deduplication
  -> multi-agent NLP pipeline
  -> processed aspect-level CSV/JSON
  -> Streamlit dashboard
  -> Docker/Traefik VPS deployment
```

Core folders:

- `src/jumia_aspect_agents/data_collection/`: scraping and dataset assembly.
- `src/jumia_aspect_agents/agents/`: multi-agent NLP pipeline.
- `src/jumia_aspect_agents/analysis/`: VADER baseline sentiment.
- `src/jumia_aspect_agents/models/`: Pydantic schemas/contracts.
- `scripts/`: CLI entrypoints for scraping, processing, and dataset building.
- `app/streamlit_app.py`: dashboard.
- `deployment/`: Docker, Docker Compose, and deployment runbook.
- `.github/workflows/deploy.yml`: CI/CD workflow.

## Data Collection Methodology

Source:

- Website: Jumia Nigeria.
- Category: Mobile phone accessories.
- URL: `https://www.jumia.com.ng/mobile-accessories/`.

The paper should describe Jumia as the empirical case study site, while the problem and proposed framework should be framed as applicable to e-commerce review analytics more generally.

Scraper entrypoint:

```bash
python scripts/scrape_jumia.py
```

VPS job:

```bash
docker compose -f deployment/docker-compose.yml run --rm scraper
```

Fields collected:

- Product name
- Product URL
- SKU when available
- Review title
- Review body
- Star rating
- Review date
- Reviewer name
- Verified purchase flag when available
- Source URL
- Scrape timestamp

Implementation:

- `requests` performs HTTP requests.
- `BeautifulSoup` parses category, product, and review pages.
- Product discovery scans configurable category pages.
- Product selection is based on listing review count, sorted descending, then capped by `SCRAPER_MAX_PRODUCTS`.
- Review scraping follows product review pages and paginated "see all" review pages when available.
- Polite randomized delays are used between requests.
- Retry handling uses Tenacity for transient request failures.
- User agents identify the scraper as an educational/research bot.

Important scraper controls:

```text
SCRAPER_MAX_PAGES
SCRAPER_MAX_PRODUCTS
SCRAPER_MAX_REVIEWS_PER_PRODUCT
SCRAPER_MAX_REVIEW_PAGES_PER_PRODUCT
SCRAPER_MIN_DELAY_SECONDS
SCRAPER_MAX_DELAY_SECONDS
SCRAPER_TIMEOUT_SECONDS
SCRAPER_MAX_RETRIES
```

Interpretation of controls:

- `SCRAPER_MAX_PAGES`: number of category/listing pages to scan for products.
- `SCRAPER_MAX_PRODUCTS`: total selected products after combining all discovered products, not per page.
- `SCRAPER_MAX_REVIEWS_PER_PRODUCT`: maximum reviews collected per selected product.
- `SCRAPER_MAX_REVIEW_PAGES_PER_PRODUCT`: maximum paginated review pages opened per product.

Ethical and practical scraping note:

The scraper was designed for academic research using publicly visible review pages. It uses delays, limited page counts, retries, and research-identifying user agents. The paper should avoid implying access to private data or platform-internal data.

## Dataset Workflow

Raw scraper runs are not overwritten. Each scrape writes timestamped files:

```text
data/raw/jumia_reviews_raw_<timestamp>.csv
data/raw/jumia_reviews_raw_<timestamp>.json
```

The dataset builder merges all raw batches:

```bash
python scripts/build_dataset.py
```

It writes:

```text
data/raw/jumia_reviews_raw_master.csv
data/raw/jumia_reviews_raw_master.json
```

When processing is requested:

```bash
python scripts/build_dataset.py --mode llm
```

It writes stable dashboard files:

```text
data/processed/jumia_reviews_processed_latest.csv
data/processed/jumia_reviews_processed_latest.json
```

Rules and LLM processed outputs can be merged into one dashboard dataset:

```bash
python scripts/merge_processed.py --publish-latest
```

This preserves the `pipeline_mode` column, allowing the dashboard to show both broad deterministic rules results and a smaller LLM sample in one "Production latest" file.

For a stronger LLM sample, use a stratified raw-review sample instead of the first rows of the master dataset:

```bash
python scripts/sample_raw_reviews.py --sample-size 300
python scripts/run_pipeline.py \
  --input data/raw/jumia_reviews_raw_llm_stratified_sample.csv \
  --mode llm
```

The sampler spreads reviews across `product_name` and `star_rating` by default, making the LLM subset more useful for paper discussion.

Deduplication:

- The scraper itself can collect duplicate reviews across repeated runs.
- The dataset builder creates a deterministic `review_id` using product URL, SKU, review title, body, date, and reviewer.
- It deduplicates on `review_id` before creating the master dataset.
- This makes the dashboard dataset effectively idempotent after the processor runs.

## Multi-Agent NLP Methodology

Main implementation:

- `src/jumia_aspect_agents/agents/pipeline.py`
- `src/jumia_aspect_agents/agents/llm.py`
- `src/jumia_aspect_agents/agents/rules.py`
- `src/jumia_aspect_agents/models/nlp.py`

Orchestration:

- LangGraph coordinates a three-node workflow.
- Each review passes through:
  1. `cleaner_router`
  2. `aspect_extractor`
  3. `contextual_classifier`

Execution modes:

- `rules`: deterministic local mode used for tests, cheap experiments, and fallback.
- `llm`: PydanticAI/OpenAI mode used for final research processing.

Agent 1: Cleaner/Router

- Cleans raw review text without changing meaning.
- Normalizes obvious noisy wording where helpful.
- Infers the product category, such as power bank, charger, cable, phone case, earbuds/headphones, or general mobile accessory.
- Produces a `CleanedReview` Pydantic object.

Agent 2: Aspect Extractor

- Extracts concrete product/service aspects discussed in the review.
- Examples: Battery life, Charging speed, Build quality, Delivery speed, Price value, Product performance, Packaging, Customer service.
- Includes evidence spans and confidence scores.
- Produces an `AspectExtractionResult`.

Agent 3: Contextual Classifier

- Classifies sentiment for each extracted aspect.
- Output labels: positive, negative, neutral, or mixed.
- Uses review context, extracted evidence, and VADER baseline sentiment.
- Produces an `AspectSentiment`.

Why this is methodologically important:

Traditional sentiment methods usually classify the whole review. This project instead creates one row per aspect, allowing a single review to contain both positive and negative findings.

## VADER Baseline

Implementation:

- `src/jumia_aspect_agents/analysis/sentiment.py`

VADER is used as the baseline sentiment analyzer. It produces:

- `vader_label`
- `vader_compound`
- `vader_positive`
- `vader_neutral`
- `vader_negative`

Docker image note:

- The production Dockerfile downloads `vader_lexicon` during image build.
- This avoids fallback lexical scoring during VPS processing.

Research interpretation:

VADER acts as a conventional lexicon-based baseline. The LLM contextual classifier is then used to account for aspect-specific and context-specific sentiment. The dashboard includes a VADER vs contextual comparison chart.

## Data Model

The final processed dataset is aspect-level, not review-level.

One raw review can produce multiple processed rows:

```text
review_id | product | aspect | aspect_evidence | vader_label | contextual_sentiment | contextual_rationale
```

Important output columns:

- `review_id`
- `product_name`
- `review_text`
- `star_rating`
- `review_date`
- `reviewer_name`
- `product_category`
- `cleaned_text`
- `aspect`
- `aspect_category`
- `aspect_evidence`
- `aspect_confidence`
- `vader_label`
- `vader_compound`
- `contextual_sentiment`
- `contextual_sentiment_score`
- `contextual_rationale`
- `pipeline_mode`

This structure supports aspect-level aggregation in the results section.

## Dashboard and Results Presentation

Dashboard:

- `app/streamlit_app.py`
- Production URL: `https://dashboard.poshlovesdata.dev`

Dashboard features:

- Dataset selector, preferring `jumia_reviews_processed_latest.csv`.
- Filters for pipeline mode, product, aspect, sentiment, rating, and review date.
- KPI cards:
  - Reviews
  - Products
  - Aspect rows
  - Aspects
  - Average sentiment score
- Contextual sentiment distribution.
- Aspect mention frequency.
- Aspect sentiment matrix.
- VADER vs contextual sentiment comparison.
- Star rating vs aspect sentiment score.
- Review timeline.
- Evidence table with review text, aspect evidence, and rationale.

Recommended results section evidence:

The paper-writing agent should use the production dashboard or processed CSV to report:

- Number of unique reviews.
- Number of unique products.
- Number of aspect rows.
- Most frequent aspects.
- Sentiment distribution by aspect.
- Examples where star rating and text sentiment differ.
- Examples where one review contains multiple aspect sentiments.
- VADER vs LLM disagreement patterns.

Important: The exact final numbers depend on the final VPS scrape and processor run. The writer should compute these from `data/processed/jumia_reviews_processed_latest.csv` after the final processor run.

## Deployment and Reproducibility

Production flow:

```text
local -> GitHub main -> GitHub Actions -> SSH to VPS -> git pull -> Docker Compose rebuild -> Traefik -> dashboard.poshlovesdata.dev
```

VPS path:

```text
~/projects/ecommerce-sentiment-agents
```

Dashboard service:

```bash
docker compose -f deployment/docker-compose.yml up -d --build dashboard
```

One-off scraper job:

```bash
docker compose -f deployment/docker-compose.yml run --rm scraper
```

One-off processor job:

```bash
docker compose -f deployment/docker-compose.yml run --rm processor
```

Restart dashboard after processing:

```bash
docker compose -f deployment/docker-compose.yml up -d dashboard
```

Reverse proxy:

- Traefik.
- External Docker network: `web`.
- Public route: `dashboard.poshlovesdata.dev`.
- Let's Encrypt TLS resolver: `myresolver`.

CI/CD:

- GitHub Actions runs tests and Ruff linting.
- On successful push to `main`, the workflow SSHes into the VPS, pulls `main`, rebuilds the dashboard container, and prunes unused Docker images.

## Key Engineering Decisions

1. Use BeautifulSoup and Requests rather than a browser automation stack.
   - Reason: Jumia review pages are accessible through HTML and static parsing is lighter, simpler, and easier to reproduce.

2. Preserve raw data before NLP processing.
   - Reason: Supports auditability and lets the pipeline be rerun with improved models or prompts.

3. Use timestamped raw files plus a canonical master dataset.
   - Reason: Keeps scrape history while providing one deduplicated source for analysis.

4. Use Pydantic models for all NLP outputs.
   - Reason: Enforces structured agent responses and reduces unparseable free-text outputs.

5. Use LangGraph for orchestration.
   - Reason: Makes the agent workflow explicit and modular.

6. Include both `rules` and `llm` modes.
   - Reason: Rules mode enables reliable tests and low-cost debugging; LLM mode supports the actual research contribution.

7. Use VADER as a baseline rather than only LLM sentiment.
   - Reason: Allows comparison against a conventional sentiment method.

8. Use Streamlit for dashboarding.
   - Reason: Provides rapid, interactive visualization suitable for course presentation and exploratory analysis.

9. Use Docker and Traefik on a VPS.
   - Reason: Demonstrates reproducibility and operational readiness beyond local notebooks.

10. Use one-off Docker Compose jobs for scraper and processor.
    - Reason: Keeps the dashboard container stable and separates web serving from batch data refresh.

## Known Limitations

The paper should acknowledge these honestly:

1. Scraping depends on Jumia page structure, which may change.
2. The dataset is limited to public reviews in one category: mobile accessories.
3. Product selection is biased toward products with visible review counts and higher review volume.
4. Reviewer demographics are unavailable, so demographic consumer behavior cannot be inferred.
5. VADER may underperform on short, informal, or localized Nigerian review language.
6. LLM outputs can vary despite structured schemas, although temperature is set to `0.0`.
7. The analysis reflects available reviews, not all Jumia buyers.
8. Very short reviews may produce general aspects rather than highly specific aspect categories.
9. Repeated scraping may collect duplicates in raw files, though the master dataset deduplicates them.

## Suggested Paper Structure

### Title

Use the official project title unless the instructor requires a shorter version.

### Abstract

Should include:

- Problem: whole-review sentiment and star ratings hide aspect-level opinions in e-commerce review analytics.
- Method: use Jumia Nigeria mobile accessories as a case study, scrape public reviews, and process them with a three-agent LLM pipeline.
- Baseline: VADER.
- Output: Streamlit dashboard and aspect-level sentiment dataset.
- Contribution: a reusable framework for aspect-based e-commerce consumer behavior analytics.

### Keywords

Suggested:

- Aspect-based sentiment analysis
- Multi-agent systems
- Consumer behavior analytics
- E-commerce reviews
- Jumia Nigeria
- Large language models
- Web scraping

### Introduction

Cover:

- Growth of e-commerce in Nigeria.
- Importance of user-generated reviews.
- Limits of star ratings.
- Need for aspect-specific analytics.
- Jumia Nigeria as the case study context, not the only scope of the problem.
- Research aim and objectives.

### Literature Review

Suggested themes:

- Online reviews and consumer decision-making.
- Sentiment analysis in e-commerce.
- Aspect-based sentiment analysis.
- Lexicon-based methods such as VADER.
- LLMs and agentic workflows for text analytics.
- Social/web media analytics dashboards.

The agent should find and cite current sources in APA 7.

### Methodology

Recommended subsections:

1. Research design.
2. Data source and sampling.
3. Web scraping procedure.
4. Data preprocessing and storage.
5. Multi-agent NLP pipeline.
6. VADER baseline.
7. Dashboard design and analysis metrics.
8. Deployment and reproducibility.

### Results and Discussion

Use the dashboard/processed CSV to report:

- Dataset summary.
- Top aspects.
- Overall contextual sentiment distribution.
- Aspect-specific sentiment patterns.
- VADER vs LLM comparison.
- Star rating vs aspect sentiment comparison.
- Review evidence examples.
- Practical interpretation for e-commerce vendors and consumers, using Jumia Nigeria examples.

### Conclusion

Should state:

- Aspect-based analysis gives richer insight than star ratings alone.
- Multi-agent LLM processing can structure noisy review text into useful aspect-level evidence.
- The framework is reusable for other e-commerce platforms and categories.

### Recommendations

Possible recommendations:

- Vendors should monitor aspect-level complaints, not only average ratings.
- Delivery, packaging, and build quality should be analyzed separately from product performance.
- E-commerce platforms could expose aspect-level summaries to buyers and sellers.
- Future work should compare more product categories and larger datasets.

## Files the Paper Agent Should Read

Priority reading order:

1. `research-summary`
2. `README.md`
3. `docs/RESEARCH_PAPER_HANDOFF.md`
4. `docs/RESULTS_ANALYSIS.md`
5. `src/jumia_aspect_agents/data_collection/scraper.py`
6. `src/jumia_aspect_agents/agents/pipeline.py`
7. `src/jumia_aspect_agents/agents/llm.py`
8. `src/jumia_aspect_agents/models/nlp.py`
9. `src/jumia_aspect_agents/analysis/sentiment.py`
10. `app/streamlit_app.py`
11. `deployment/DEPLOY.md`

## Commands for Reproducing the Workflow

Local setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Scrape:

```bash
python scripts/scrape_jumia.py \
  --max-pages 1 \
  --max-products 4 \
  --max-reviews-per-product 10 \
  --max-review-pages-per-product 2
```

Build master dataset:

```bash
python scripts/build_dataset.py
```

Process with rules:

```bash
python scripts/build_dataset.py --mode rules
```

Process with LLM:

```bash
python scripts/build_dataset.py --mode llm
```

Run dashboard:

```bash
streamlit run app/streamlit_app.py
```

Run tests:

```bash
python -m pytest
python -m ruff check app scripts src tests
```

## Current Development Status

Implemented:

- Project scaffold.
- Jumia scraper.
- Raw CSV/JSON outputs.
- Dataset builder and deduplication.
- PydanticAI/LangGraph multi-agent NLP pipeline.
- VADER baseline with Docker-installed lexicon.
- Streamlit dashboard.
- Docker deployment.
- Traefik route and HTTPS.
- GitHub Actions deployment workflow.
- VPS production dashboard.

Final paper-writing task:

- Use the final processed dataset to compute exact results.
- Write the article in the required structure.
- Add APA 7 citations.
- Include screenshots or exported charts from the dashboard if allowed by the assignment.
- Clearly distinguish implemented evidence from interpretation.
