from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports/figures"
OUT = ROOT / "reports/COSC878_Journal_Article_Jumia_Aspect_Based_Analytics_TEMPLATE_FORMAT.docx"
AUTHOR = "Oluwapelumi Oyeyemi Oshundiya"
AFFILIATION = "COSC878 - Web and Social Media Analytics"
EMAIL = "oshundiya2255@pg.babcock.edu.ng"

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
    },
    name="rows",
)

ASPECT_SENTIMENT = [
    ("General product experience", "2,094"),
    ("Battery life", "1,409"),
    ("Product performance", "1,017"),
    ("Build quality", "782"),
    ("Charging speed", "590"),
    ("Price value", "352"),
    ("Portability", "234"),
    ("Delivery speed", "44"),
]


def set_font(run, size: float = 10, *, bold: bool | None = None, italic: bool | None = None) -> None:
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_paragraph_tnr(paragraph, size: float = 10, *, justify: bool = True) -> None:
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(6)
    if justify:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in paragraph.runs:
        set_font(run, size)


def set_columns(section, count: int) -> None:
    sect_pr = section._sectPr
    cols = sect_pr.xpath("./w:cols")
    if cols:
        cols = cols[0]
    else:
        cols = OxmlElement("w:cols")
        sect_pr.append(cols)
    cols.set(qn("w:num"), str(count))
    if count > 1:
        cols.set(qn("w:space"), "720")


def setup_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    set_columns(section, 1)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(6)


def add_title_block(doc: Document) -> None:
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(
        "An Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics: "
        "A Case Study of the Mobile Phone Accessories Market on Jumia Nigeria"
    )
    set_font(run, 24)
    title.paragraph_format.space_after = Pt(22)

    for label, value in [
        ("Name:", AUTHOR),
        ("Email(your school email):", EMAIL),
        ("Affiliation:", AFFILIATION),
    ]:
        p = doc.add_paragraph()
        r1 = p.add_run(label + " ")
        set_font(r1, 12)
        r2 = p.add_run(value)
        set_font(r2, 12)
        p.paragraph_format.space_after = Pt(10)


def begin_two_columns(doc: Document) -> None:
    section = doc.add_section(WD_SECTION.CONTINUOUS)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    set_columns(section, 2)


