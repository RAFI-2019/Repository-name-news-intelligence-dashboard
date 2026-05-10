# import streamlit as st
# import pandas as pd
# import psycopg2
# import plotly.express as px

# st.set_page_config(
#     page_title="Bangla News Intelligence Dashboard",
#     layout="wide"
# )

# DB_CONFIG = {
#     "host": "localhost",
#     "port": 5433,
#     "user": "postgres",
#     "password": "abc123",
#     "dbname": "O_C_News_Monitor"
# }

# def load_data(query):
#     conn = psycopg2.connect(**DB_CONFIG)
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# st.title("Bangla News Intelligence Dashboard")

# # Load data
# scraping_df = load_data("SELECT * FROM vw_scraping_summary;")
# daily_df = load_data("SELECT * FROM vw_daily_summary;")
# matched_df = load_data("SELECT * FROM vw_matched_articles;")

# # KPIs
# col1, col2, col3, col4 = st.columns(4)

# col1.metric("Total Scraped", int(scraping_df["total_saved"].sum()))
# col2.metric("Total Processed", int(scraping_df["total_processed"].sum()))
# col3.metric("Matched Articles", matched_df["article_id"].nunique())
# col4.metric("Keyword Hits", int(matched_df["matched_keyword_count"].sum()))

# st.divider()

# # Daily summary chart
# st.subheader("Date-wise Keyword Matching Summary")

# fig = px.bar(
#     daily_df,
#     x="published_date",
#     y="matched_articles",
#     title="Matched Articles by Date"
# )
# st.plotly_chart(fig, use_container_width=True)

# st.divider()

# # Scraping summary
# st.subheader("Scraping Performance Summary")
# st.dataframe(scraping_df, use_container_width=True)

# st.divider()

# # Matched articles
# st.subheader("Matched Articles")

# search_text = st.text_input("Search headline or keyword")

# filtered_df = matched_df.copy()

# if search_text:
#     search_text = search_text.strip()
#     filtered_df = filtered_df[
#         filtered_df["headline"].astype(str).str.contains(search_text, case=False, na=False) |
#         filtered_df["matched_keywords"].astype(str).str.contains(search_text, case=False, na=False)
#     ]

# st.dataframe(filtered_df, use_container_width=True)

# # Download
# csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
# st.download_button(
#     label="Download matched articles CSV",
#     data=csv,
#     file_name="matched_articles.csv",
#     mime="text/csv"
# )



# # =======================================================

# import streamlit as st
# import pandas as pd
# import psycopg2
# import plotly.express as px

# st.set_page_config(
#     page_title="News Analytics & Intelligence Platform",
#     layout="wide"
# )

# DB_CONFIG = {
#     "host": "localhost",
#     "port": 5433,
#     "user": "postgres",
#     "password": "abc123",
#     "dbname": "O_C_News_Monitor"
# }

# def load_data(query):
#     conn = psycopg2.connect(**DB_CONFIG)
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# st.title("📰 News Analytics & Intelligence Platform")
# st.caption("Scraping Performance Monitoring & Keyword Intelligence System")

# # Load data
# scraping_df = load_data("SELECT * FROM vw_scraping_summary;")
# daily_keyword_df = load_data("SELECT * FROM vw_daily_summary;")
# matched_df = load_data("SELECT * FROM vw_matched_articles;")

# # Date-wise scraping summary from session table
# daily_scraping_df = scraping_df.copy()
# daily_scraping_df["scraping_date"] = pd.to_datetime(daily_scraping_df["start_time"]).dt.date

# daily_scraping_df = (
#     daily_scraping_df
#     .groupby("scraping_date", as_index=False)
#     .agg(
#         total_sessions=("session_id", "count"),
#         total_scraped=("total_saved", "sum"),
#         total_processed=("total_processed", "sum"),
#         latest_status=("status", "last"),
#         latest_stop_reason=("stop_reason", "last")
#     )
#     .sort_values("scraping_date", ascending=False)
# )

# latest_date = daily_scraping_df["scraping_date"].max()
# latest_scraped = int(daily_scraping_df.loc[daily_scraping_df["scraping_date"] == latest_date, "total_scraped"].sum())

