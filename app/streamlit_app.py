"""Streamlit dashboard for aspect-based Jumia review analytics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_DIR = Path("data/processed")
SENTIMENT_ORDER = ["positive", "neutral", "mixed", "negative"]
SENTIMENT_COLORS = {
    "positive": "#2f855a",
    "neutral": "#718096",
    "mixed": "#b7791f",
    "negative": "#c53030",
}


st.set_page_config(
    page_title="Jumia Mobile Accessories Sentiment",
    page_icon=None,
    layout="wide",
)


def main() -> None:
    apply_theme()
    dataset_options = discover_datasets(DATA_DIR)

    if not dataset_options:
        render_empty_state()
        return

    with st.sidebar:
        st.header("Dataset")
        selected_dataset = st.selectbox(
            "Processed file",
            options=list(dataset_options.keys()),
            index=preferred_dataset_index(dataset_options),
        )

    df = load_dataset(dataset_options[selected_dataset])
    filtered = render_filters(df, selected_dataset)

    st.title("Jumia Mobile Accessories Sentiment")
    st.caption("Aspect-level review analytics for the Jumia Nigeria mobile accessories market.")

    if filtered.empty:
        st.warning("No records match the selected filters.")
        return

    render_kpis(filtered)

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.subheader("Contextual Sentiment")
        st.plotly_chart(sentiment_distribution_chart(filtered), width="stretch")

    with right:
        st.subheader("Aspect Mentions")
        st.plotly_chart(aspect_frequency_chart(filtered), width="stretch")

    st.subheader("Aspect Sentiment Matrix")
    st.plotly_chart(aspect_sentiment_chart(filtered), width="stretch")

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("VADER vs Contextual")
        st.plotly_chart(vader_context_chart(filtered), width="stretch")

    with right:
        st.subheader("Star Rating vs Aspect Score")
        st.plotly_chart(rating_score_chart(filtered), width="stretch")

    trend = temporal_trend_chart(filtered)
    if trend is not None:
        st.subheader("Review Timeline")
        st.plotly_chart(trend, width="stretch")

    st.subheader("Review Evidence")
    st.dataframe(
        evidence_table(filtered),
        width="stretch",
        hide_index=True,
        height=420,
    )


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        [data-testid="stMetric"] {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            color: #1a202c;
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: #4a5568;
        }
        [data-testid="stMetricValue"] {
            color: #1a202c;
        }
        [data-testid="stDataFrame"] {
            color: #1a202c;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def discover_datasets(data_dir: Path) -> dict[str, Path]:
    datasets = []
    for path in sorted(data_dir.glob("*.csv"), key=dataset_sort_key):
        label = path.name
        if path.stem == "jumia_reviews_processed_latest":
            label = f"Production latest - {path.name}"
        elif "_llm" in path.stem:
            label = f"LLM - {path.name}"
        elif "_rules" in path.stem:
            label = f"Rules - {path.name}"
        datasets.append((label, path))
    return dict(datasets)


def dataset_sort_key(path: Path) -> tuple[int, str]:
    if path.stem == "jumia_reviews_processed_latest":
        return (0, path.name)
    if "_llm" in path.stem:
        return (1, path.name)
    if "_rules" in path.stem:
        return (2, path.name)
    return (3, path.name)


def preferred_dataset_index(dataset_options: dict[str, Path]) -> int:
    labels = list(dataset_options)
    for index, label in enumerate(labels):
        if label.startswith("Production latest"):
            return index
    for index, label in enumerate(labels):
        if label.startswith("LLM"):
            return index
    return 0


@st.cache_data(show_spinner=False)
def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["review_date_parsed"] = pd.to_datetime(
        df["review_date"],
        format="%d-%m-%Y",
        errors="coerce",
    )
    df["aspect_normalized"] = df["aspect"].map(normalize_aspect)
    df["aspect_category_normalized"] = df["aspect_category"].map(normalize_aspect_category)
    df["contextual_sentiment"] = df["contextual_sentiment"].str.lower()
    df["vader_label"] = df["vader_label"].str.lower()
    df["product_short_name"] = df["product_name"].map(shorten_product_name)
    return df


def render_filters(df: pd.DataFrame, selected_dataset: str) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filters")
        st.caption(selected_dataset)

        modes = sorted(df["pipeline_mode"].dropna().unique().tolist())
        products = sorted(df["product_short_name"].dropna().unique().tolist())
        aspects = sorted(df["aspect_normalized"].dropna().unique().tolist())
        sentiments = [value for value in SENTIMENT_ORDER if value in set(df["contextual_sentiment"])]

        selected_modes = st.multiselect("Pipeline", modes, default=modes)
        selected_products = st.multiselect("Products", products, default=products)
        selected_aspects = st.multiselect("Aspects", aspects, default=aspects)
        selected_sentiments = st.multiselect("Sentiment", sentiments, default=sentiments)

        min_rating = int(df["star_rating"].min()) if df["star_rating"].notna().any() else 1
        max_rating = int(df["star_rating"].max()) if df["star_rating"].notna().any() else 5
        selected_rating = st.slider(
            "Star rating",
            min_value=1,
            max_value=5,
            value=(min_rating, max_rating),
            step=1,
        )

        if df["review_date_parsed"].notna().any():
            min_date = df["review_date_parsed"].min().date()
            max_date = df["review_date_parsed"].max().date()
            selected_dates = st.date_input(
                "Review date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
        else:
            selected_dates = None

    filtered = df.copy()
    filtered = filtered[filtered["pipeline_mode"].isin(selected_modes)]
    filtered = filtered[filtered["product_short_name"].isin(selected_products)]
    filtered = filtered[filtered["aspect_normalized"].isin(selected_aspects)]
    filtered = filtered[filtered["contextual_sentiment"].isin(selected_sentiments)]
    filtered = filtered[
        filtered["star_rating"].between(selected_rating[0], selected_rating[1], inclusive="both")
    ]

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start, end = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
        filtered = filtered[
            filtered["review_date_parsed"].isna()
            | filtered["review_date_parsed"].between(start, end, inclusive="both")
        ]

    return filtered


def render_kpis(df: pd.DataFrame) -> None:
    unique_reviews = df["review_id"].nunique()
    unique_products = df["product_name"].nunique()
    unique_aspects = df["aspect_normalized"].nunique()
    avg_score = df["contextual_sentiment_score"].mean()
    avg_rating = df["star_rating"].mean()

    cols = st.columns(5)
    cols[0].metric("Reviews", f"{unique_reviews:,}")
    cols[1].metric("Products", f"{unique_products:,}")
    cols[2].metric("Aspect Rows", f"{len(df):,}")
    cols[3].metric("Aspects", f"{unique_aspects:,}")
    cols[4].metric("Avg Score", f"{avg_score:.2f}", f"{avg_rating:.1f} stars")


def sentiment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    counts = (
        df["contextual_sentiment"]
        .value_counts()
        .reindex(SENTIMENT_ORDER)
        .dropna()
        .reset_index()
    )
    counts.columns = ["sentiment", "count"]
    fig = px.bar(
        counts,
        x="sentiment",
        y="count",
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        text="count",
    )
    return polish_chart(fig, y_title="Aspect rows", x_title="")


def aspect_frequency_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["aspect_normalized"].value_counts().head(10).sort_values().reset_index()
    counts.columns = ["aspect", "count"]
    fig = px.bar(
        counts,
        x="count",
        y="aspect",
        orientation="h",
        text="count",
        color_discrete_sequence=["#2b6cb0"],
    )
    return polish_chart(fig, x_title="Mentions", y_title="")


def aspect_sentiment_chart(df: pd.DataFrame) -> go.Figure:
    matrix = (
        df.groupby(["aspect_normalized", "contextual_sentiment"])
        .size()
        .reset_index(name="count")
    )
    top_aspects = df["aspect_normalized"].value_counts().head(12).index.tolist()
    matrix = matrix[matrix["aspect_normalized"].isin(top_aspects)]
    fig = px.bar(
        matrix,
        x="aspect_normalized",
        y="count",
        color="contextual_sentiment",
        category_orders={"contextual_sentiment": SENTIMENT_ORDER},
        color_discrete_map=SENTIMENT_COLORS,
    )
    fig.update_layout(barmode="stack")
    return polish_chart(fig, x_title="", y_title="Aspect rows")


def vader_context_chart(df: pd.DataFrame) -> go.Figure:
    comparison = (
        df.groupby(["vader_label", "contextual_sentiment"])
        .size()
        .reset_index(name="count")
    )
    fig = px.bar(
        comparison,
        x="vader_label",
        y="count",
        color="contextual_sentiment",
        category_orders={
            "vader_label": SENTIMENT_ORDER,
            "contextual_sentiment": SENTIMENT_ORDER,
        },
        color_discrete_map=SENTIMENT_COLORS,
    )
    fig.update_layout(barmode="group")
    return polish_chart(fig, x_title="VADER baseline", y_title="Aspect rows")


def rating_score_chart(df: pd.DataFrame) -> go.Figure:
    plot_df = df.dropna(subset=["star_rating", "contextual_sentiment_score"])
    fig = px.strip(
        plot_df,
        x="star_rating",
        y="contextual_sentiment_score",
        color="contextual_sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        hover_data=["aspect_normalized", "review_title", "reviewer_name"],
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#718096")
    return polish_chart(fig, x_title="Star rating", y_title="Contextual score")


def temporal_trend_chart(df: pd.DataFrame) -> go.Figure | None:
    trend_df = df.dropna(subset=["review_date_parsed"])
    if trend_df.empty:
        return None

    trend = (
        trend_df.groupby(["review_date_parsed", "contextual_sentiment"])
        .size()
        .reset_index(name="count")
    )
    fig = px.line(
        trend,
        x="review_date_parsed",
        y="count",
        color="contextual_sentiment",
        markers=True,
        category_orders={"contextual_sentiment": SENTIMENT_ORDER},
        color_discrete_map=SENTIMENT_COLORS,
    )
    return polish_chart(fig, x_title="", y_title="Aspect rows")


def evidence_table(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "review_date",
        "star_rating",
        "aspect_normalized",
        "contextual_sentiment",
        "vader_label",
        "aspect_evidence",
        "contextual_rationale",
        "review_text",
        "reviewer_name",
    ]
    table = df[columns].copy()
    table.columns = [
        "Date",
        "Stars",
        "Aspect",
        "Contextual",
        "VADER",
        "Evidence",
        "Rationale",
        "Review",
        "Reviewer",
    ]
    return table.sort_values(["Date", "Aspect"], ascending=[False, True])


def polish_chart(fig: go.Figure, *, x_title: str, y_title: str) -> go.Figure:
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text="",
        xaxis_title=x_title,
        yaxis_title=y_title,
        font=dict(size=13, color="#2d3748"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hoverlabel=dict(bgcolor="#ffffff", font_color="#1a202c"),
        xaxis=dict(color="#2d3748", gridcolor="#edf2f7", zerolinecolor="#cbd5e0"),
        yaxis=dict(color="#2d3748", gridcolor="#edf2f7", zerolinecolor="#cbd5e0"),
    )
    for trace in fig.data:
        if trace.type == "bar":
            trace.update(textposition="outside", marker_line_width=0, cliponaxis=False)
        elif trace.type == "scatter":
            trace.update(marker_line_width=0, cliponaxis=False)
    return fig


def normalize_aspect(value: object) -> str:
    text = clean_label(value)
    replacements = {
        "Battery quality": "Battery life",
        "Product performance": "Product performance",
        "General": "General product experience",
    }
    return replacements.get(text, text)


def normalize_aspect_category(value: object) -> str:
    text = clean_label(value)
    replacements = {
        "General": "General product experience",
        "Product performance": "General product experience",
    }
    return replacements.get(text, text)


def clean_label(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip().replace("_", " ")
    if not text:
        return "Unknown"
    return " ".join(word.capitalize() for word in text.split())


def shorten_product_name(value: object, max_length: int = 72) -> str:
    text = str(value)
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3].rstrip()}..."


def render_empty_state() -> None:
    st.title("Jumia Mobile Accessories Sentiment")
    st.warning("No processed CSV files were found in data/processed.")


if __name__ == "__main__":
    main()
