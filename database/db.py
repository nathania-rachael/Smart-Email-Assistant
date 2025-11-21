import sqlite3
import pandas as pd
import os

# Absolute path to emails.db (inside /database folder)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emails.db")

def get_connection():
    # Prevents "database is locked" errors on Streamlit Cloud
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def fetch_all_emails():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM emails", conn)
    conn.close()
    return df
