from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/jumia_reviews_processed_latest.csv"
FIGURES = ROOT / "reports/figures"
OUT = ROOT / "reports/COSC878_Journal_Article_Jumia_Aspect_Based_Analytics.docx"
DASHBOARD_SCREENSHOT = FIGURES / "paper_dashboard_screenshot.png"
DASHBOARD_CONTACT_SHEET = FIGURES / "paper_dashboard_section_screenshots.png"
AUTHOR = "Oluwapelumi Oyeyemi Oshundiya"
AUTHOR_EMAIL = "oshundiya2255@pg.babcock.edu.ng"
REPOSITORY_URL = "https://github.com/poshlovesdata/ecommerce-sentiment-agents.git"
DASHBOARD_URL = "https://dashboard.poshlovesdata.dev"

SENTIMENT_COUNTS = pd.Series(
    {"positive": 4546, "negative": 1249, "neutral": 601, "mixed": 186},
    name="rows",
)

ASPECT_COUNTS = pd.Series(
    {
        "General product experience": 2094,
        "Battery life": 1409,
        "Product performance": 1017,
        "Build quality": 782,
        "Charging speed": 590,
        "Price value": 352,
        "Portability": 234,
        "Delivery speed": 44,
        "Durability": 6,
        "Battery": 3,
    },
    name="rows",
)

ASPECT_SENTIMENT_PERCENT = pd.DataFrame(
    {
        "positive": [80.6, 56.8, 67.2, 67.8, 56.1, 88.1, 71.8, 56.8],
        "negative": [9.9, 25.8, 22.4, 26.0, 23.1, 6.8, 16.2, 13.6],
        "neutral": [8.5, 11.1, 7.7, 2.8, 19.3, 3.4, 10.7, 29.5],
        "mixed": [0.9, 6.2, 2.8, 3.5, 1.5, 1.7, 1.3, 0.0],
    },
    index=[
        "General product experience",
        "Battery life",
        "Product performance",
        "Build quality",
        "Charging speed",
        "Price value",
        "Portability",
        "Delivery speed",
    ],
)

VADER_CROSSTAB = pd.DataFrame(
    {
        "negative": [921, 173, 155],
        "neutral": [0, 589, 12],
        "positive": [106, 192, 4248],
    },
    index=["negative", "neutral", "positive"],
)


def sentiment_score(label: str) -> int:
    return {"positive": 1, "neutral": 0, "mixed": 0, "negative": -1}.get(str(label).lower(), 0)


def money_int(value: int | float) -> str:
    return f"{int(value):,}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def load_data() -> pd.DataFrame:
    if DATA.exists():
        df = pd.read_csv(DATA)
        if not df.empty and "contextual_sentiment" in df.columns:
            df["contextual_sentiment"] = df["contextual_sentiment"].str.lower()
            df["pipeline_mode"] = df["pipeline_mode"].str.lower()
            df["score_int"] = df["contextual_sentiment"].map(sentiment_score)
            return df
    return pd.DataFrame()


