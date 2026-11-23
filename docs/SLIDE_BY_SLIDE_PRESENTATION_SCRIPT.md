# COSC878 Slide-by-Slide Presentation Script

Deck: `reports/COSC878_Jumia_Aspect_Based_Analytics_Demo_Deck.pptx`

Use this script with the 11-slide deck. The timing is designed for a 10-minute academic presentation with a short controlled live demo. Speak naturally; if time is tight, shorten the dashboard demo first.

## Slide 1 - Title

**Timing: 0:00-0:45**

Good day everyone. My project is titled **Aspect-Based Multi-Agent Consumer Analytics**, with Jumia Nigeria mobile phone accessories as the case study.

The broader problem I am addressing is e-commerce consumer behavior analytics. E-commerce platforms collect large amounts of review text, but ratings alone do not explain what customers actually liked or disliked.

In this project, I collected public reviews from Jumia Nigeria, transformed them into aspect-level sentiment records, and built a dashboard to explore the results. The final processed dataset contains **4,964 unique reviews**, **6,582 aspect-level rows**, and a VADER/contextual agreement rate of **90.0%** on non-mixed rows.

## Slide 2 - Research Problem

**Timing: 0:45-1:35**

The core problem is that star ratings are too coarse to explain consumer behavior.

A review can have a high rating and still contain a specific complaint. For example, a customer may say the product was a good buy but also complain that the material becomes rough or does not last. If we only look at the star rating, we miss the product attribute that needs attention.

Whole-review sentiment has the same limitation. It flattens the review into one label, even when the review contains several opinions. This is why the project uses aspect-based analysis: the analytic unit becomes the product or service aspect, not just the entire review.

## Slide 3 - Research Questions

**Timing: 1:35-2:20**

The study is guided by three main research questions.

First, which product and service aspects do consumers discuss most frequently in Jumia Nigeria mobile accessories reviews?

Second, how does aspect-level sentiment differ from what we might infer from star ratings?

Third, how does contextual sentiment compare with a traditional VADER sentiment baseline?

This keeps the project framed as e-commerce consumer behavior analytics. Jumia Nigeria is the empirical case study platform, not a claim about all e-commerce platforms or all Nigerian consumers.

## Slide 4 - Dataset

**Timing: 2:20-3:15**

The production dataset contains **4,964 unique reviews** across **98 products**, producing **6,582 aspect-level rows** and **59 unique aspects**.

The review dates range from **March 27, 2023 to June 12, 2026**.

An important design choice is that the dataset combines two processing modes. The **rules pipeline** processed the full dataset and produced **6,207 aspect rows** across all **4,964 reviews** and **98 products**. This gives broad, low-cost coverage.

The **LLM pipeline** was applied to a **300-review stratified sample**, covering **61 products** and producing **375 aspect rows**. I am not claiming that the LLM processed the full dataset. The LLM sample is used for deeper contextual aspect extraction and classification while controlling API cost.

## Slide 5 - System Architecture

**Timing: 3:15-4:15**

This slide shows the end-to-end architecture.

The pipeline starts with public Jumia review pages from the mobile accessories category. Product discovery and review scraping are handled with Python, Requests, and BeautifulSoup.

The raw scrapes are saved as timestamped CSV and JSON batches, then merged into a deduplicated master dataset. Deduplication is based on a deterministic review ID so repeated scraping does not inflate the results.

After that, the reviews pass through rules and LLM processing to create aspect-level sentiment data. The final output is visualized in a Streamlit and Plotly dashboard, deployed on a VPS using Docker Compose and Traefik.

The key point is that this is not only a notebook analysis. It is a reproducible pipeline from web data collection to deployed analytics.

## Slide 6 - Multi-Agent NLP Pipeline

**Timing: 4:15-5:00**

The NLP pipeline is organized around three conceptual agents.

The first is the **Cleaner and Router**. It cleans short, noisy review text and infers the product category, such as power bank, charger, cable, earbuds, or general mobile accessory.

The second is the **Aspect Extractor**. It identifies specific product or service aspects mentioned in the review, such as battery life, charging speed, build quality, price value, delivery speed, or general product performance.

The third is the **Contextual Classifier**. It assigns sentiment to each aspect as positive, negative, neutral, or mixed.

Across the merged aspect-level dataset, the overall contextual sentiment distribution is **4,546 positive**, **1,249 negative**, **601 neutral**, and **186 mixed** rows. VADER remains in the dataset as a baseline comparison, but the final interpretation is aspect-specific and contextual.

## Slide 7 - Agent Example

**Timing: 5:00-5:45**

This slide gives a simple example of what the agents do.

Suppose the raw review says: **"Good product. d bettry lasts very long bt the charging speed is slow nd d cable is short."**

The first agent, the **Cleaner and Router**, normalizes the noisy text and routes the review to the likely product category. In this example, informal words like "d", "bettry", "bt", and "nd" become "the", "battery", "but", and "and", and the product is treated as a power bank example.

