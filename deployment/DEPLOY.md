# VPS Deployment Runbook

Production URL:

```text
https://dashboard.poshlovesdata.dev
```

Deployment flow:

```text
local -> GitHub main -> GitHub Actions -> SSH to VPS -> git pull -> Docker Compose rebuild -> Traefik -> production
```

## First-Time VPS Setup

Clone the repository on the VPS:

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:<your-github-username>/<your-repo-name>.git jumia-aspect-consumer-analytics
cd jumia-aspect-consumer-analytics
```

Create the production environment file:

```bash
cp .env.example .env
nano .env
```

At minimum, set:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
PIPELINE_MODE=llm
JUMIA_CATEGORY_URL=https://www.jumia.com.ng/mobile-accessories/
DASHBOARD_HOST=dashboard.poshlovesdata.dev
TRAEFIK_NETWORK=web
```

Confirm the external Traefik network exists:

```bash
docker network ls | grep web
```

If Traefik already uses the `web` network, do not recreate it.

## Manual Deploy

From the repository root on the VPS:

```bash
git pull origin main
docker compose -f deployment/docker-compose.yml up -d --build dashboard
docker image prune -f
```

Check container status:

```bash
docker compose -f deployment/docker-compose.yml ps
docker compose -f deployment/docker-compose.yml logs -f dashboard
```

## Automated Deploy

GitHub Actions deploys on every push to `main`.

Required repository secrets:

```text
VPS_IP
VPS_USERNAME
VPS_SSH_KEY
```

The workflow:

1. Checks out the repository.
2. Installs Python dependencies.
3. Runs tests.
4. Runs Ruff linting.
5. SSHes into the VPS.
6. Pulls `main`.
7. Rebuilds and restarts the dashboard service.

## Large Dataset Refresh

Run scraper batches on the VPS:

```bash
docker compose -f deployment/docker-compose.yml run --rm scraper
```

Build the canonical master dataset and latest dashboard dataset:

```bash
docker compose -f deployment/docker-compose.yml run --rm processor
```

Restart the dashboard so Streamlit reloads the latest CSV:

```bash
docker compose -f deployment/docker-compose.yml up -d dashboard
```

The dashboard prefers:

```text
data/processed/jumia_reviews_processed_latest.csv
```

Raw scrape batches remain in:

```text
data/raw/
```

## Useful Overrides

For a larger scrape, edit `.env`:

```text
SCRAPER_MAX_PAGES=10
SCRAPER_MAX_PRODUCTS=300
SCRAPER_MAX_REVIEWS_PER_PRODUCT=200
SCRAPER_MAX_REVIEW_PAGES_PER_PRODUCT=20
```

For a cheaper processing test:

```text
PIPELINE_MODE=rules
```

Then run:

```bash
docker compose -f deployment/docker-compose.yml run --rm processor
```

Switch back to:

```text
PIPELINE_MODE=llm
```

for the production research dataset.

## Rollback

Find a previous commit:

```bash
git log --oneline -5
```

Check out that commit temporarily and rebuild:

```bash
git checkout <commit-sha>
docker compose -f deployment/docker-compose.yml up -d --build dashboard
```

Return to normal deployment state:

```bash
git checkout main
git pull origin main
docker compose -f deployment/docker-compose.yml up -d --build dashboard
```

## Troubleshooting

Check Traefik routing labels:

```bash
docker inspect jumia-aspect-dashboard | grep -A 20 traefik
```

Check app logs:

```bash
docker compose -f deployment/docker-compose.yml logs -f dashboard
```

Check generated datasets:

```bash
ls -lah data/raw
ls -lah data/processed
```

Check the Streamlit health endpoint from inside the container:

```bash
docker exec jumia-aspect-dashboard curl -f http://127.0.0.1:8501/_stcore/health
```

Check the public Traefik route:

```bash
curl -I https://dashboard.poshlovesdata.dev
```