# # KPIs
# col1, col2, col3, col4, col5 = st.columns(5)

# col1.metric("Latest Date Scraped", latest_scraped)
# col2.metric("Total Scraped", int(scraping_df["total_saved"].sum()))
# col3.metric("Total Processed", int(scraping_df["total_processed"].sum()))
# col4.metric("Matched Articles", matched_df["article_id"].nunique())
# col5.metric("Keyword Hits", int(matched_df["matched_keyword_count"].sum()))

# st.divider()

# # Scraping Performance Monitor
# st.header("1️⃣ Scraping Performance Monitor")

# c1, c2 = st.columns([1.2, 1])

# with c1:
#     st.subheader("Date-wise Scraped Articles")
#     fig_scrape = px.bar(
#         daily_scraping_df.sort_values("scraping_date"),
#         x="scraping_date",
#         y="total_scraped",
#         text="total_scraped",
#         title="Scraped Articles by Date"
#     )
#     st.plotly_chart(fig_scrape, use_container_width=True)

# with c2:
#     st.subheader("Date-wise Scraping Summary")
#     st.dataframe(daily_scraping_df, use_container_width=True, hide_index=True)

# st.subheader("Session-wise Scraping Details")
# st.dataframe(scraping_df, use_container_width=True, hide_index=True)

# st.divider()

# # Keyword-Matched Article Tracker
# st.header("2️⃣ Keyword-Matched Article Tracker")

# c3, c4 = st.columns([1.2, 1])

# with c3:
#     st.subheader("Date-wise Matched Articles")
#     fig_keyword = px.bar(
#         daily_keyword_df,
#         x="published_date",
#         y="matched_articles",
#         text="matched_articles",
#         title="Matched Articles by Published Date"
#     )
#     st.plotly_chart(fig_keyword, use_container_width=True)

# with c4:
#     st.subheader("Date-wise Keyword Hits")
#     fig_hits = px.bar(
#         daily_keyword_df,
#         x="published_date",
#         y="total_keyword_hits",
#         text="total_keyword_hits",
#         title="Keyword Hits by Published Date"
#     )
#     st.plotly_chart(fig_hits, use_container_width=True)

# st.subheader("Matched Articles")

# search_text = st.text_input("Search by headline or keyword")

# filtered_df = matched_df.copy()

# if search_text:
#     search_text = search_text.strip()
#     filtered_df = filtered_df[
#         filtered_df["headline"].astype(str).str.contains(search_text, case=False, na=False) |
#         filtered_df["matched_keywords"].astype(str).str.contains(search_text, case=False, na=False)
#     ]

# st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
# st.download_button(
#     label="⬇️ Download matched articles CSV",
#     data=csv,
#     file_name="matched_articles.csv",
#     mime="text/csv"
# )


# ===============================================================================

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
# CUSTOM CSS - BORDER RADIUS 0 / SHARP STYLE
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #f4f6f9;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
}

# .dashboard-title {
#     font-size: 38px;
#     font-weight: 800;
#     color: #1f2937;
#     margin-bottom: 2px;
#     letter-spacing: -0.5px;
# }

# .dashboard-title {
#     font-size: 30px;
#     font-weight: 800;
#     color: #1f2937;
#     margin-bottom: 2px;
#     letter-spacing: -0.7px;
#     white-space: normal;
#     line-height: 1.2;
# }
            
# With this:
.dashboard-title {
    font-size: 26px;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 2px;
    letter-spacing: -0.5px;
    white-space: normal;
    line-height: 1.3;
    word-break: break-word;
    overflow-wrap: break-word;
    display: block;
    width: 100%;
}
                        
.dashboard-subtitle {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 25px;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 0px;
    border-left: 5px solid #2563eb;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.kpi-label {
    font-size: 13px;
    color: #6b7280;
    font-weight: 600;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
}

.section-box {
    background: white;
    padding: 18px;
    border-radius: 0px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    margin-top: 18px;
    border: 1px solid #e5e7eb;
}

