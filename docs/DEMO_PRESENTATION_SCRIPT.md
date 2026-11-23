# 10-Minute Demo and Presentation Script

Use this as a rehearsal script. The timing is approximate, so speak naturally and skip small details if time is tight.

## 0:00-0:45 - Opening

Good day everyone. My project is titled "An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria."

The main idea is that e-commerce platforms collect a lot of consumer feedback, but star ratings alone do not explain why consumers are satisfied or dissatisfied. A customer can give a product five stars and still complain about battery life, delivery, build quality, or charging speed.

So this project asks: can we use aspect-based sentiment analysis and a multi-agent LLM pipeline to turn unstructured e-commerce reviews into clearer consumer behavior insights?

## 0:45-1:45 - Problem and Motivation

Traditional review analytics often reduces a review to either a star rating or one overall sentiment label. That is useful, but it is not enough for decision-making.

For example, if a power bank has mostly positive ratings, a seller may assume everything is fine. But if many reviews mention poor battery life or weak build quality, then the real issue is hidden inside the text.

This is why I framed the project as an e-commerce consumer behavior analytics problem. Jumia Nigeria is used as the case study because the platform has public product reviews, and mobile accessories generate aspect-rich feedback about performance, charging, battery, price, delivery, and durability.

## 1:45-2:45 - Research Objectives

The objectives were:

First, to collect public product reviews from Jumia Nigeria's mobile phone accessories category.

Second, to process the reviews into structured aspect-level records.

Third, to compare a contextual LLM-based classifier with a VADER sentiment baseline.

Fourth, to build an interactive dashboard that visualizes consumer sentiment by aspect, product, rating, pipeline mode, and time.

And finally, to deploy the system on a VPS using Docker and Traefik, so the implementation is reproducible and accessible.

## 2:45-4:00 - System Architecture

The system has five main stages.

First is data collection. I used Python, Requests, and BeautifulSoup to scrape public review pages from Jumia Nigeria. The scraper collects the product name, product URL, review title, review body, star rating, date, reviewer name, and other metadata where available.

Second is dataset building. Raw scrapes are saved as timestamped CSV and JSON files, then merged into a deduplicated master dataset using a deterministic review ID.

Third is NLP processing. The system has both a deterministic rules mode and an LLM mode. The rules mode processes the full dataset cheaply. The LLM mode uses a stratified sample because processing thousands of reviews with OpenAI would be expensive.

Fourth is dashboarding. The processed aspect-level dataset is visualized in Streamlit with Plotly charts.

Fifth is deployment. The app is deployed at dashboard.poshlovesdata.dev using Docker Compose and Traefik on my VPS.

## 4:00-5:10 - Multi-Agent NLP Pipeline

The NLP pipeline is designed as three agents.

Agent one is the Cleaner and Router. It cleans the raw review text and infers the product category, such as power bank, charger, cable, phone case, or earbuds.

Agent two is the Aspect Extractor. It identifies the specific product or service aspects discussed in the review, such as Battery life, Build quality, Charging speed, Delivery speed, Price value, and Product performance.

Agent three is the Contextual Classifier. It assigns positive, negative, neutral, or mixed sentiment to each extracted aspect. It also keeps the VADER baseline result so that the dashboard can compare traditional lexicon sentiment with contextual classification.

This design is useful because a single review can contain more than one opinion. For example, a review might praise price value but complain about charging speed. Whole-review sentiment would flatten that complexity.

## 5:10-7:30 - Live Dashboard Demo

Now I will show the deployed dashboard.

Open:

```text
https://dashboard.poshlovesdata.dev
```

At the top of the dashboard, the KPI cards show the final processed dataset. The system contains 4,964 unique reviews, 98 products, 6,582 aspect-level rows, and 59 unique aspects.

The dashboard uses the production latest dataset, which merges the full rules output with the LLM stratified sample.

In the sidebar, you can see filters for pipeline mode, product, aspect, sentiment, rating, and date. The pipeline filter is important because the rules pipeline gives broad coverage, while the LLM pipeline gives more granular contextual analysis.

