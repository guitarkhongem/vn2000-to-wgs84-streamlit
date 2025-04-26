import streamlit as st
import pandas as pd
import math
import re
import folium
from streamlit_folium import st_folium
from functions import vn2000_to_wgs84_baibao
import analytics

# Set page config
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")

# Init database
conn, c = analytics.init_db()
analytics.log_visit(c, conn)

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# Parse
def parse_coordinates(text):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i < len(tokens):
        t0 = tokens[i]
        if re.match(r'^[A-Za-z0-9]+$', t0) and i+1 < len(tokens):
            i += 1  # Bỏ mã hiệu
        try:
            x = float(tokens[i])
            y = float(tokens[i+1])
            z = float(tokens[i+2]) if i+2 < len(tokens) else 0
            if 1e6 < x < 2e6 and 330000 < y < 670000 and -1000 < z < 3200:
                coords.append((x, y, z))
            i += 3
        except:
            i += 1
    return coords

# UI
st.subheader("Nhập tọa độ VN2000 (cách nhau dấu cách/tab hoặc xuống dòng):")
coords_input = st.text_area("", height=200)
if st.button("🔄 Chuyển đổi VN2000 ➔ WGS84"):
    parsed = parse_coordinates(coords_input)
    if parsed:
        results = []
        for x, y, z in parsed:
            lat, lon, _ = vn2000_to_wgs84_baibao(x, y, z, 106.25)
            results.append((lat, lon))
        df = pd.DataFrame(results, columns=["Vĩ độ (Lat)", "Kinh độ (Lon)"])
        st.success("🎯 Kết quả:")
        st.dataframe(df)

        # Map
        if not df.empty:
            st.markdown("### 🌍 Bản đồ:")
            center_lat = df["Vĩ độ (Lat)"].mean()
            center_lon = df["Kinh độ (Lon)"].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="Stamen Terrain")
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]),
                    radius=3, color="red", fill=True, fill_opacity=0.7
                ).add_to(m)
            st_folium(m, width=800, height=500)

# Sidebar analytics
visit_count, like_count = analytics.get_stats(c)
st.sidebar.markdown(f"👀 Lượt truy cập: **{visit_count}**")
st.sidebar.markdown(f"👍 Lượt thích: **{like_count}**")
if st.sidebar.button("💖 Like ứng dụng"):
    analytics.increment_like(c, conn)
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown(
    "📌 Tác giả: Trần Trường Sinh  \n"
    "📞 Số điện thoại: 0917.750.555"
)
st.markdown(
    "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ TRONG CÔNG NGHỆ MÁY BAY KHÔNG NGƯỜI LÁI CÓ ĐỊNH VỊ TÂM CHỤP CHÍNH XÁC**  \n"
    "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
    "¹ Trường Đại học Mỏ - Địa chất  \n"
    "² Công ty CP Xây dựng và Thương mại QT Miền Bắc  \n"
    "_Hội nghị Khoa học Quốc gia Về Công nghệ Địa không gian, 2021_"
)
