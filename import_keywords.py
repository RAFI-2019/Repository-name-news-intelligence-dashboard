# =========================
# IMPORT KEYWORDS → POSTGRESQL
# =========================

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# =========================
# CONFIG
# =========================
BASE_DIR = r"D:\No_2025\DR\Partho_Vai_September_13_2025\Scrapping_Test\Scrapping_Easy\Prothomalo\OandC\Dashboard_April_28_2026"

KEYWORD_FILE = os.path.join(BASE_DIR, "keyword", "Bangla_Keywords_List.xlsx")

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "abc123",
    "dbname": "O_C_News_Monitor"
}

# =========================
# MAIN
# =========================
def main():
    df = pd.read_excel(KEYWORD_FILE)

    # assume first column contains keywords
    col = df.columns[0]

    keywords = (
        df[col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    records = [(k,) for k in keywords]

    query = """
    INSERT INTO keyword_master (keyword)
    VALUES %s
    ON CONFLICT (keyword) DO NOTHING
    """

    execute_values(cur, query, records)
    conn.commit()

    cur.close()
    conn.close()

    print(f"✅ Keywords imported: {len(records)}")

# =========================
if __name__ == "__main__":
    main()