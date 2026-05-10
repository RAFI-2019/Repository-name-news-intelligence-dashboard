# =========================
# KEYWORD MATCHING ENGINE
# news_articles + keyword_master → keyword_matches
# =========================

import re
import psycopg2
from psycopg2.extras import execute_values

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "abc123",
    "dbname": "O_C_News_Monitor"
}

RESET_OLD_MATCHES = True   # True = clean previous matches and run fresh


# =========================
# TEXT CLEANER
# =========================
def clean_text(value):
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# MAIN MATCHING FUNCTION
# =========================
def run_keyword_matching():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("🚀 Keyword matching started...")

    if RESET_OLD_MATCHES:
        cur.execute("DELETE FROM keyword_matches;")
        conn.commit()
        print("🧹 Old keyword matches deleted.")

    # Load active articles
    cur.execute("""
        SELECT article_id, headline, content
        FROM news_articles
        WHERE headline IS NOT NULL OR content IS NOT NULL;
    """)
    articles = cur.fetchall()

    # Load keywords
    cur.execute("""
        SELECT keyword_id, keyword
        FROM keyword_master
        WHERE keyword IS NOT NULL
        ORDER BY LENGTH(keyword) DESC;
    """)
    keywords = cur.fetchall()

    print(f"📰 Articles loaded : {len(articles)}")
    print(f"🔑 Keywords loaded : {len(keywords)}")

    match_records = []

    for article_id, headline, content in articles:
        combined_text = clean_text(headline) + " " + clean_text(content)

        if not combined_text.strip():
            continue

        for keyword_id, keyword in keywords:
            keyword_clean = clean_text(keyword)

            if not keyword_clean:
                continue

            # Exact substring matching
            if keyword_clean in combined_text:
                match_records.append((
                    article_id,
                    keyword_id,
                    keyword_clean
                ))

    if match_records:
        insert_query = """
        INSERT INTO keyword_matches (
            article_id, keyword_id, keyword
        )
        VALUES %s
        ON CONFLICT (article_id, keyword_id) DO NOTHING;
        """

        execute_values(cur, insert_query, match_records)
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM keyword_matches;")
    total_matches = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT article_id)
        FROM keyword_matches;
    """)
    matched_articles = cur.fetchone()[0]

    cur.close()
    conn.close()

    print("✅ Keyword matching completed.")
    print(f"🔢 Total keyword matches  : {total_matches}")
    print(f"📰 Matched articles       : {matched_articles}")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_keyword_matching()