import os
import sqlite3
import datetime
from urllib.parse import urlparse, urlunparse

def extract_edge_history(output_file="edge_history.txt"):
    # Edge history location (Windows)
    edge_history_path = os.path.expanduser(
        r"~\AppData\Local\Microsoft\Edge\User Data\Default\History"
    )

    if not os.path.exists(edge_history_path):
        raise FileNotFoundError("Edge history database not found! Is Edge installed?")

    # Connect to the database
    conn = sqlite3.connect(edge_history_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT url, title, last_visit_time
        FROM urls
        ORDER BY last_visit_time DESC
    """)

    entries = cursor.fetchall()

    def convert_time(chrome_time):
        if chrome_time:
            epoch_start = datetime.datetime(1601, 1, 1)
            return epoch_start + datetime.timedelta(microseconds=chrome_time)
        else:
            return None

    def strip_query_params(url):
        try:
            parsed = urlparse(url)
            clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            return clean_url
        except Exception:
            return url  # fallback in case parsing fails

    with open(output_file, "w", encoding="utf-8") as f:
        for url, title, last_visit_time in entries:
            visit_time = convert_time(last_visit_time)
            if visit_time:
                clean_url = strip_query_params(url)
                f.write(f"Visited '{title}' at {visit_time.strftime('%Y-%m-%d %H:%M:%S')} ({clean_url})\n")

    conn.close()
    print(f"✅ Browsing history saved to {output_file}")

if __name__ == "__main__":
    extract_edge_history()
