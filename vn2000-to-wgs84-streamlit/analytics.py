# analytics.py
import sqlite3
import streamlit as st

# Kết nối hoặc tạo mới database analytics.db
conn = sqlite3.connect("analytics.db", check_same_thread=False)
c = conn.cursor()

# Tạo bảng nếu chưa có
c.execute('''
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY,
        count INTEGER
    )
''')
c.execute('INSERT OR IGNORE INTO likes (id, count) VALUES (1, 0)')
conn.commit()

# Ghi nhận lượt truy cập
def log_visit():
    c.execute('INSERT INTO visits (ts) VALUES (datetime("now", "localtime"))')
    conn.commit()

# Ghi nhận lượt like
def add_like():
    c.execute('UPDATE likes SET count = count + 1 WHERE id = 1')
    conn.commit()

# Lấy dữ liệu thống kê
def get_stats():
    c.execute('SELECT COUNT(*) FROM visits')
    visit_count = c.fetchone()[0]
    c.execute('SELECT count FROM likes WHERE id = 1')
    like_count = c.fetchone()[0]
    return visit_count, like_count

# Hiển thị ở sidebar
def display_sidebar():
    visit_count, like_count = get_stats()
    st.sidebar.markdown("## 📊 Thống kê sử dụng")
    st.sidebar.markdown(f"- 🔍 **Lượt truy cập:** `{visit_count}`")
    st.sidebar.markdown(f"- 👍 **Lượt thích:** `{like_count}`")
    if st.sidebar.button("👍 Thích ứng dụng"):
        add_like()
        st.success("💖 Cảm ơn bạn đã thích!")
