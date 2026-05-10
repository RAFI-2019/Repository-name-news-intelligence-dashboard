# =========================
# IMPORT EXCEL → POSTGRESQL
# =========================

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# =========================
# CONFIG
# =========================
# BASE_DIR = r"D:\No_2025\DR\Partho_Vai_September_13_2025\Scrapping_Test\Scrapping_Easy\Prothomalo\OandC\May_07_2026"

# DATA_DIR = os.path.join(BASE_DIR, "data")

# ARTICLE_FILE = os.path.join(DATA_DIR, "ProthomAlo_20260507_121326.xlsx")
# SESSION_FILE = os.path.join(DATA_DIR, "ProthomAlo_Session_Log.xlsx")


# BASE_DIR = r"D:\2026\OandC\May_10_2026\ProthomAlo_20260510_095521.xlsx"

# DATA_DIR = BASE_DIR

# ARTICLE_FILE = os.path.join(DATA_DIR, "ProthomAlo_20260507_121326.xlsx")
# SESSION_FILE = os.path.join(DATA_DIR, "ProthomAlo_Session_Log.xlsx")




# =========================
# CONFIG
# =========================

BASE_DIR = r"D:\2026\OandC\May_10_2026"

ARTICLE_FILE = os.path.join(BASE_DIR, "ProthomAlo_20260510_095521.xlsx")
SESSION_FILE = os.path.join(BASE_DIR, "ProthomAlo_Session_Log.xlsx")

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "abc123",
    "dbname": "O_C_News_Monitor"
}

# =========================
# HELPER
# =========================
def clean_value(value):
    if pd.isna(value):
        return None
    return value

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# =========================
# IMPORT SESSION LOG
# =========================
def import_sessions():
    df = pd.read_excel(SESSION_FILE)

    conn = get_connection()
    cur = conn.cursor()

    records = []

    for _, row in df.iterrows():
        records.append((
            clean_value(row["session_id"]),
            clean_value(row["source_name"]),
            clean_value(row["start_time"]),
            clean_value(row["end_time"]),
            int(row["duration_seconds"]) if not pd.isna(row["duration_seconds"]) else None,
            int(row["total_saved"]) if not pd.isna(row["total_saved"]) else None,
            int(row["total_processed"]) if not pd.isna(row["total_processed"]) else None,
            clean_value(row["status"]),
            clean_value(row["stop_reason"]),
            clean_value(row["output_file"])
        ))

    query = """
    INSERT INTO scraping_sessions (
        session_id, source_name, start_time, end_time,
        duration_seconds, total_saved, total_processed,
        status, stop_reason, output_file
    )
    VALUES %s
    ON CONFLICT (session_id) DO NOTHING
    """

    execute_values(cur, query, records)
    conn.commit()

    cur.close()
    conn.close()

    print(f"✅ Sessions processed: {len(records)}")

# =========================
# IMPORT ARTICLES
# =========================
def import_articles():
    df = pd.read_excel(ARTICLE_FILE)

    # Correct session_id:
    # ProthomAlo_20260428_211709.xlsx → PROTHOMALO_20260428_211709
    session_id = "PROTHOMALO_" + os.path.basename(ARTICLE_FILE) \
        .replace("ProthomAlo_", "") \
        .replace(".xlsx", "")

    conn = get_connection()
    cur = conn.cursor()

    records = []

    for _, row in df.iterrows():
        records.append((
            session_id,
            clean_value(row.get("Newspaper")),
            clean_value(row.get("Category")),
            clean_value(row.get("Sub-Head")),
            clean_value(row.get("Headline")),
            clean_value(row.get("Sub-Head-2")),
            clean_value(row.get("Link")),
            clean_value(row.get("Author")),
            clean_value(row.get("Location")),
            clean_value(row.get("Published_Time")),
            clean_value(row.get("Published_Time_Eng")),
            clean_value(row.get("Published_Date")),
            clean_value(row.get("Updated_Time")),
            clean_value(row.get("Updated_Time_Eng")),
            clean_value(row.get("Content")),
            clean_value(row.get("Version"))
        ))

    query = """
    INSERT INTO news_articles (
        session_id, newspaper, category, sub_head, headline,
        sub_head_2, link, author, location,
        published_time, published_time_eng, published_date,
        updated_time, updated_time_eng,
        content, version
    )
    VALUES %s
    ON CONFLICT (newspaper, link) DO NOTHING
    """

    execute_values(cur, query, records)
    conn.commit()

    cur.close()
    conn.close()

    print(f"✅ Articles processed: {len(records)}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Starting import...")

    import_sessions()
    import_articles()

    print("🎯 Import completed successfully.")