h1, h2, h3 {
    # color: #111827;
    color: #154c79;
}

[data-testid="stDataFrame"] {
    border-radius: 0px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}

.stDownloadButton button {
    border-radius: 0px !important;
    font-weight: 600;
}

.stTextInput input {
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
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "abc123",
    "dbname": "O_C_News_Monitor"
}

# =========================================================
# LOAD DATA FUNCTION
# =========================================================
def load_data(query):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# =========================================================
# LOAD DATA
# =========================================================
scraping_df = load_data("SELECT * FROM vw_scraping_summary;")
daily_keyword_df = load_data("SELECT * FROM vw_daily_summary;")
matched_df = load_data("SELECT * FROM vw_matched_articles;")

# =========================================================
# DAILY SCRAPING SUMMARY
# =========================================================
daily_scraping_df = scraping_df.copy()

daily_scraping_df["scraping_date"] = pd.to_datetime(
    daily_scraping_df["start_time"]
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
matched_articles = matched_df["article_id"].nunique()
keyword_hits = int(matched_df["matched_keyword_count"].sum())

# =========================================================
# TITLE
# =========================================================
st.markdown(
    '<div class="dashboard-title">📰 News Analytics & Intelligence Platform</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">Scraping Performance Monitoring & Keyword Intelligence System</div>',
    unsafe_allow_html=True
)

# =========================================================
# KPI SECTION
# =========================================================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Latest Date Scraped</div>
        <div class="kpi-value">{latest_scraped}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Scraped</div>
        <div class="kpi-value">{total_scraped}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Processed</div>
        <div class="kpi-value">{total_processed}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Matched Articles</div>
        <div class="kpi-value">{matched_articles}</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Keyword Hits</div>
        <div class="kpi-value">{keyword_hits}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# MODULE 1: SCRAPING PERFORMANCE MONITOR
# =========================================================
st.header("1️⃣ Scraping Performance Monitor")

left1, right1 = st.columns([1.2, 1])

with left1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    fig_scrape = px.bar(
        daily_scraping_df.sort_values("scraping_date"),
        x="scraping_date",
        y="total_scraped",
        text="total_scraped",
        title="Date-wise Scraped Articles"
    )

    fig_scrape.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_size=18,
        xaxis_title="Date",
        yaxis_title="Articles"
    )

    st.plotly_chart(fig_scrape, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    st.subheader("Daily Scraping Summary")

    st.dataframe(
        daily_scraping_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-box">', unsafe_allow_html=True)

st.subheader("Session-wise Scraping Details")

st.dataframe(
    scraping_df,
    use_container_width=True,
    hide_index=True
)

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# =========================================================
# MODULE 2: KEYWORD-MATCHED ARTICLE TRACKER
# =========================================================
st.header("2️⃣ Keyword-Matched Article Tracker")

left2, right2 = st.columns([1.2, 1])

with left2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    fig_match = px.bar(
        daily_keyword_df,
        x="published_date",
        y="matched_articles",
        text="matched_articles",
        title="Date-wise Matched Articles"
    )

    fig_match.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_size=18,
        xaxis_title="Published Date",
        yaxis_title="Matched Articles"
    )

    st.plotly_chart(fig_match, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    fig_hits = px.bar(
        daily_keyword_df,
        x="published_date",
        y="total_keyword_hits",
        text="total_keyword_hits",
        title="Date-wise Keyword Hits"
    )

    fig_hits.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_size=18,
        xaxis_title="Published Date",
        yaxis_title="Keyword Hits"
    )

    st.plotly_chart(fig_hits, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SEARCH + MATCHED ARTICLES
# =========================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)

st.subheader("Matched Articles")

search_text = st.text_input("Search by headline or keyword")

filtered_df = matched_df.copy()

if search_text:
    search_text = search_text.strip()

    filtered_df = filtered_df[
        filtered_df["headline"].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )
        |
        filtered_df["matched_keywords"].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )
    ]

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

csv = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Download matched articles CSV",
    data=csv,
    file_name="matched_articles.csv",
    mime="text/csv"
)

st.markdown('</div>', unsafe_allow_html=True)