The second agent, the **Aspect Extractor**, separates the review into individual discussion points: **Battery life**, **Charging speed**, and **Cable or build quality**.

The third agent, the **Contextual Classifier**, assigns sentiment to each aspect separately. Battery life is positive because the battery lasts very long. Charging speed is negative because it is slow. Cable or build quality is negative because the cable is short.

The important idea is that the original review is mixed overall. If we only used one sentiment label, we would lose the separate product signals.

## Slide 8 - Dashboard Demo

**Timing: 5:45-7:20**

Now I will briefly show the deployed dashboard.

**Demo cue:** Open `https://dashboard.poshlovesdata.dev`.

At the top, the KPI cards show the final production dataset: **4,964 reviews**, **98 products**, **6,582 aspect rows**, and **59 aspects**.

The sidebar filters are important. I can filter by pipeline mode, product, aspect, sentiment, rating, and date. The pipeline filter lets me separate the broad rules output from the smaller LLM sample.

Next, I would point to the sentiment and aspect charts. The dataset is mostly positive, but the negative and mixed rows show that there is still meaningful dissatisfaction inside the review text.

Then I would filter to an aspect such as **Battery life** or **Build quality**. This demonstrates the value of aspect-level analysis: instead of asking only whether reviews are positive overall, we can ask which product attributes are causing satisfaction or dissatisfaction.

Finally, the VADER versus contextual chart and review evidence table make the results explainable. The evidence table lets us trace the chart result back to actual review text and aspect evidence.

## Slide 9 - Key Findings

**Timing: 7:20-8:25**

The findings show that consumers mostly discuss functional product attributes.

The most frequent aspect is **General product experience**, with **2,094 rows**, partly because many reviews are short comments like "good", "nice", or "bad".

Among more specific aspects, **Battery life** is the most discussed, with **1,409 rows**. Product performance, build quality, charging speed, price value, portability, and delivery speed also appear frequently.

The strongest positive aspect is **Price value**, with **88.1% positive** sentiment. This suggests that many buyers felt the products were acceptable for the price.

However, the pain points are more concentrated around functional reliability. **Battery life** has **25.8% negative** sentiment and **6.2% mixed** sentiment. **Build quality** has the highest negative share among major aspects at **26.0%**. Charging speed also has the lowest average sentiment score among the major aspects.

## Slide 10 - Why Aspects Matter

**Timing: 8:25-9:20**

This slide shows why aspect-based analysis matters.

The system found **191 high-rated reviews** that still contained negative or mixed aspect-level feedback. In other words, a customer could give four or five stars but still mention a real product weakness.

This is important for vendors and platforms because aggregate ratings can hide repair signals. A high rating may suggest that the customer is generally satisfied, but the text may still reveal durability, battery, material, charging, or performance concerns.

The VADER comparison also supports the need for contextual analysis. VADER agreed with contextual sentiment on **90.0%** of non-mixed rows, so it is useful as a baseline. But it cannot represent mixed sentiment well, and it can misread phrases where positive words appear inside a complaint, such as "good but do not last long."

## Slide 11 - Limitations and Conclusion

**Timing: 9:20-10:00**

There are several limitations.

First, the data comes from one platform and one product category, so Jumia Nigeria mobile accessories should be treated as a case study, not as a universal representation of all e-commerce behavior.

Second, the project uses public reviews only, and reviewer demographics are not available. So I do not make claims about age, gender, income, location, or demographic behavior.

Third, the LLM run is a **300-review stratified sample**, not a full-dataset LLM pass. The full dataset was processed with the rules pipeline.

Finally, scraping depends on website structure, which can change over time.

In conclusion, this project shows that aspect-based multi-agent analytics gives a more actionable view of e-commerce review data than ratings or whole-review sentiment alone. Instead of only asking whether a review is positive, the system asks what the consumer is reacting to and how they feel about that specific aspect.

Thank you.

## If The Live Demo Is Slow

Use the screenshot in slide 8 and continue speaking from the demo script:

The dashboard shows the same production dataset used in the paper and deck. The important parts are the KPI cards, the pipeline filter, the aspect mention chart, the aspect sentiment matrix, the VADER comparison, and the review evidence table.

Then continue to slide 9.

## Short Answers For Questions

**Why use both rules and LLM?**

The rules pipeline gives affordable full-dataset coverage. The LLM pipeline gives deeper contextual reasoning on a stratified sample. Combining them makes the system practical while still demonstrating the research contribution.

**Did the LLM process all reviews?**

No. The LLM processed a 300-review stratified sample covering 61 products and producing 375 aspect rows. The full 4,964-review dataset was processed by the rules pipeline.

**Can this make demographic claims?**

No. The dataset does not include reliable demographic information, so the analysis is about review behavior and product/service aspects, not demographic behavior.

**What is the main contribution?**

The contribution is the end-to-end framework: public e-commerce reviews are scraped, deduplicated, transformed into aspect-level sentiment evidence through a multi-agent workflow, compared with VADER, and visualized in a deployed dashboard.
