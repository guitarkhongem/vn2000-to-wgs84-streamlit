# analytics.py

import sqlite3
import pandas as pd

conn = sqlite3.connect("analytics.db", check_same_thread=False)
c = conn.cursor()

# Khởi tạo bảng nếu chưa có
c.execute("CREATE TABLE IF NOT EXISTS visits (ts TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY, count INTEGER)")
c.execute("INSERT OR IGNORE INTO likes (id, count) VALUES (1, 0)")
conn.commit()

def log_visit():
    c.execute("INSERT INTO visits (ts) VALUES (datetime('now', 'localtime'))")
    conn.commit()

def like():
    c.execute("UPDATE likes SET count = count + 1 WHERE id = 1")
    conn.commit()

def get_stats():
    c.execute("SELECT COUNT(*) FROM visits")
    visits = c.fetchone()[0]
    c.execute("SELECT count FROM likes WHERE id = 1")
    likes = c.fetchone()[0]
    return visits, likes

def visits_by_day():
    df = pd.read_sql_query("""
        SELECT DATE(ts) AS date, COUNT(*) AS count
        FROM visits
        GROUP BY DATE(ts)
        ORDER BY DATE(ts)
    """, conn)
    return df

def visits_by_hour():
    df = pd.read_sql_query("""
        SELECT STRFTIME('%H', ts) AS hour, COUNT(*) AS count
        FROM visits
        GROUP BY hour
        ORDER BY hour
    """, conn)
    return df
