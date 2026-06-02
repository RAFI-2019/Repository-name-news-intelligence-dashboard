import html
import re
from io import BytesIO
from datetime import timedelta

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st


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
    padding-top: 2rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100% !important;
}

header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
}

section[data-testid="stSidebar"] > div {
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
}

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
    margin-bottom: 18px;
    font-weight: 600;
}

.view-note {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-left: 5px solid #00BFFF;
    padding: 12px 16px;
    margin-bottom: 16px;
    color: #374151;
    font-weight: 600;
}

.date-range-box {
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-left: 5px solid #00BFFF;
    padding: 14px 18px;
    margin-bottom: 16px;
}

.kpi-card {
    background: white;
    padding: 18px;
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
    font-size: 28px;
    font-weight: 800;
    color: #00BFFF;
}

.section-box {
    background: white;
    padding: 18px;
    border-radius: 0px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    margin-top: 16px;
    border: 1px solid #dbeafe;
}

.dark-section-box {
    background: #000000;
    padding: 18px;
    border-radius: 0px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    margin-top: 16px;
    border: 1px solid #333333;
}

.article-card {
    background: white;
    border: 1px solid #dbeafe;
    padding: 18px;
    margin-bottom: 12px;
    border-left: 6px solid #00BFFF;
}

.article-headline {
    font-size: 21px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 8px;
    line-height: 1.5;
}

.article-meta {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 10px;
    font-weight: 600;
}

.keyword-line {
    color: #00BFFF;
    font-weight: 800;
    margin-bottom: 8px;
}

