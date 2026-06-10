# Aspect-Based Multi-Agent Consumer Analytics

Research project for COSC878 - Web and Social Media Analytics.

## Title

An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria

## Project Goal

This project collects product review data from Jumia Nigeria's mobile phone accessories market, processes the unstructured review text through a multi-agent NLP pipeline, and visualizes aspect-level consumer sentiment in a Streamlit dashboard.

The implementation is organized to match the research methodology:

1. Data collection from public product review pages.
2. Text cleaning and product routing.
3. Aspect extraction from review text.
4. Aspect-specific sentiment classification.
5. Dashboard visualization and VPS deployment.

## Repository Structure

```text
.
|-- app/
|   `-- streamlit_app.py          # Phase 4 dashboard entrypoint
|-- data/
|   |-- processed/                # Cleaned/enriched review datasets
|   `-- raw/                      # Raw scraped review datasets
|-- deployment/
|   |-- Dockerfile                # Phase 5 container image
|   `-- docker-compose.yml        # Phase 5 Traefik/VPS setup
|-- notebooks/                    # Optional exploration for the paper
|-- reports/
|   `-- figures/                  # Exported plots for the research paper
|-- scripts/
|   |-- run_pipeline.py           # Phase 3 batch processing CLI
|   `-- scrape_jumia.py           # Phase 2 scraping CLI
|-- src/
|   `-- jumia_aspect_agents/
|       |-- agents/               # Multi-agent NLP components
|       |-- analysis/             # Sentiment/aspect aggregation logic
|       |-- config.py             # Environment-based settings
|       |-- data_collection/      # Jumia scraping modules
|       |-- models/               # Pydantic data contracts
|       `-- utils/                # Loguru, IO, retry helpers
|-- tests/                        # Unit and integration tests
|-- .env.example                  # Environment variable template
|-- requirements.txt              # Python dependencies
`-- research-summary              # Course/research brief
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` with your real API key and runtime settings.

## Dataset Workflow

For larger runs, scrape in batches, then build one canonical dataset for the dashboard:

```bash
.venv/bin/python scripts/build_dataset.py
```

This writes:

```text
data/raw/jumia_reviews_raw_master.csv
data/raw/jumia_reviews_raw_master.json
```

To also process the master dataset and create the production dashboard file:

```bash
.venv/bin/python scripts/build_dataset.py --mode llm
```

The dashboard prefers this file when it exists:

```text
data/processed/jumia_reviews_processed_latest.csv
```

## Phase Status

- Phase 1: Environment and project scaffolding. Done.
- Phase 2: Data collection scraper. Done.
- Phase 3: Multi-agent NLP pipeline. Done.
- Phase 4: Streamlit dashboard. Done.
- Phase 5: Docker, Compose, and Traefik deployment.