def add_abstract(doc: Document) -> None:
    p = doc.add_paragraph()
    label = p.add_run("Abstract—")
    set_font(label, 10, bold=True, italic=True)
    text = (
        "E-commerce platforms generate large quantities of consumer review data, but conventional analytics often reduce "
        "this evidence to star ratings or whole-review sentiment scores. This paper presents an aspect-based multi-agent "
        "framework for consumer behavior analytics using mobile phone accessories reviews from Jumia Nigeria as a case "
        "study. Public review data were scraped, deduplicated, and processed into aspect-level records. A deterministic "
        "rules pipeline processed the full dataset, while a three-agent LLM workflow was applied to a 300-review stratified "
        "sample. The verified dataset contains 4,964 unique reviews, 98 products, 6,582 aspect-level rows, and 59 unique "
        "aspects. Results show predominantly positive sentiment but reveal important negative and mixed feedback around "
        "battery life, build quality, and charging speed. VADER and contextual sentiment agreed on 90.0% of non-mixed rows. "
        "The study demonstrates that aspect-based analytics provides richer evidence for e-commerce decision-making than "
        "aggregate ratings alone."
    )
    body = p.add_run(text)
    set_font(body, 10, bold=True)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    p = doc.add_paragraph()
    label = p.add_run("Keywords—")
    set_font(label, 10, bold=True, italic=True)
    body = p.add_run(
        "aspect-based sentiment analysis, consumer behavior analytics, e-commerce reviews, multi-agent systems, Jumia Nigeria, large language models"
    )
    set_font(body, 10, bold=True, italic=True)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def h1(doc: Document, number: str, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(f"{number}. {text.upper()}")
    set_font(run, 10, bold=True)


def h2(doc: Document, letter: str, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r1 = p.add_run(f"{letter}. ")
    set_font(r1, 10, italic=True)
    r2 = p.add_run(text)
    set_font(r2, 10, bold=True, italic=True)


def para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    set_paragraph_tnr(p)


def bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.first_line_indent = Inches(-0.12)
    r = p.add_run("· ")
    set_font(r, 10)
    r = p.add_run(text)
    set_font(r, 10)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    set_font(r, 8)
    p.paragraph_format.space_after = Pt(8)


def make_template_figures() -> dict[str, Path]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    palette = {"positive": "#2E7D32", "negative": "#B42318", "neutral": "#6B7280", "mixed": "#C47F00"}

    paths: dict[str, Path] = {}
    fig, ax = plt.subplots(figsize=(3.2, 2.2), dpi=220)
    counts = SENTIMENT_COUNTS.reindex(["positive", "negative", "neutral", "mixed"])
    bars = ax.bar(counts.index, counts.values, color=[palette[k] for k in counts.index])
    ax.set_ylabel("Rows")
    ax.set_title("Contextual Sentiment")
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(bars, labels=[f"{int(v):,}" for v in counts.values], fontsize=6, padding=2)
    fig.tight_layout()
    paths["sentiment"] = FIGURES / "template_sentiment_distribution.png"
    fig.savefig(paths["sentiment"], bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=220)
    aspect_counts = ASPECT_COUNTS.sort_values()
    bars = ax.barh(aspect_counts.index, aspect_counts.values, color="#2E74B5")
    ax.set_xlabel("Rows")
    ax.set_title("Aspect Mentions")
    ax.bar_label(bars, labels=[str(int(v)) for v in aspect_counts.values], fontsize=6, padding=2)
    fig.tight_layout()
    paths["aspects"] = FIGURES / "template_top_aspects.png"
    fig.savefig(paths["aspects"], bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.05, 1.25), dpi=220)
    ax.axis("off")
    dataset_rows = [
        ["Dataset signal"],
        ["Unique reviews: 4,964"],
        ["Unique products: 98"],
        ["Aspect-level rows: 6,582"],
        ["Unique aspects: 59"],
        ["Rules aspect rows: 6,207"],
        ["LLM sample: 300 reviews; 375 rows"],
    ]
    table = ax.table(cellText=dataset_rows, cellLoc="left", loc="center", colWidths=[1.0])
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1, 1.15)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_text_props(weight="bold")
    paths["dataset_table"] = FIGURES / "template_dataset_table.png"
    fig.savefig(paths["dataset_table"], bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.05, 1.55), dpi=220)
    ax.axis("off")
    aspect_rows = [["Aspect", "Rows"]] + [list(row) for row in ASPECT_SENTIMENT]
    table = ax.table(cellText=aspect_rows, cellLoc="left", loc="center", colWidths=[0.76, 0.24])
    table.auto_set_font_size(False)
    table.set_fontsize(6.9)
    table.scale(1, 1.12)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_text_props(weight="bold")
    paths["aspect_table"] = FIGURES / "template_aspect_table.png"
    fig.savefig(paths["aspect_table"], bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    return paths


def add_figure(doc: Document, path: Path, caption_text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(3.05))
    caption(doc, caption_text)


def add_table_figure(doc: Document, path: Path, title: str) -> None:
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(title)
    set_font(r, 8, bold=True)
    cap.paragraph_format.space_after = Pt(2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(3.0))
    p.paragraph_format.space_after = Pt(8)


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.first_child_found_in("w:tcW")
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")


def add_table(doc: Document, title: str, rows: list[list[str]], widths_dxa: list[int] | None = None) -> None:
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(title)
    set_font(r, 8, bold=True)
    table = doc.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    table.autofit = False
    for i, head in enumerate(rows[0]):
        cell = table.rows[0].cells[i]
        cell.text = head
    for row in rows[1:]:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if widths_dxa and idx < len(widths_dxa):
                set_cell_width(cell, widths_dxa[idx])
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    set_font(run, 6.7)
    doc.add_paragraph()


def add_references(doc: Document) -> None:
    h1(doc, "", "References")
    refs = [
        "[1] T. Chen, P. Samaranayake, X. Cen, M. Qi, and Y.-C. Lan, “The impact of online reviews on consumers’ purchasing decisions: Evidence from an eye-tracking study,” Frontiers in Psychology, vol. 13, 2022, doi: 10.3389/fpsyg.2022.865702.",
        "[2] B. Pang and L. Lee, “Opinion mining and sentiment analysis,” Foundations and Trends in Information Retrieval, vol. 2, no. 1–2, pp. 1–135, 2008, doi: 10.1561/1500000011.",
        "[3] C. Hutto and E. Gilbert, “VADER: A parsimonious rule-based model for sentiment analysis of social media text,” Proc. Int. AAAI Conf. Web and Social Media, vol. 8, no. 1, pp. 216–225, 2014, doi: 10.1609/icwsm.v8i1.14550.",
        "[4] G. Brauwers and F. Frasincar, “A survey on aspect-based sentiment classification,” ACM Computing Surveys, vol. 55, no. 4, Article 65, 2022, doi: 10.1145/3503044.",
        "[5] C. Zhou et al., “A comprehensive evaluation of large language models on aspect-based sentiment analysis,” arXiv:2412.02279, 2024.",
        "[6] M. A. Brown, A. Gruen, G. Maldoff, S. Messing, Z. Sanderson, and M. Zimmer, “Web scraping for research: Legal, ethical, institutional, and scientific considerations,” arXiv:2410.23432, 2024.",
        "[7] J. Foerderer, “Should we trust web-scraped data?” arXiv:2308.02231, 2023.",
        "[8] LangChain, “LangGraph overview,” 2026. [Online]. Available: https://docs.langchain.com/oss/python/langgraph/overview",
        "[9] Pydantic, “Pydantic AI documentation,” 2026. [Online]. Available: https://pydantic.dev/docs/ai/overview/",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Inches(0.18)
        p.paragraph_format.first_line_indent = Inches(-0.18)
        set_paragraph_tnr(p, 8, justify=False)


def build() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))
    figs = make_template_figures()
    doc = Document()
    doc.core_properties.author = AUTHOR
    doc.core_properties.title = "Aspect-Based Multi-Agent Framework for Consumer Behavior Analytics"
    setup_document(doc)
    add_title_block(doc)
    begin_two_columns(doc)
    add_abstract(doc)

    h1(doc, "I", "Introduction")
    para(doc, "Digital commerce increasingly depends on user-generated evidence. Product reviews, star ratings, review dates, and post-purchase comments give buyers social proof and give sellers operational signals about product quality, delivery experience, and value perception. In web and social media analytics, consumer-generated text is valuable because it connects behavioral traces with interpretive content.")
    para(doc, "This paper frames the problem broadly as e-commerce consumer behavior analytics and uses Jumia Nigeria’s mobile phone accessories category as the empirical case study. Jumia Nigeria is therefore treated as the case study site, not as the whole problem domain.")
    para(doc, "The proposed framework decomposes review text into product or service aspects and assigns contextual sentiment to each aspect. This shifts the analytical unit from whole reviews to aspect-level evidence.")

    h1(doc, "II", "Problem Statement")
    para(doc, "E-commerce platforms contain large volumes of unstructured consumer feedback, yet many analytical approaches rely on star ratings or whole-review polarity. These summaries are insufficient for understanding the specific product and service factors that shape consumer satisfaction. A high rating may hide durability complaints, while a low rating may still contain praise for price value or portability.")

    h1(doc, "III", "Research Objectives and Questions")
    h2(doc, "A", "Objectives")
    for item in [
        "Collect public e-commerce review data from Jumia Nigeria’s mobile phone accessories category.",
        "Preserve key review metadata including review text, star rating, date, product, source URL, and verification status where available.",
        "Design a multi-agent aspect-based sentiment pipeline using typed outputs and graph-based orchestration.",
        "Compare contextual aspect sentiment with a VADER baseline.",
        "Visualize consumer behavior patterns across products, aspects, sentiment labels, star ratings, and dates.",
    ]:
        bullet(doc, item)
    h2(doc, "B", "Research Questions")
    para(doc, "The study asks which aspects are most frequently discussed, how aspect-level sentiment differs from star-rating interpretation, which aspects attract the strongest positive or negative sentiment, how contextual classification compares with VADER, and what practical insights vendors can extract from aspect-based review analytics.")

    h1(doc, "IV", "Literature Review")
    para(doc, "Online reviews are a major source of consumer information because they provide experiential evidence from prior buyers rather than seller-controlled descriptions. Chen et al. [1] show that online reviews influence purchasing decisions and that negative comments can receive substantial consumer attention.")
    para(doc, "Opinion mining research treats online reviews and blogs as opinion-rich resources that require computational methods for summarization, extraction, and decision support [2]. VADER is a widely used rule-based model for short and informal text [3], but it does not directly represent mixed sentiment and can miss context-dependent aspect meaning.")
    para(doc, "Aspect-based sentiment analysis identifies specific attributes discussed in text and assigns sentiment to each attribute. Brauwers and Frasincar [4] describe aspect-based sentiment classification as a fine-grained method for extracting sentiment information from sentences or documents. Recent work has also evaluated large language models for ABSA tasks [5], motivating this study’s use of an LLM sample for contextual analysis.")

    h1(doc, "V", "Methodology")
    h2(doc, "A", "Research Design and Data Source")
    para(doc, "The study used a computational case-study design. The empirical site was Jumia Nigeria’s public mobile accessories pages. The scraper collected product name, product URL, SKU where available, review title, review body, star rating, review date, reviewer name, verified purchase flag where available, source URL, and scrape timestamp.")
    h2(doc, "B", "Data Collection and Ethics")
    para(doc, "Data collection used Python requests for HTTP retrieval and BeautifulSoup for HTML parsing. Timestamped raw CSV and JSON files were retained and merged into a deduplicated master dataset using deterministic review identifiers. The scraper used limited page counts, retries, randomized delays, and a research-identifying user agent. Only publicly visible review data were collected.")
    h2(doc, "C", "Multi-Agent Pipeline")
    para(doc, "The LLM workflow consisted of three agents coordinated through LangGraph: a cleaner/router, an aspect extractor, and a contextual classifier. Pydantic schemas constrained outputs into typed objects. The deterministic rules pipeline processed the full dataset, while the LLM pipeline processed a 300-review stratified sample covering 61 products.")

    h1(doc, "VI", "System Architecture and Implementation")
    para(doc, "The architecture follows a source-to-insight pipeline: public category pages, product discovery, review scraping, raw batches, a deduplicated master dataset, aspect-level processing, VADER comparison, Streamlit dashboarding, and Docker-based deployment. The final processed dataset is aspect-level rather than review-level, allowing one review to produce multiple aspect records.")
    doc.add_page_break()
    add_table_figure(doc, figs["dataset_table"], "TABLE I. Dataset and Pipeline Coverage")

    h1(doc, "VII", "Results and Discussion")
    add_figure(doc, figs["sentiment"], "Fig. 1. Overall contextual sentiment distribution.")
    para(doc, "Across all merged aspect rows, sentiment was predominantly positive: 4,546 positive, 1,249 negative, 601 neutral, and 186 mixed rows. The positive majority indicates that many consumers expressed satisfaction, but negative and mixed rows show that meaningful dissatisfaction remained visible once reviews were decomposed into aspects.")
    add_figure(doc, figs["aspects"], "Fig. 2. Most frequently mentioned aspects.")
    para(doc, "General product experience was the most frequent category because many reviews were short comments. Among specific aspects, battery life, product performance, build quality, and charging speed dominated, reflecting the functional nature of mobile accessories.")
    add_table_figure(doc, figs["aspect_table"], "TABLE II. Top Aspect Mentions")
    para(doc, "Price value had the strongest positive profile among major aspects, with 88.1% positive sentiment. Battery life, build quality, and charging speed combined high mention frequency with notable negative sentiment. These patterns suggest that vendors should not interpret positive overall sentiment as evidence that all product attributes are performing well.")
    para(doc, "VADER and contextual sentiment agreed on 5,758 of 6,396 non-mixed rows, an agreement rate of 90.0%. However, VADER cannot represent mixed sentiment and sometimes misreads phrases where positive lexical cues appear inside complaints. The analysis also found 239 negative or mixed aspect rows inside 191 high-rated reviews, confirming that star ratings are too coarse for consumer behavior analytics.")

    h1(doc, "VIII", "Limitations")
    para(doc, "The dataset is limited to public reviews from one category on one platform. Product selection favored items with visible review counts. Reviewer demographics were unavailable, so demographic consumer behavior cannot be inferred. The LLM pipeline processed a 300-review stratified sample, not the full 4,964-review dataset. Web scraping also depends on page structure, which may change.")

    h1(doc, "IX", "Conclusion")
    para(doc, "This study developed an aspect-based multi-agent framework for e-commerce consumer behavior analytics using Jumia Nigeria mobile accessories reviews as a case study. The verified dataset contained 4,964 unique reviews, 98 products, 6,582 aspect-level rows, and 59 unique aspects. The rules pipeline processed the full dataset, while the LLM pipeline processed a 300-review stratified sample for contextual analysis.")
    para(doc, "The findings show that aspect-based analysis provides richer insight than star ratings or whole-review sentiment alone. Overall sentiment was positive, but battery life, build quality, and charging speed contained substantial negative or mixed feedback. For vendors, review analytics should therefore monitor specific product attributes rather than only average ratings.")

    h1(doc, "X", "Recommendations")
    for item in [
        "Vendors should monitor aspect-level complaints, especially battery life, build quality, and charging speed.",
        "Marketplace dashboards should expose aspect-level summaries to help sellers and buyers interpret reviews more efficiently.",
        "Future work should expand the LLM run beyond the 300-review stratified sample and compare additional product categories and platforms.",
    ]:
        bullet(doc, item)

    add_references(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