.highlight {
    color: #005B96;
    background-color: #E0F7FF;
    font-weight: 900;
    padding: 1px 3px;
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
.stSelectbox div,
.stRadio div {
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
def get_db_config():
    try:
        return {
            "host": st.secrets["database"]["host"],
            "port": int(st.secrets["database"]["port"]),
            "user": st.secrets["database"]["user"],
            "password": st.secrets["database"]["password"],
            "dbname": st.secrets["database"]["dbname"],
            "sslmode": st.secrets["database"].get("sslmode", "require")
        }
    except Exception:
        return {
            "host": "localhost",
            "port": 5433,
            "user": "postgres",
            "password": "abc123",
            "dbname": "O_C_News_Monitor"
        }


DB_CONFIG = get_db_config()


# =========================================================
# HELPER FUNCTIONS
# =========================================================
@st.cache_data(ttl=300)
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


def keyword_hits_html(keywords, content):
    """Show each matched keyword with its hit count, sorted by count descending."""
    kw_list = split_keywords(keywords)
    counts = {kw: str(content).count(kw) for kw in kw_list}
    sorted_kws = sorted(counts.items(), key=lambda x: -x[1])
    parts = []
    for kw, cnt in sorted_kws:
        parts.append(
            f'<span class="highlight">{html.escape(kw)}</span>'
            f'<span style="color:#6b7280;font-size:11px;"> &times;{cnt}</span>'
        )
    return " &nbsp; ".join(parts)


def fmt_duration(seconds):
    """Format seconds into human readable duration."""
    s = int(seconds or 0)
    if s >= 3600:
        return f"{s//3600}h {(s%3600)//60}m {s%60}s"
    return f"{s//60}m {s%60}s"


def render_kpi_cards(kpis, columns_count):
    cols = st.columns(columns_count)
    for col, (label, value) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{safe_text(label)}</div>
                <div class="kpi-value">{safe_text(value)}</div>
            </div>
            """, unsafe_allow_html=True)


def build_keyword_summary(filtered_df):
    """Build keyword hit summary from a (pre-filtered) matched_df."""
    keyword_rows = []
    for _, row in filtered_df.iterrows():
        article_id = row.get("article_id")
        for kw in split_keywords(row.get("matched_keywords", "")):
            keyword_rows.append({"keyword": kw, "article_id": article_id})

    if not keyword_rows:
        return pd.DataFrame(columns=["keyword", "hit_count", "article_count"])

    kdf = pd.DataFrame(keyword_rows)
    kdf = (
        kdf.groupby("keyword", as_index=False)
        .agg(hit_count=("keyword", "count"), article_count=("article_id", "nunique"))
        .sort_values("hit_count", ascending=False)
    )
    return kdf


def make_dark_bar(df, x, y, title, x_title, y_title, horizontal=False):
    """Dark-themed bar chart. Set horizontal=True for Bangla x-axis labels."""
    if horizontal:
        fig = px.bar(df, x=y, y=x, text=y, title=title, orientation="h")
        xaxis_cfg = dict(title=dict(text=y_title, font=dict(color="#FFFFFF")),
                         tickfont=dict(color="#FFFFFF"), gridcolor="#333333", linecolor="#FFFFFF")
        yaxis_cfg = dict(title=dict(text=x_title, font=dict(color="#FFFFFF")),
                         tickfont=dict(color="#FFFFFF", size=13), gridcolor="#333333",
                         linecolor="#FFFFFF", autorange="reversed")
    else:
        fig = px.bar(df, x=x, y=y, text=y, title=title)
        xaxis_cfg = dict(title=dict(text=x_title, font=dict(color="#FFFFFF")),
                         tickfont=dict(color="#FFFFFF"), gridcolor="#333333", linecolor="#FFFFFF")
        yaxis_cfg = dict(title=dict(text=y_title, font=dict(color="#FFFFFF")),
                         tickfont=dict(color="#FFFFFF"), gridcolor="#333333", linecolor="#FFFFFF")

    fig.update_layout(
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        title_font=dict(size=16, color="#FFFFFF"),
        font=dict(color="#FFFFFF"),
        transition_duration=0,
        xaxis=xaxis_cfg,
        yaxis=yaxis_cfg,
        margin=dict(l=40, r=30, t=50, b=40)
    )
    fig.update_traces(
        marker_color="#00BFFF",
        textfont=dict(color="#FFFFFF", size=11),
        textposition="outside",
        cliponaxis=False
    )
    return fig


def safe_filename(value):
    """Create a safe filename fragment from the selected date label/filter label."""
    value = str(value or "export")
    value = value.replace("→", "to")
    value = re.sub(r"[^0-9A-Za-z_\-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "export"


def dataframe_to_excel_bytes(df):
    """Return an Excel file as bytes. Keeps export logic reusable and clean."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="articles")
    return buf.getvalue()


def prepare_export_df(df):
    """Remove internal helper columns before user download."""
    if df is None or df.empty:
        return pd.DataFrame()
    return df.drop(columns=[c for c in df.columns if str(c).startswith("__")], errors="ignore").copy()


# =========================================================
# DATE RANGE SELECTOR
# =========================================================
def render_date_range_selector(matched_df):
    """
    Single date range selector at top of User View.
    Returns (date_from, date_to, label_str).
    Default = Latest date in data.
    """
    all_dates = (
        pd.to_datetime(matched_df["published_date"], errors="coerce")
        .dt.date.dropna()
    )
    latest_date = all_dates.max()
    earliest_date = all_dates.min()

    st.markdown('<div class="date-range-box">', unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 3])

    with col_sel:
        range_option = st.selectbox(
            "Select date range",
            ["Latest date", "Last 7 days", "Last 14 days", "Last 30 days", "All time", "Custom range"],
            index=0,
            key="date_range_selector"
        )

    if range_option == "Latest date":
        date_from = latest_date
        date_to   = latest_date
        label     = str(latest_date)

    elif range_option == "Last 7 days":
        date_from = latest_date - timedelta(days=6)
        date_to   = latest_date
        label     = f"{date_from} → {date_to}"

    elif range_option == "Last 14 days":
        date_from = latest_date - timedelta(days=13)
        date_to   = latest_date
        label     = f"{date_from} → {date_to}"

    elif range_option == "Last 30 days":
        date_from = latest_date - timedelta(days=29)
        date_to   = latest_date
        label     = f"{date_from} → {date_to}"

    elif range_option == "All time":
        date_from = earliest_date
        date_to   = latest_date
        label     = f"{date_from} → {date_to} (all time)"

    else:  # Custom range
        c1, c2 = st.columns(2)
        with c1:
            date_from = st.date_input("From", value=latest_date - timedelta(days=6),
                                      min_value=earliest_date, max_value=latest_date,
                                      key="custom_from")
        with c2:
            date_to = st.date_input("To", value=latest_date,
                                    min_value=earliest_date, max_value=latest_date,
                                    key="custom_to")
        label = f"{date_from} → {date_to}"

    with col_info:
        st.markdown(
            f'<div style="padding-top:28px; color:#6b7280; font-size:13px;">'
            f'Showing data for: <strong style="color:#00BFFF;">{label}</strong></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
    return date_from, date_to, label


# =========================================================
# USER VIEW SECTIONS
# =========================================================
def render_keyword_wise_summary(keyword_summary_df, date_label):
    """Keyword chart — top 10 horizontal bars + full table."""
    st.markdown('<div class="dark-section-box">', unsafe_allow_html=True)
    st.subheader(f"Keyword-wise Summary — {date_label}")

    if keyword_summary_df.empty:
        st.info("No keyword data found for selected date range.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    kleft, kright = st.columns([1.2, 1])

    with kleft:
        top10 = keyword_summary_df.head(10)
        fig_kw = make_dark_bar(
            top10, "keyword", "hit_count",
            "Top 10 Keywords by Hit Count",
            "Keyword", "Hit Count",
            horizontal=True
        )
        st.plotly_chart(fig_kw, use_container_width=True)

    with kright:
        display_df = keyword_summary_df.rename(columns={
            "keyword": "Keyword",
            "hit_count": "Total Hits",
            "article_count": "Articles"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_matched_articles(filtered_df, keyword_summary_df, date_label):
    """Article list — keyword + text filters, pagination, inline selection, export."""
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader(f"Matched Articles — {date_label}")

    all_keywords = (
        sorted(keyword_summary_df["keyword"].unique().tolist())
        if not keyword_summary_df.empty else []
    )

    # ── Filters (no date filter here — handled at top level) ──
    f1, f2 = st.columns([1, 1])

    with f1:
        selected_keyword = st.selectbox(
            "Filter by matched keyword",
            ["All Keywords"] + all_keywords,
            key="kw_filter"
        )

    with f2:
        search_text = st.text_input(
            "Search headline or content",
            key="search_filter"
        )

    # ── Apply filters ──
    result_df = filtered_df.copy()

    if selected_keyword != "All Keywords":
        result_df = result_df[
            result_df["matched_keywords"].astype(str).str.contains(
                re.escape(selected_keyword), case=False, na=False, regex=True
            )
        ]

    if search_text.strip():
        q = search_text.strip()
        result_df = result_df[
            result_df["headline"].astype(str).str.contains(q, case=False, na=False, regex=False)
            | result_df["content"].astype(str).str.contains(q, case=False, na=False, regex=False)
            | result_df["matched_keywords"].astype(str).str.contains(q, case=False, na=False, regex=False)
        ]

    # Stable internal key for selection. article_id is preferred.
    # Fallback to row index only if article_id is missing/blank.
    if "article_id" in result_df.columns:
        result_df["__article_key"] = result_df["article_id"].astype(str)
        blank_key_mask = result_df["__article_key"].isin(["", "nan", "None", "NaT"])
        if blank_key_mask.any():
            result_df.loc[blank_key_mask, "__article_key"] = result_df.loc[blank_key_mask].index.astype(str)
    else:
        result_df["__article_key"] = result_df.index.astype(str)

    total = len(result_df)

    # ── Selection state ──
    if "selected_article_keys" not in st.session_state:
        st.session_state["selected_article_keys"] = set()

    if not isinstance(st.session_state["selected_article_keys"], set):
        st.session_state["selected_article_keys"] = set(st.session_state["selected_article_keys"])

    current_keys = set(result_df["__article_key"].astype(str).tolist())
    st.session_state["selected_article_keys"] = st.session_state["selected_article_keys"].intersection(current_keys)

    selected_count = len(st.session_state["selected_article_keys"])

    # ── Pagination ──
    PAGE_SIZE = 20
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceiling division

    pg_col, info_col, clear_col = st.columns([1, 3, 1])

    with pg_col:
        page = st.number_input("Page", min_value=1, max_value=total_pages,
                               value=1, step=1, key="page_num")

    with info_col:
        start = (page - 1) * PAGE_SIZE
        end   = min(start + PAGE_SIZE, total)
        st.caption(
            f"Showing {start + 1}–{end} of {total} matched articles | Selected: {selected_count}"
            if total > 0 else "No articles found for selected filters."
        )

    with clear_col:
        if selected_count > 0:
            if st.button("Clear selected", key="clear_selected_articles"):
                st.session_state["selected_article_keys"] = set()
                for k in list(st.session_state.keys()):
                    if str(k).startswith("article_tick_"):
                        st.session_state[k] = False
                st.rerun()

    visible_df = result_df.iloc[start:end]

    # ── Article cards with inline checkbox ──
    for _, row in visible_df.iterrows():
        article_key    = str(row.get("__article_key", ""))
        article_id     = row.get("article_id", "")
        headline       = row.get("headline", "")
        content        = row.get("content", "")
        keywords       = row.get("matched_keywords", "")
        link           = row.get("link", "")
        newspaper      = row.get("newspaper", "")
        published_date = row.get("published_date", "")
        keyword_count  = row.get("matched_keyword_count", "")

        highlighted_headline = highlight_keywords(headline, keywords)
        highlighted_content  = highlight_keywords(content, keywords)
        kw_display           = keyword_hits_html(keywords, str(content))

        checkbox_key = f"article_tick_{article_key}"

        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = article_key in st.session_state["selected_article_keys"]

        checked = st.checkbox(
            "Select this article",
            key=checkbox_key
        )

        if checked:
            st.session_state["selected_article_keys"].add(article_key)
        else:
            st.session_state["selected_article_keys"].discard(article_key)

        st.markdown(f"""
        <div class="article-card">
            <div class="article-headline">{highlighted_headline}</div>
            <div class="article-meta">
                {safe_text(newspaper)} &nbsp;|&nbsp;
                {safe_text(published_date)} &nbsp;|&nbsp;
                Keyword matches: {safe_text(keyword_count)}
            </div>
            <div class="keyword-line">
                Matched Keywords: {kw_display}
            </div>
        </div>
        """, unsafe_allow_html=True)

        short_title = str(headline)[:60] if headline else str(article_id)
        with st.expander(f"Read full article — {short_title}"):
            st.markdown(
                f'<div style="line-height:1.9; text-align:justify;">{highlighted_content}</div>',
                unsafe_allow_html=True
            )
            if link:
                st.markdown(f"[Open original article ↗]({link})")

    # ── Export ──
    if total > 0:
        st.markdown("#### Download Articles")

        selected_keys = st.session_state["selected_article_keys"].intersection(current_keys)
        selected_df = result_df[result_df["__article_key"].astype(str).isin(selected_keys)].copy()

        export_all_df = prepare_export_df(result_df)
        export_selected_df = prepare_export_df(selected_df)

        file_label = safe_filename(date_label)

        all_csv = export_all_df.to_csv(index=False).encode("utf-8-sig")
        all_xlsx = dataframe_to_excel_bytes(export_all_df)

        selected_csv = export_selected_df.to_csv(index=False).encode("utf-8-sig") if not export_selected_df.empty else b""
        selected_xlsx = dataframe_to_excel_bytes(export_selected_df) if not export_selected_df.empty else b""

        st.caption(
            f"All filtered articles: {len(export_all_df)} | "
            f"Selected articles: {len(export_selected_df)}"
        )

        d1, d2, d3, d4 = st.columns(4)

        with d1:
            st.download_button(
                label="⬇️ All CSV",
                data=all_csv,
                file_name=f"matched_articles_all_{file_label}.csv",
                mime="text/csv",
                key="dl_all_csv"
            )

        with d2:
            st.download_button(
                label="⬇️ All Excel",
                data=all_xlsx,
                file_name=f"matched_articles_all_{file_label}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_all_excel"
            )

        with d3:
            st.download_button(
                label="⬇️ Selected CSV",
                data=selected_csv,
                file_name=f"matched_articles_selected_{file_label}.csv",
                mime="text/csv",
                key="dl_selected_csv",
                disabled=export_selected_df.empty
            )

        with d4:
            st.download_button(
                label="⬇️ Selected Excel",
                data=selected_xlsx,
                file_name=f"matched_articles_selected_{file_label}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_selected_excel",
                disabled=export_selected_df.empty
            )

    st.markdown('</div>', unsafe_allow_html=True)


def render_keyword_tracker_kpis(filtered_df, keyword_summary_df, date_label):
    """KPI summary cards — all scoped to selected date range."""
    st.header("Keyword-Matched Article Tracker")

    total_matched  = filtered_df["article_id"].nunique()
    total_hits     = int(filtered_df["matched_keyword_count"].fillna(0).sum())
    unique_kws     = keyword_summary_df["keyword"].nunique()

    field_kpis = [
        ("Matched Articles", total_matched),
        ("Keyword Hits", total_hits),
        ("Unique Keywords", unique_kws),
        ("Date Range", date_label),
    ]

    render_kpi_cards(field_kpis, columns_count=4)


def render_date_wise_charts(filtered_daily_df, date_label):
    """Date-wise bar charts — scoped to selected date range."""
    st.markdown('<div class="dark-section-box">', unsafe_allow_html=True)
    st.subheader(f"Date-wise Matched Articles and Keyword Hits — {date_label}")

    if filtered_daily_df.empty:
        st.info("No date-wise data found for selected range.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    left2, right2 = st.columns([1, 1])

    with left2:
        fig_match = make_dark_bar(
            filtered_daily_df, "published_date", "matched_articles",
            "Date-wise Matched Articles", "Published Date", "Matched Articles"
        )
        st.plotly_chart(fig_match, use_container_width=True)

    with right2:
        fig_hits = make_dark_bar(
            filtered_daily_df, "published_date", "total_keyword_hits",
            "Date-wise Keyword Hits", "Published Date", "Keyword Hits"
        )
        st.plotly_chart(fig_hits, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# MAIN USER VIEW ORCHESTRATOR
# =========================================================
def render_user_sections(matched_df, daily_keyword_df):
    """
    Single entry point for User View.
    1. Date range selector — controls everything below.
    2. Filter matched_df and daily_keyword_df ONCE.
    3. Pass filtered data to all render functions.
    """

    # ── 1. Date range selector ──
    date_from, date_to, date_label = render_date_range_selector(matched_df)

    # ── 2. Filter once ──
    matched_dates = pd.to_datetime(matched_df["published_date"], errors="coerce").dt.date
    filtered_matched = matched_df[matched_dates.between(date_from, date_to)].copy()

    daily_dates = pd.to_datetime(daily_keyword_df["published_date"], errors="coerce").dt.date
    filtered_daily = daily_keyword_df[daily_dates.between(date_from, date_to)].copy()

    # ── 3. Build keyword summary from filtered data ──
    keyword_summary_df = build_keyword_summary(filtered_matched)

    # ── 4. Render all sections with filtered data ──
    render_keyword_wise_summary(keyword_summary_df, date_label)
    render_matched_articles(filtered_matched, keyword_summary_df, date_label)
    render_keyword_tracker_kpis(filtered_matched, keyword_summary_df, date_label)
    render_date_wise_charts(filtered_daily, date_label)


# =========================================================
# LOAD DATA
# =========================================================
try:
    scraping_df      = load_data("SELECT * FROM vw_scraping_summary;")
    daily_keyword_df = load_data("SELECT * FROM vw_daily_summary;")
    matched_df       = load_data("SELECT * FROM vw_matched_articles;")
except Exception as e:
    st.error(f"Database loading failed: {e}")
    st.stop()


# =========================================================
# SAFETY CHECKS
# =========================================================
if matched_df.empty:
    st.warning("No matched article data found. Run keyword matching first.")
    st.stop()

if "content" not in matched_df.columns:
    st.error(
        "The view vw_matched_articles does not include a content column. "
        "Please recreate the SQL view with a.content."
    )
    st.stop()

REQUIRED_COLS = ["article_id", "headline", "content", "matched_keywords",
                 "matched_keyword_count", "published_date", "newspaper", "link"]
missing_cols = [c for c in REQUIRED_COLS if c not in matched_df.columns]
if missing_cols:
    st.error(f"View vw_matched_articles is missing columns: {missing_cols}")
    st.stop()


# =========================================================
# DAILY SCRAPING SUMMARY (Admin only)
# =========================================================
if not scraping_df.empty:
    daily_scraping_df = scraping_df.copy()
    daily_scraping_df["scraping_date"] = pd.to_datetime(
        daily_scraping_df["start_time"], errors="coerce"
    ).dt.date
    daily_scraping_df = (
        daily_scraping_df
        .groupby("scraping_date", as_index=False)
        .agg(
            total_sessions   =("session_id",   "count"),
            total_scraped    =("total_saved",   "sum"),
            total_processed  =("total_processed","sum"),
            latest_status    =("status",        "last"),
            latest_stop_reason=("stop_reason",  "last")
        )
        .sort_values("scraping_date", ascending=False)
    )
    daily_scraping_df["skipped_or_failed"] = (
        daily_scraping_df["total_processed"] - daily_scraping_df["total_scraped"]
    )
    daily_scraping_df["success_rate_%"] = (
        daily_scraping_df["total_scraped"] / daily_scraping_df["total_processed"] * 100
    ).round(2)

    # Human-readable duration in session table
    if "duration_seconds" in scraping_df.columns:
        scraping_df["duration"] = scraping_df["duration_seconds"].apply(fmt_duration)
else:
    daily_scraping_df = pd.DataFrame()


# =========================================================
# TITLE + VIEW MODE
# =========================================================
st.markdown(
    '<div class="dashboard-title">News Analytics &amp; Intelligence Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dashboard-subtitle">Scraping Performance Monitoring &amp; Keyword Intelligence System</div>',
    unsafe_allow_html=True
)

view_mode = st.sidebar.radio(
    "Select Dashboard View",
    ["User View", "Admin View"],
    index=0
)

if view_mode == "User View":
    st.markdown(
        '<div class="view-note">User View: Showing keyword-matched article intelligence.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="view-note">Admin View: Showing scraper performance monitoring and keyword intelligence.</div>',
        unsafe_allow_html=True
    )


# =========================================================
# ADMIN VIEW ONLY
# =========================================================
if view_mode == "Admin View":

    if scraping_df.empty:
        st.warning("No scraping session data found.")
    else:
        latest_scrape_date = daily_scraping_df["scraping_date"].max()

        latest_scraped = int(
            daily_scraping_df.loc[
                daily_scraping_df["scraping_date"] == latest_scrape_date,
                "total_scraped"
            ].sum()
        )

        total_scraped    = int(scraping_df["total_saved"].sum())
        total_processed  = int(scraping_df["total_processed"].sum())
        total_skipped    = total_processed - total_scraped
        success_rate     = round((total_scraped / total_processed * 100), 2) if total_processed else 0
        keyword_hits_all = int(matched_df["matched_keyword_count"].fillna(0).sum())

        admin_kpis = [
            ("Latest Date Scraped",   str(latest_scrape_date)),
            ("Articles on Latest Date", latest_scraped),
            ("Total Scraped",         total_scraped),
            ("Total Processed",       total_processed),
            ("Skipped / Failed",      total_skipped),
            ("Success Rate",          f"{success_rate}%"),
        ]
        render_kpi_cards(admin_kpis, columns_count=6)

        st.divider()
        st.header("Scraping Performance Monitor")

        left1, right1 = st.columns([1.2, 1])

        with left1:
            st.markdown('<div class="dark-section-box">', unsafe_allow_html=True)
            fig_scrape = make_dark_bar(
                daily_scraping_df.sort_values("scraping_date"),
                "scraping_date", "total_scraped",
                "Date-wise Scraped Articles", "Date", "Articles"
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
# USER VIEW
# =========================================================
if view_mode == "User View":
    render_user_sections(matched_df, daily_keyword_df)