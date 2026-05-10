# ===============================================================================

import html
import re

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="News Analytics & Intelligence Platform",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.main { background-color: #f4f6f9; }

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100% !important;
}

header[data-testid="stHeader"] { background: transparent; }

.dashboard-title {
    font-size: 26px;
    font-weight: 800;
    color: #00BFFF;
    margin-bottom: 2px;
    line-height: 1.3;
}

.dashboard-subtitle {
    font-size: 15px;
    color: #2563eb;
    margin-bottom: 25px;
    font-weight: 600;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 0px;
    border-left: 5px solid #00BFFF;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.kpi-label {
    font-size: 13px;
    color: #374151;
    font-weight: 700;
    margin-bottom: 6px;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #00BFFF;
}

.section-box {
    background: white;
    padding: 18px;
    border-radius: 0px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    margin-top: 18px;
    border: 1px solid #dbeafe;
}

.article-card {
    background:white;
    border:1px solid #dbeafe;
    padding:18px;
    margin-bottom:16px;
    border-left:6px solid #00BFFF;
}

.article-headline {
    font-size:21px;
    font-weight:800;
    color:#111827;
    margin-bottom:8px;
    line-height:1.5;
}

.article-meta {
    color:#6b7280;
    font-size:13px;
    margin-bottom:10px;
    font-weight:600;
}

.keyword-line {
    color:#00BFFF;
    font-weight:800;
    margin-bottom:8px;
}

.highlight {
    color:#005B96;
    background-color:#E0F7FF;
    font-weight:900;
    padding:1px 3px;
}

h1, h2, h3 {
    color: #00BFFF !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 0px;
    overflow: hidden;
    border: 1px solid #dbeafe;
}

[data-testid="stDownloadButton"] > button {
    border-radius: 0px !important;
    font-weight: 600;
    background-color: #00BFFF !important;
    color: #ffffff !important;
    border: none !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background-color: #009ACD !important;
    color: #ffffff !important;
}

.stTextInput input,
.stSelectbox div {
    border-radius: 0px !important;
}

hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE CONFIG
# =========================================================
# DB_CONFIG = {
#     "host": "localhost",
#     "port": 5433,
#     "user": "postgres",
#     "password": "abc123",
#     "dbname": "O_C_News_Monitor"
# }


DB_CONFIG = {
    "host": "ep-royal-feather-ao09dcs5-pooler.c-2.ap-southeast-1.aws.neon.tech",
    "port": 5432,
    "user": "neondb_owner",
    "password": "npg_PFVL9sMGN1DX",
    "dbname": "neondb",
    "sslmode": "require"
}



# =========================================================
# FUNCTIONS
# =========================================================
@st.cache_data(ttl=60)
def load_data(query):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df


def safe_text(value):
    if pd.isna(value):
        return ""
    return html.escape(str(value))


def split_keywords(value):
    if pd.isna(value):
        return []
    return [k.strip() for k in str(value).split(",") if k.strip()]


def highlight_keywords(text, keywords):
    text = safe_text(text)
    kws = split_keywords(keywords)

    for kw in sorted(kws, key=len, reverse=True):
        escaped_kw = html.escape(kw)
        pattern = re.escape(escaped_kw)
        text = re.sub(
            pattern,
            f'<span class="highlight">{escaped_kw}</span>',
            text
        )

    return text


def make_chart(df, x, y, title, x_title, y_title):
    fig = px.bar(df, x=x, y=y, text=y, title=title)
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_size=18,
        xaxis_title=x_title,
        yaxis_title=y_title
    )
    return fig

# =========================================================
# LOAD DATA
# =========================================================
try:
    scraping_df = load_data("SELECT * FROM vw_scraping_summary;")
    daily_keyword_df = load_data("SELECT * FROM vw_daily_summary;")
    matched_df = load_data("SELECT * FROM vw_matched_articles;")
except Exception as e:
    st.error(f"Database loading failed: {e}")
    st.stop()