def make_figures(df: pd.DataFrame) -> dict[str, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#1F2937",
            "xtick.color": "#374151",
            "ytick.color": "#374151",
        }
    )
    palette = {
        "positive": "#2E7D32",
        "negative": "#B42318",
        "neutral": "#6B7280",
        "mixed": "#C47F00",
    }
    paths: dict[str, Path] = {}

    sentiment_counts = SENTIMENT_COUNTS.reindex(["positive", "negative", "neutral", "mixed"])
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=180)
    bars = ax.bar(
        sentiment_counts.index,
        sentiment_counts.values,
        color=[palette.get(x, "#4B5563") for x in sentiment_counts.index],
    )
    ax.set_title("Overall Aspect-Level Sentiment Distribution")
    ax.set_xlabel("Contextual sentiment")
    ax.set_ylabel("Aspect rows")
    ax.bar_label(bars, labels=[f"{int(v):,}" for v in sentiment_counts.values], padding=3, fontsize=8)
    fig.tight_layout()
    paths["sentiment"] = FIGURES / "paper_sentiment_distribution.png"
    fig.savefig(paths["sentiment"], bbox_inches="tight")
    plt.close(fig)

    aspect_counts = ASPECT_COUNTS.sort_values()
    fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=180)
    bars = ax.barh(aspect_counts.index, aspect_counts.values, color="#2E74B5")
    ax.set_title("Most Frequently Mentioned Aspects")
    ax.set_xlabel("Aspect rows")
    ax.bar_label(bars, labels=[f"{int(v):,}" for v in aspect_counts.values], padding=3, fontsize=8)
    fig.tight_layout()
    paths["aspects"] = FIGURES / "paper_top_aspects.png"
    fig.savefig(paths["aspects"], bbox_inches="tight")
    plt.close(fig)

    matrix_pct = ASPECT_SENTIMENT_PERCENT[["positive", "negative", "neutral", "mixed"]]
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=180)
    left = [0] * len(matrix_pct)
    for col in matrix_pct.columns:
        vals = matrix_pct[col].values
        ax.barh(matrix_pct.index, vals, left=left, color=palette[col], label=col.title())
        left = [l + v for l, v in zip(left, vals)]
    ax.set_title("Aspect Sentiment Mix for Top Aspects")
    ax.set_xlabel("Share of aspect rows (%)")
    ax.set_xlim(0, 100)
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.28), frameon=False)
    ax.invert_yaxis()
    fig.tight_layout()
    paths["matrix"] = FIGURES / "paper_aspect_sentiment_mix.png"
    fig.savefig(paths["matrix"], bbox_inches="tight")
    plt.close(fig)

    crosstab = VADER_CROSSTAB.loc[["negative", "neutral", "positive"], ["negative", "neutral", "positive"]]
    fig, ax = plt.subplots(figsize=(5.6, 4.8), dpi=180)
    im = ax.imshow(crosstab.values, cmap="Blues")
    ax.set_xticks(range(3), labels=[c.title() for c in crosstab.columns])
    ax.set_yticks(range(3), labels=[i.title() for i in crosstab.index])
    ax.set_xlabel("Contextual sentiment")
    ax.set_ylabel("VADER label")
    ax.set_title("VADER vs Contextual Sentiment")
    for i in range(3):
        for j in range(3):
            val = int(crosstab.iloc[i, j])
            ax.text(j, i, f"{val:,}", ha="center", va="center", color="#111827", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    paths["vader"] = FIGURES / "paper_vader_contextual_matrix.png"
    fig.savefig(paths["vader"], bbox_inches="tight")
    plt.close(fig)

    make_dashboard_contact_sheet()

    return paths


def make_dashboard_contact_sheet() -> None:
    """Create a compact appendix image from dashboard section screenshots, if present."""

    try:
        from PIL import Image, ImageDraw
    except Exception:
        return

    screenshot_dir = ROOT / "dashboard_screenshots"
    files = sorted(screenshot_dir.glob("*.png"))
    if not files:
        return

    labels = [
        "KPI summary",
        "Sentiment and aspect mentions",
        "Aspect sentiment matrix",
        "VADER and rating comparison",
        "Review timeline",
        "Review evidence table",
        "Dashboard filters",
    ]
    thumbs = []
    for index, file_path in enumerate(files[:7]):
        image = Image.open(file_path).convert("RGB")
        image.thumbnail((620, 310))
        canvas = Image.new("RGB", (660, 380), "white")
        canvas.paste(image, ((660 - image.width) // 2, 20))
        draw = ImageDraw.Draw(canvas)
        label = labels[index] if index < len(labels) else file_path.stem
        draw.text((24, 340), label, fill=(31, 41, 55))
        thumbs.append(canvas)

    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 660, rows * 380), "white")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 660, (index // cols) * 380))
    sheet.save(DASHBOARD_CONTACT_SHEET)


def configure_styles(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10

    for style_name, size, color, before, after in [
        ("Heading 1", 16, "2E74B5", 16, 8),
        ("Heading 2", 13, "2E74B5", 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ]:
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)


def add_title_page(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(
        "An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: "
        "A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria"
    )
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor.from_string("0B2545")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Submitted by: {AUTHOR}")
    run.font.size = Pt(12)
    run.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Email: {AUTHOR_EMAIL}")
    run.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"GitHub Repository: {REPOSITORY_URL}")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Live Dashboard: {DASHBOARD_URL}")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("COSC878 - Web and Social Media Analytics")
    run.font.size = Pt(12)
    run.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Journal Article Assignment").italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("June 2026")
    doc.add_page_break()


def add_paragraph(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.add_run(text)


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Number")


def add_table(doc: Document, rows: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, text in enumerate(rows[0]):
        hdr[i].text = text
        for p in hdr[i].paragraphs:
            for run in p.runs:
                run.bold = True
    for row in rows[1:]:
        cells = table.add_row().cells
        for i, text in enumerate(row):
            cells[i].text = text
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.size = Pt(9)
    doc.add_paragraph()


def add_figure(doc: Document, path: Path, caption: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(6.15))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)


def build_doc(df: pd.DataFrame, figs: dict[str, Path]) -> None:
    doc = Document()
    doc.core_properties.author = AUTHOR
    doc.core_properties.title = (
        "An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: "
        "A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria"
    )
    configure_styles(doc)
    add_title_page(doc)

    doc.add_heading("Abstract", level=1)
    add_paragraph(
        doc,
        "E-commerce platforms generate large quantities of consumer review data, but conventional "
        "analytics often reduce this evidence to star ratings or whole-review sentiment scores. "
        "This paper presents an aspect-based multi-agent framework for consumer behavior analytics, "
        "using mobile phone accessories reviews from Jumia Nigeria as a case study. Public review "
        "data were scraped, deduplicated, and processed into aspect-level records. A deterministic "
        "rules pipeline processed the full dataset, while a three-agent LLM workflow was applied to "
        "a 300-review stratified sample for contextual aspect extraction and sentiment classification. "
        "The merged verified dataset contains 4,964 unique reviews, 98 products, 6,582 aspect-level "
        "rows, and 59 unique aspects. Results show that overall sentiment was largely positive "
        "(4,546 positive rows), but aspect-level analysis exposed important negative and mixed "
        "feedback around battery life, build quality, and charging speed. VADER and contextual "
        "sentiment agreed on 90.0% of non-mixed rows, but VADER could not represent mixed sentiment "
        "and sometimes misread contextual complaints. The study demonstrates that aspect-based "
        "analytics provides richer evidence for e-commerce decision-making than aggregate ratings alone."
    )
    doc.add_heading("Keywords", level=2)
    add_paragraph(
        doc,
        "Aspect-based sentiment analysis; consumer behavior analytics; e-commerce reviews; "
        "multi-agent systems; Jumia Nigeria; large language models"
    )

    doc.add_heading("Introduction", level=1)
    add_paragraph(
        doc,
        "Digital commerce increasingly depends on user-generated evidence. Product reviews, star ratings, "
        "review dates, and post-purchase comments give buyers social proof and give sellers operational "
        "signals about product quality, delivery experience, and value perception. In web and social media "
        "analytics, this kind of consumer-generated text is valuable because it connects behavioral traces "
        "with interpretive content. A review does not merely record that a consumer bought an item; it often "
        "explains which features satisfied or disappointed the buyer."
    )
    add_paragraph(
        doc,
        "However, e-commerce review analytics is frequently summarized at a level that hides the most useful "
        "information. A five-star review can include a complaint about durability; a one-star review can still "
        "praise price value; and a short informal review can contain several aspect-specific opinions. This "
        "paper frames the problem broadly as e-commerce consumer behavior analytics and uses Jumia Nigeria's "
        "mobile phone accessories category as the empirical case study. Jumia is therefore treated as a site "
        "for observing the problem, not as the boundary of the problem domain."
    )
    add_paragraph(
        doc,
        "The study proposes an aspect-based multi-agent framework that decomposes review text into product "
        "or service aspects and assigns contextual sentiment to each aspect. The framework combines public "
        "web data collection, deterministic baseline processing, LLM-based contextual analysis, VADER baseline "
        "sentiment, and an interactive Streamlit dashboard. Its central argument is that consumer behavior "
        "analytics becomes more actionable when the unit of analysis shifts from whole reviews to aspect-level "
        "evidence."
    )
    doc.add_heading("Significance of the Study", level=2)
    add_paragraph(
        doc,
        "The study is significant for web and social media analytics because it demonstrates how publicly available "
        "e-commerce reviews can be transformed into structured consumer insight using practical course techniques: "
        "web scraping, sentiment analysis, LLM-assisted text analytics, baseline comparison, and dashboard visualization. "
        "For vendors, the framework identifies specific product attributes that require attention rather than relying "
        "only on average star ratings. For researchers, it provides a reproducible case study showing how aspect-based "
        "review analytics can be applied in an emerging-market e-commerce context without making unsupported demographic "
        "claims."
    )

    doc.add_heading("Problem Statement", level=1)
    add_paragraph(
        doc,
        "E-commerce platforms contain large volumes of unstructured consumer feedback, yet many analytical "
        "approaches rely on star ratings or whole-review polarity. These summaries are insufficient for "
        "understanding the specific product and service factors that shape satisfaction. In mobile phone "
        "accessories markets, consumer concerns may involve battery life, charging speed, build quality, "
        "delivery speed, packaging, price value, and general performance. Collapsing these concerns into "
        "one rating can obscure hidden dissatisfaction and make it difficult for vendors to prioritize product "
        "improvements."
    )
    add_paragraph(
        doc,
        "The problem is not merely technical. It affects how online sellers, marketplace operators, and consumers "
        "interpret review signals. If a high average rating masks recurring complaints about durability, a seller "
        "may underestimate quality problems. If a low rating includes positive remarks about price value, a vendor "
        "may overlook strengths that should be preserved. Therefore, a more granular analytics framework is needed "
        "to extract, classify, and visualize aspect-specific sentiment from noisy public reviews."
    )

    doc.add_heading("Research Objectives and Questions", level=1)
    doc.add_heading("Research Objectives", level=2)
    add_numbered(
        doc,
        [
            "Collect public e-commerce review data from Jumia Nigeria's mobile phone accessories category as a case study.",
            "Preserve review metadata including product name, review text, star rating, review date, reviewer name, product URL, source URL, and verification status where available.",
            "Design a multi-agent aspect-based sentiment analysis pipeline using typed outputs and graph-based orchestration.",
            "Compare contextual aspect sentiment with VADER baseline sentiment.",
            "Visualize consumer behavior patterns across products, aspects, sentiment labels, star ratings, and dates.",
            "Evaluate whether aspect-based analytics reveals insights that aggregate ratings alone do not show.",
        ],
    )
    doc.add_heading("Research Questions", level=2)
    add_numbered(
        doc,
        [
            "Which product and service aspects are most frequently discussed in the Jumia Nigeria mobile accessories case study?",
            "How does aspect-level sentiment differ from whole-review star-rating interpretation?",
            "Which aspects attract the highest positive, negative, neutral, or mixed sentiment?",
            "How does contextual aspect sentiment compare with a VADER lexicon-based baseline?",
            "What practical consumer behavior insights can e-commerce vendors extract from aspect-based review analytics?",
        ],
    )

    doc.add_heading("Literature Review", level=1)
    doc.add_heading("Online Reviews and Consumer Behavior", level=2)
    add_paragraph(
        doc,
        "Online reviews are a major source of consumer information because they provide experiential evidence "
        "from prior buyers rather than seller-controlled descriptions. Chen et al. [1] show that online reviews "
        "influence purchasing decisions and that negative comments can receive substantial consumer attention. "
        "This supports the relevance of review analytics for e-commerce decision-making: consumer feedback is not "
        "only a post-purchase artifact but also a pre-purchase information source."
    )
    add_paragraph(
        doc,
        "Opinion mining research similarly treats online reviews and blogs as opinion-rich resources that require "
        "computational methods for summarization, extraction, and decision support [2]. For e-commerce, "
        "the review text is especially important because star ratings alone do not explain why consumers evaluate a "
        "product positively or negatively."
    )
    doc.add_heading("Sentiment Analysis and Its Limits", level=2)
    add_paragraph(
        doc,
        "Sentiment analysis identifies affective or evaluative orientation in text. Traditional approaches include "
        "lexicon-based methods, machine learning classifiers, and hybrid systems [2]. VADER is a widely "
        "used rule-based model designed for short, informal social media text. Hutto and Gilbert [3] describe it as "
        "a parsimonious model that combines validated lexical features with grammatical and syntactic rules for sentiment "
        "intensity. This makes VADER appropriate as a baseline for short review snippets, but it still has difficulty "
        "representing mixed opinions and context-specific aspect meaning."
    )
    doc.add_heading("Aspect-Based Sentiment Analysis", level=2)
    add_paragraph(
        doc,
        "Aspect-based sentiment analysis responds to the limits of document-level sentiment by identifying the specific "
        "entity attributes discussed in a text and assigning sentiment to each attribute. Brauwers and Frasincar [4] "
        "describe aspect-based sentiment classification as a fine-grained method for extracting sentiment information "
        "from sentences or documents. This study follows that tradition by transforming each review into one or more "
        "aspect-level records."
    )
    add_paragraph(
        doc,
        "The aspect-based approach is particularly suitable for consumer electronics and accessories because consumers "
        "often evaluate functional attributes separately. A power bank may be praised for price value while criticized "
        "for battery life; earbuds may be liked for portability but disliked for bass quality; a charger may receive "
        "positive comments about speed but negative comments about cable durability. These examples show why aspect-level "
        "modeling can produce more actionable analytics than a single polarity label."
    )
    doc.add_heading("Large Language Models and Multi-Agent Analytics", level=2)
    add_paragraph(
        doc,
        "Recent work has examined the use of large language models for aspect-based sentiment analysis. Zhou et al. [5] "
        "evaluate LLMs across multiple ABSA subtasks and datasets, showing that LLMs can be competitive in fine-tuning "
        "and in-context settings while still requiring careful task formulation. This study uses LLMs not as a full-dataset "
        "replacement for deterministic processing, but as a contextual analysis layer applied to a stratified sample."
    )
    add_paragraph(
        doc,
        "Multi-agent design is useful because review analytics involves distinct subtasks: text cleaning, aspect extraction, "
        "and contextual classification. LangGraph is used as a low-level orchestration framework for stateful agent workflows "
        "[8], while PydanticAI provides typed agent outputs for generative AI workflows [9]. "
        "The use of structured schemas reduces free-text ambiguity and improves reproducibility of the processing pipeline."
    )
    doc.add_heading("Research Gap", level=2)
    add_paragraph(
        doc,
        "The reviewed literature establishes that online reviews influence consumer behavior, sentiment analysis can summarize "
        "opinionated text, and ABSA can provide fine-grained aspect-level interpretation. The gap addressed here is the design "
        "and application of a reproducible, aspect-based multi-agent framework for e-commerce consumer behavior analytics in "
        "an emerging-market case study, while explicitly distinguishing broad deterministic coverage from sampled LLM-based "
        "contextual analysis."
    )

    doc.add_heading("Methodology", level=1)
    doc.add_heading("Research Design", level=2)
    add_paragraph(
        doc,
        "The study used a computational case-study design. The broader research object was e-commerce consumer behavior "
        "analytics; the empirical site was Jumia Nigeria's mobile phone accessories category. The design combined web scraping, "
        "data cleaning, aspect-based sentiment processing, baseline comparison, descriptive analytics, and dashboard visualization."
    )
    doc.add_heading("Data Source and Sampling", level=2)
    add_paragraph(
        doc,
        "The source website was Jumia Nigeria, specifically public product and review pages in the mobile accessories category. "
        "The scraper discovered products from category listing pages, prioritized products with visible review counts, and collected "
        "review fields from product review pages. The final verified dataset contains 4,964 unique reviews from 98 products. "
        "The dataset reflects available public reviews and does not represent all Jumia buyers."
    )
    doc.add_heading("Data Collection Procedure", level=2)
    add_paragraph(
        doc,
        "Data collection used Python requests for HTTP retrieval and BeautifulSoup for HTML parsing. The scraper preserved product "
        "name, product URL, SKU where available, review title, review body, star rating, review date, reviewer name, verified purchase "
        "flag where available, source URL, and scrape timestamp. Timestamped raw CSV and JSON files were retained, then merged into a "
        "deduplicated master dataset using a deterministic review_id generated from product and review fields."
    )
    add_paragraph(
        doc,
        "The scraping procedure used limited page counts, retry handling, randomized delays, and a research-identifying user agent. "
        "Only publicly visible review data were collected. This follows responsible research practice by avoiding private data and "
        "limiting collection to the scope needed for the course project, consistent with recent guidance on web-scraped research data "
        "and its legal, ethical, institutional, and scientific considerations [6], [7]."
    )
    doc.add_heading("Analytical Pipeline", level=2)
    add_paragraph(
        doc,
        "The final processed dataset is aspect-level rather than review-level. One review can therefore generate multiple records, "
        "each containing a product aspect, evidence span, VADER baseline label, contextual sentiment label, score, and rationale. "
        "The processing workflow had two complementary modes. The deterministic rules pipeline processed the full dataset and produced "
        "6,207 aspect rows. The LLM pipeline processed a 300-review stratified sample covering 61 products and produced 375 aspect rows. "
        "The two outputs were merged into one dashboard dataset with a pipeline_mode field so results could be filtered by method."
    )
    doc.add_heading("Multi-Agent Framework", level=2)
    add_paragraph(
        doc,
        "The LLM workflow consisted of three agents coordinated through LangGraph. Agent 1, the cleaner/router, cleaned review text "
        "without changing its meaning and inferred a product category. Agent 2, the aspect extractor, identified concrete product or "
        "service aspects and evidence spans. Agent 3, the contextual classifier, assigned positive, negative, neutral, or mixed sentiment "
        "to each extracted aspect using the review context, extracted evidence, and VADER baseline score. Pydantic schemas constrained "
        "outputs into structured objects such as CleanedReview, AspectExtractionResult, and AspectSentiment."
    )
    doc.add_heading("Baseline and Evaluation Metrics", level=2)
    add_paragraph(
        doc,
        "VADER was used as a conventional lexicon-based baseline. The study compared VADER labels with contextual labels on non-mixed "
        "rows, because VADER does not provide a mixed sentiment class. Metrics included dataset size, product coverage, aspect frequency, "
        "sentiment distribution, aspect-specific sentiment share, VADER/contextual agreement, and mismatches between star ratings and "
        "aspect sentiment."
    )

    doc.add_heading("System Architecture", level=1)
    add_paragraph(
        doc,
        "The architecture follows a source-to-insight pipeline: public category pages lead to product discovery; product pages lead to "
        "review scraping; raw batches are merged into a deduplicated master dataset; rules and LLM pipelines generate aspect-level rows; "
        "the processed file powers a Streamlit dashboard; and Docker, GitHub Actions, and Traefik support production deployment. This "
        "architecture makes the framework reproducible while keeping raw data, processed data, and visualization layers separate."
    )
    add_table(
        doc,
        [
            ["Layer", "Role in the framework"],
            ["Data source", "Public Jumia Nigeria mobile accessories product and review pages."],
            ["Collection", "Requests, BeautifulSoup, retry handling, randomized delays, and timestamped raw outputs."],
            ["Storage", "Raw CSV/JSON batches, deduplicated master dataset, and processed aspect-level CSV/JSON files."],
            ["Processing", "Rules pipeline for full-dataset coverage; LLM multi-agent pipeline for stratified contextual analysis."],
            ["Baseline", "VADER sentiment labels and compound scores for comparison."],
            ["Visualization", "Streamlit dashboard with filters, KPI cards, charts, matrices, timeline, and evidence table."],
            ["Deployment", "Docker Compose, GitHub Actions, VPS deployment, and Traefik reverse proxy."],
        ],
        widths=[1.45, 4.85],
    )

    doc.add_heading("Implementation", level=1)
    add_paragraph(
        doc,
        "The implementation was organized as a Python project. Data collection modules handled Jumia page parsing and dataset assembly. "
        "Agent modules implemented the rules pipeline, LLM prompts, and LangGraph orchestration. Pydantic models defined review and NLP "
        "contracts. Analysis modules computed VADER sentiment. A Streamlit application loaded the latest processed file and presented "
        "interactive filters for pipeline mode, product, aspect, sentiment, rating, and date."
    )
    add_paragraph(
        doc,
        "The production dashboard defaulted to data/processed/jumia_reviews_processed_latest.csv, which merged the full rules output and "
        "the LLM stratified sample. This design allowed the paper to report broad quantitative results from full-dataset rules processing "
        "while discussing contextual LLM behavior from a cost-controlled sample. The implementation deliberately avoids claiming that the "
        f"LLM processed all 4,964 reviews. The reproducible source repository is {REPOSITORY_URL}, and the deployed dashboard is available at "
        f"{DASHBOARD_URL}."
    )
    if DASHBOARD_SCREENSHOT.exists():
        add_figure(
            doc,
            DASHBOARD_SCREENSHOT,
            "Figure 1. Production Streamlit dashboard showing KPI cards, filters, contextual sentiment, aspect mentions, and the aspect sentiment matrix.",
        )

    doc.add_heading("Results and Discussion", level=1)
    doc.add_heading("Dataset Summary", level=2)
    add_table(
        doc,
        [
            ["Dataset signal", "Verified value"],
            ["Unique reviews", "4,964"],
            ["Unique products", "98"],
            ["Merged aspect-level rows", "6,582"],
            ["Unique aspects", "59"],
            ["Rules aspect rows", "6,207"],
            ["LLM stratified sample", "300 reviews, 61 products, 375 aspect rows"],
            ["Review date range", "March 27, 2023 to June 12, 2026"],
        ],
        widths=[2.55, 3.75],
    )
    add_paragraph(
        doc,
        "The merged dataset provided two analytical views. The rules pipeline provided the broad quantitative base across all unique reviews, "
        "while the LLM sample provided a contextual view across a stratified subset. The difference in unique aspect counts is meaningful: "
        "rules produced eight standardized aspect types across the full dataset, while the LLM sample identified 59 unique aspects from 300 "
        "reviews. This suggests a trade-off between standardization and contextual granularity."
    )
    add_figure(doc, figs["sentiment"], "Figure 2. Overall aspect-level contextual sentiment distribution.")
    add_paragraph(
        doc,
        "Across all merged aspect rows, sentiment was predominantly positive: 4,546 positive, 1,249 negative, 601 neutral, and 186 mixed rows. "
        "The positive majority indicates that many consumers expressed satisfaction with the products, but the 1,435 negative or mixed rows "
        "show that meaningful dissatisfaction remained visible once reviews were decomposed into aspects."
    )

    doc.add_heading("Most Discussed Aspects", level=2)
    add_figure(doc, figs["aspects"], "Figure 3. Top aspect mentions in the merged processed dataset.")
    add_table(
        doc,
        [
            ["Aspect", "Rows"],
            ["General product experience", "2,094"],
            ["Battery life", "1,409"],
            ["Product performance", "1,017"],
            ["Build quality", "782"],
            ["Charging speed", "590"],
            ["Price value", "352"],
            ["Portability", "234"],
            ["Delivery speed", "44"],
        ],
        widths=[3.3, 1.1],
    )
    add_paragraph(
        doc,
        "General product experience was the most frequent category because many reviews were short comments such as general praise or complaint. "
        "Among more specific aspects, battery life, product performance, build quality, and charging speed dominated. This pattern reflects the "
        "functional nature of mobile accessories: consumers evaluate whether products last, charge effectively, work reliably, and justify their price."
    )

    doc.add_heading("Aspect-Specific Sentiment", level=2)
    add_figure(doc, figs["matrix"], "Figure 4. Sentiment mix for high-volume aspects.")
    add_table(
        doc,
        [
            ["Aspect", "Rows", "Positive", "Negative", "Neutral", "Mixed", "Avg score"],
            ["General product experience", "2,094", "80.6%", "9.9%", "8.5%", "0.9%", "0.480"],
            ["Battery life", "1,409", "56.8%", "25.8%", "11.1%", "6.2%", "0.201"],
            ["Product performance", "1,017", "67.2%", "22.4%", "7.7%", "2.8%", "0.287"],
            ["Build quality", "782", "67.8%", "26.0%", "2.8%", "3.5%", "0.292"],
            ["Charging speed", "590", "56.1%", "23.1%", "19.3%", "1.5%", "0.180"],
            ["Price value", "352", "88.1%", "6.8%", "3.4%", "1.7%", "0.485"],
            ["Portability", "234", "71.8%", "16.2%", "10.7%", "1.3%", "0.316"],
            ["Delivery speed", "44", "56.8%", "13.6%", "29.5%", "0.0%", "0.241"],
        ],
        widths=[1.75, 0.58, 0.75, 0.75, 0.75, 0.65, 0.75],
    )
    add_paragraph(
        doc,
        "Price value had the strongest positive profile among major aspects, with 88.1% positive sentiment. By contrast, battery life, build "
        "quality, and charging speed combined high mention frequency with notable negative sentiment. Build quality had the highest negative "
        "share among high-volume aspects, while charging speed had the lowest average score among major aspects. These findings suggest that "
        "vendors should not interpret positive overall sentiment as evidence that all product attributes are performing well."
    )

    doc.add_heading("VADER and Contextual Sentiment", level=2)
    add_figure(doc, figs["vader"], "Figure 5. VADER/contextual sentiment crosstab for non-mixed rows.")
    add_table(
        doc,
        [
            ["VADER label", "Context negative", "Context neutral", "Context positive"],
            ["Negative", "921", "0", "106"],
            ["Neutral", "173", "589", "192"],
            ["Positive", "155", "12", "4,248"],
        ],
        widths=[1.55, 1.35, 1.35, 1.35],
    )
    add_paragraph(
        doc,
        "VADER and contextual sentiment agreed on 5,758 of 6,396 non-mixed rows, an agreement rate of 90.0%. This indicates that VADER was a "
        "useful baseline for many short review snippets. Nevertheless, the disagreements were analytically important. VADER could not represent "
        "mixed sentiment and sometimes misread phrases where positive lexical cues appeared inside complaints. For example, a statement such as "
        "'good but do not last long' can contain a positive word while communicating dissatisfaction with durability."
    )

    doc.add_heading("Star Ratings Versus Aspect Feedback", level=2)
    add_paragraph(
        doc,
        "The analysis found 239 negative or mixed aspect rows inside 191 high-rated reviews. It also found 335 positive aspect rows inside 283 "
        "low-rated reviews. These mismatches confirm that star ratings are too coarse for consumer behavior analytics. A high rating may coexist "
        "with criticism of material quality or battery durability; a low rating may still include appreciation for price value or portability. "
        "Aspect-level modeling therefore uncovers hidden consumer priorities that rating averages cannot express."
    )
    add_table(
        doc,
        [
            ["Mismatch type", "Evidence from verified results", "Interpretation"],
            ["High rating with negative/mixed aspects", "239 rows across 191 reviews", "Overall satisfaction can mask feature-level dissatisfaction."],
            ["Low rating with positive aspects", "335 rows across 283 reviews", "Overall dissatisfaction can coexist with valued product attributes."],
            ["Mixed LLM classifications", "186 merged rows", "Some reviews contain simultaneous praise and criticism."],
        ],
        widths=[1.7, 1.7, 2.7],
    )

    doc.add_heading("Consumer Behavior Interpretation", level=2)
    add_paragraph(
        doc,
        "Within the Jumia Nigeria mobile accessories case study, consumers appeared to evaluate products primarily by functional performance. "
        "Battery life, charging speed, product performance, and build quality were more prominent than service aspects such as delivery speed. "
        "The strong price-value sentiment suggests that many buyers considered products acceptable for their cost, while the negative shares for "
        "battery life and build quality suggest persistent concerns around reliability and durability."
    )
    add_paragraph(
        doc,
        "These are product-review behavior insights, not demographic claims. The dataset does not include demographic variables and cannot support "
        "claims about age, gender, income, region, or other buyer characteristics. The valid inference is that the available public reviews emphasize "
        "functional product concerns and that aspect-level decomposition makes those concerns easier to identify."
    )

    doc.add_heading("Limitations", level=1)
    add_bullets(
        doc,
        [
            "The dataset is limited to public reviews from one product category on one e-commerce platform.",
            "Product selection favored items with visible review counts and higher review volume.",
            "The analysis reflects available reviewers, not all Jumia customers or all mobile accessories buyers.",
            "Reviewer demographics were unavailable, so demographic consumer behavior cannot be inferred.",
            "The LLM pipeline processed a 300-review stratified sample, not the full 4,964-review dataset.",
            "The rules pipeline provided broad coverage but used fewer standardized aspect categories.",
            "VADER may misread short, informal, localized, or context-dependent review language.",
            "Web scraping depends on Jumia page structure, which may change over time.",
            "LLM outputs can vary despite structured schemas and temperature set to 0.0.",
        ],
    )

    doc.add_heading("Conclusion", level=1)
    add_paragraph(
        doc,
        "This study developed and evaluated an aspect-based multi-agent framework for e-commerce consumer behavior analytics, using the Jumia "
        "Nigeria mobile phone accessories market as a case study. The verified dataset contained 4,964 unique reviews, 98 products, 6,582 "
        "aspect-level rows, and 59 unique aspects. The rules pipeline processed the full dataset, while the LLM pipeline processed a 300-review "
        "stratified sample for contextual analysis."
    )
    add_paragraph(
        doc,
        "The findings show that aspect-based analysis provides richer insight than star ratings or whole-review sentiment alone. Overall sentiment "
        "was positive, but battery life, build quality, and charging speed contained substantial negative or mixed feedback. VADER agreed with "
        "contextual sentiment on most non-mixed rows, yet contextual classification added value by representing mixed opinions and interpreting "
        "aspect evidence in context. For e-commerce vendors, the practical implication is clear: review analytics should monitor specific product "
        "attributes rather than only average ratings."
    )
    doc.add_heading("Recommendations", level=1)
    add_bullets(
        doc,
        [
            "Vendors should monitor aspect-level complaints, especially battery life, build quality, and charging speed.",
            "Marketplace dashboards should expose aspect-level summaries to help sellers and buyers interpret reviews more efficiently.",
            "Future work should expand the LLM run beyond the 300-review stratified sample and test sample stability across categories.",
            "Future studies should compare additional product categories and platforms to evaluate transferability beyond the Jumia Nigeria case study.",
            "Where ethically and legally permitted, future datasets could incorporate more metadata, but demographic claims should only be made when demographic data are actually available.",
        ],
    )

    doc.add_heading("References", level=1)
    refs = [
        "[1] T. Chen, P. Samaranayake, X. Cen, M. Qi, and Y.-C. Lan, \"The impact of online reviews on consumers' purchasing decisions: Evidence from an eye-tracking study,\" Frontiers in Psychology, vol. 13, Art. no. 865702, 2022, doi: 10.3389/fpsyg.2022.865702.",
        "[2] B. Pang and L. Lee, \"Opinion mining and sentiment analysis,\" Foundations and Trends in Information Retrieval, vol. 2, no. 1-2, pp. 1-135, 2008, doi: 10.1561/1500000011.",
        "[3] C. Hutto and E. Gilbert, \"VADER: A parsimonious rule-based model for sentiment analysis of social media text,\" Proc. Int. AAAI Conf. Web and Social Media, vol. 8, no. 1, pp. 216-225, 2014, doi: 10.1609/icwsm.v8i1.14550.",
        "[4] G. Brauwers and F. Frasincar, \"A survey on aspect-based sentiment classification,\" ACM Computing Surveys, vol. 55, no. 4, Art. no. 65, 2022, doi: 10.1145/3503044.",
        "[5] C. Zhou et al., \"A comprehensive evaluation of large language models on aspect-based sentiment analysis,\" arXiv:2412.02279, 2024. [Online]. Available: https://arxiv.org/abs/2412.02279",
        "[6] M. A. Brown, A. Gruen, G. Maldoff, S. Messing, Z. Sanderson, and M. Zimmer, \"Web scraping for research: Legal, ethical, institutional, and scientific considerations,\" arXiv:2410.23432, 2024. [Online]. Available: https://arxiv.org/abs/2410.23432",
        "[7] J. Foerderer, \"Should we trust web-scraped data?\" arXiv:2308.02231, 2023. [Online]. Available: https://arxiv.org/abs/2308.02231",
        "[8] LangChain, \"LangGraph overview,\" 2026. [Online]. Available: https://docs.langchain.com/oss/python/langgraph/overview",
        "[9] Pydantic, \"Pydantic AI documentation,\" 2026. [Online]. Available: https://pydantic.dev/docs/ai/overview/",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)


    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))
    df = load_data()
    figs = make_figures(df)
    build_doc(df, figs)
    print(OUT)


if __name__ == "__main__":
    main()
