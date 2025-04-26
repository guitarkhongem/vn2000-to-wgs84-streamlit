import sqlite3

def init_db():
    conn = sqlite3.connect("analytics.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS visits (ts TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY, count INTEGER)")
    c.execute("INSERT OR IGNORE INTO likes (id, count) VALUES (1, 0)")
    conn.commit()
    return conn, c

def log_visit(c, conn):
    c.execute("INSERT INTO visits (ts) VALUES (datetime('now','localtime'))")
    conn.commit()

def get_stats(c):
    c.execute("SELECT COUNT(*) FROM visits")
    visits = c.fetchone()[0]
    c.execute("SELECT count FROM likes WHERE id=1")
    likes = c.fetchone()[0]
    return visits, likes

def increment_like(c, conn):
    c.execute("UPDATE likes SET count = count + 1 WHERE id=1")
    conn.commit()