# =========================================================
# SAFETY CHECKS
# =========================================================
if scraping_df.empty:
    st.warning("No scraping session data found.")
    st.stop()

if matched_df.empty:
    st.warning("No matched article data found. Run keyword matching first.")
    st.stop()

if "content" not in matched_df.columns:
    st.error("The view vw_matched_articles does not include content column. Please recreate the SQL view with a.content.")
    st.stop()

# =========================================================
# DAILY SCRAPING SUMMARY
# =========================================================
daily_scraping_df = scraping_df.copy()
daily_scraping_df["scraping_date"] = pd.to_datetime(
    daily_scraping_df["start_time"],
    errors="coerce"
).dt.date

daily_scraping_df = (
    daily_scraping_df
    .groupby("scraping_date", as_index=False)
    .agg(
        total_sessions=("session_id", "count"),
        total_scraped=("total_saved", "sum"),
        total_processed=("total_processed", "sum"),
        latest_status=("status", "last"),
        latest_stop_reason=("stop_reason", "last")
    )
    .sort_values("scraping_date", ascending=False)
)

daily_scraping_df["skipped_or_failed"] = (
    daily_scraping_df["total_processed"] - daily_scraping_df["total_scraped"]
)

daily_scraping_df["success_rate"] = (
    daily_scraping_df["total_scraped"] / daily_scraping_df["total_processed"] * 100
).round(2)

# =========================================================
# KPI VALUES
# =========================================================
latest_date = daily_scraping_df["scraping_date"].max()
latest_scraped = int(
    daily_scraping_df.loc[
        daily_scraping_df["scraping_date"] == latest_date,
        "total_scraped"
    ].sum()
)

total_scraped = int(scraping_df["total_saved"].sum())
total_processed = int(scraping_df["total_processed"].sum())
total_skipped = total_processed - total_scraped
success_rate = round((total_scraped / total_processed * 100), 2) if total_processed else 0

matched_articles = matched_df["article_id"].nunique()
keyword_hits = int(matched_df["matched_keyword_count"].sum())

# =========================================================
# TITLE
# =========================================================
st.markdown(
    '<div class="dashboard-title">News Analytics &amp; Intelligence Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dashboard-subtitle">Scraping Performance Monitoring &amp; Keyword Intelligence System</div>',
    unsafe_allow_html=True
)

# =========================================================
# KPI SECTION
# =========================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)

kpis = [
    ("Latest Date Scraped", latest_scraped),
    ("Total Scraped", total_scraped),
    ("Total Processed", total_processed),
    ("Skipped / Failed", total_skipped),
    ("Success Rate", f"{success_rate}%"),
    ("Keyword Hits", keyword_hits),
]