Now look at the Contextual Sentiment chart. The overall distribution is mostly positive, with 4,546 positive aspect rows. But there are still 1,249 negative rows and 186 mixed rows, which means there is meaningful dissatisfaction inside the review text.

Next, look at Aspect Mentions. The most mentioned aspects are General product experience, Battery life, Product performance, Build quality, Charging speed, Price value, and Portability. This shows that consumers are mainly evaluating functional performance.

Now I will look at the Aspect Sentiment Matrix. This is one of the most important views because it shows which aspects are positive or negative. Price value is strongly positive, with 88.1% positive sentiment. But Battery life and Build quality have more dissatisfaction. Battery life has 25.8% negative sentiment, and Build quality has 26.0% negative sentiment.

This tells us that even when consumers are generally satisfied, there are specific product attributes that vendors need to improve.

Now I will show VADER vs Contextual. VADER agreed with contextual sentiment on 90.0% of non-mixed rows, so it is useful as a baseline. But VADER cannot represent mixed sentiment well, and it sometimes misreads phrases where positive words appear inside a complaint.

Finally, the Review Evidence table shows the actual text evidence and rationale. This makes the analysis explainable because we are not only showing charts; we can trace each aspect sentiment back to review text.

## 7:30-8:50 - Key Findings

The main finding is that aspect-level analysis reveals consumer behavior patterns that star ratings alone would miss.

The final dataset has 4,964 unique reviews and 6,582 aspect-level sentiment rows.

Most sentiment is positive, but the dissatisfaction is concentrated around specific functional aspects.

Battery life is one of the strongest consumer concerns. It has high mention volume and meaningful negative sentiment.

Build quality has the highest negative share among major aspects, at 26.0%.

Charging speed has the lowest average sentiment score among the major aspects.

Price value is the most positively perceived major aspect, with 88.1% positive sentiment.

Another important result is star-rating mismatch. The system found 191 high-rated reviews that still contained negative or mixed aspect-level feedback. This supports the argument that ratings alone are too coarse for consumer behavior analytics.

## 8:50-9:35 - Limitations

There are also limitations.

First, the data comes from one e-commerce platform and one category, so Jumia Nigeria mobile accessories should be treated as a case study, not as a universal representation of all e-commerce behavior.

Second, reviewer demographics are unavailable, so the project cannot make claims about age, gender, income, or location.

Third, the LLM pipeline was run on a 300-review stratified sample instead of the full dataset because of API cost. The full dataset was processed with the rules pipeline.

Fourth, scraping depends on the website structure, which can change over time.

## 9:35-10:00 - Conclusion

In conclusion, this project shows that aspect-based multi-agent analytics can make e-commerce review data more useful.

Instead of only asking whether a review is positive or negative, the system asks what exactly the consumer is talking about and how they feel about that specific aspect.

The deployed dashboard demonstrates that this approach can uncover hidden dissatisfaction, compare contextual sentiment with a baseline method, and provide practical insights for sellers, platforms, and researchers.

Thank you.

## Backup Demo Notes

If the live dashboard is slow, use screenshots from `reports/figures/` or show the local result numbers from `docs/RESULTS_ANALYSIS.md`.

If asked why both rules and LLM were used:

> The rules pipeline gives affordable full-dataset coverage, while the LLM pipeline gives deeper contextual analysis on a stratified sample. Combining them makes the prototype practical for a course project while still demonstrating the research contribution.

If asked why VADER was included:

> VADER is a conventional lexicon-based baseline. It gives a comparison point for the contextual classifier and helps show where simple sentiment methods work and where they miss mixed or context-dependent language.

If asked whether the data is private:

> No. The scraper collected publicly visible product review pages and used polite delays, limited page counts, and reproducible batch jobs.

If asked what is novel:

> The novelty is not just scraping reviews. The contribution is the end-to-end framework: public e-commerce reviews are transformed into aspect-level sentiment evidence using a multi-agent workflow, compared with VADER, and deployed in an interactive dashboard.