for col, (label, value) in zip([c1, c2, c3, c4, c5, c6], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =========================================================
# MODULE 1
# =========================================================
st.header("1️⃣ Scraping Performance Monitor")

left1, right1 = st.columns([1.2, 1])

with left1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    fig_scrape = make_chart(
        daily_scraping_df.sort_values("scraping_date"),
        "scraping_date",
        "total_scraped",
        "Date-wise Scraped Articles",
        "Date",
        "Articles"
    )
    st.plotly_chart(fig_scrape, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Daily Scraping Summary")
    st.dataframe(daily_scraping_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Session-wise Scraping Details")
st.dataframe(scraping_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =========================================================
# MODULE 2
# =========================================================
st.header("2️⃣ Keyword-Matched Article Tracker")

left2, right2 = st.columns([1.2, 1])

with left2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    fig_match = make_chart(
        daily_keyword_df,
        "published_date",
        "matched_articles",
        "Date-wise Matched Articles",
        "Published Date",
        "Matched Articles"
    )
    st.plotly_chart(fig_match, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    fig_hits = make_chart(
        daily_keyword_df,
        "published_date",
        "total_keyword_hits",
        "Date-wise Keyword Hits",
        "Published Date",
        "Keyword Hits"
    )
    st.plotly_chart(fig_hits, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# KEYWORD SUMMARY
# =========================================================
keyword_rows = []

for _, row in matched_df.iterrows():
    article_id = row.get("article_id")
    for kw in split_keywords(row.get("matched_keywords", "")):
        keyword_rows.append({"keyword": kw, "article_id": article_id})

keyword_summary_df = pd.DataFrame(keyword_rows)

if not keyword_summary_df.empty:
    keyword_summary_df = (
        keyword_summary_df
        .groupby("keyword", as_index=False)
        .agg(
            hit_count=("keyword", "count"),
            article_count=("article_id", "nunique")
        )
        .sort_values("hit_count", ascending=False)
    )

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Keyword-wise Summary")

    kleft, kright = st.columns([1.2, 1])

    with kleft:
        fig_kw = px.bar(
            keyword_summary_df.head(20),
            x="keyword",
            y="hit_count",
            text="hit_count",
            title="Top Keywords by Hit Count"
        )
        fig_kw.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Keyword",
            yaxis_title="Hit Count"
        )
        st.plotly_chart(fig_kw, use_container_width=True)

    with kright:
        st.dataframe(keyword_summary_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SEARCH + FILTER + ARTICLE CARDS
# =========================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Matched Articles")

all_keywords = sorted(keyword_summary_df["keyword"].unique().tolist()) if not keyword_summary_df.empty else []

f1, f2 = st.columns([1, 1])

with f1:
    search_text = st.text_input("Search headline, keyword, or full article content")

with f2:
    selected_keyword = st.selectbox(
        "Filter by matched keyword",
        ["All"] + all_keywords
    )

filtered_df = matched_df.copy()

if selected_keyword != "All":
    filtered_df = filtered_df[
        filtered_df["matched_keywords"].astype(str).str.contains(
            re.escape(selected_keyword),
            case=False,
            na=False,
            regex=True
        )
    ]

if search_text:
    search_text = search_text.strip()
    filtered_df = filtered_df[
        filtered_df["headline"].astype(str).str.contains(search_text, case=False, na=False)
        |
        filtered_df["matched_keywords"].astype(str).str.contains(search_text, case=False, na=False)
        |
        filtered_df["content"].astype(str).str.contains(search_text, case=False, na=False)
    ]

st.caption(f"Showing {len(filtered_df)} matched articles")

# limit visible cards for performance
MAX_VISIBLE_CARDS = 50
visible_df = filtered_df.head(MAX_VISIBLE_CARDS)

for _, row in visible_df.iterrows():
    headline = row.get("headline", "")
    content = row.get("content", "")
    keywords = row.get("matched_keywords", "")
    link = row.get("link", "")
    newspaper = row.get("newspaper", "")
    published_date = row.get("published_date", "")
    keyword_count = row.get("matched_keyword_count", "")

    highlighted_headline = highlight_keywords(headline, keywords)
    highlighted_content = highlight_keywords(content, keywords)

    st.markdown(f"""
    <div class="article-card">
        <div class="article-headline">{highlighted_headline}</div>
        <div class="article-meta">
            {safe_text(newspaper)} | {safe_text(published_date)} | Matched Keyword Count: {safe_text(keyword_count)}
        </div>
        <div class="keyword-line">
            Matched Keywords: {safe_text(keywords)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Read Full Article"):
        st.markdown(
            f'<div style="line-height:1.8; text-align:justify;">{highlighted_content}</div>',
            unsafe_allow_html=True
        )
        if link:
            st.link_button("Open Original Article", link)

if len(filtered_df) > MAX_VISIBLE_CARDS:
    st.info(f"Only first {MAX_VISIBLE_CARDS} articles are shown for performance. Use search/filter to narrow results.")

csv = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download matched articles CSV",
    data=csv,
    file_name="matched_articles.csv",
    mime="text/csv"
)

st.markdown('</div>', unsafe_allow_html=True)