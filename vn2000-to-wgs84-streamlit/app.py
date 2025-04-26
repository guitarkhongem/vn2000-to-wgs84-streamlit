import streamlit as st
import pandas as pd
import re
import math
import folium
from streamlit_folium import st_folium
import analytics  # File analytics.py
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

# 🏁 Cấu hình trang
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")

# 🖼️ Đặt background
def set_background():
    with open("background.png", "rb") as f:
        data = f.read()
    encoded = data.hex()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('data:image/png;base64,{data.hex()}');
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
set_background()

# 🏷️ Header: Logo + Tiêu đề
col1, col2 = st.columns([1, 5], gap="small")
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# 📊 Analytics (lượt view và like)
analytics.log_visit()
analytics.display_sidebar()

# 🛠️ Hàm Parse tọa độ
import re

def parse_coordinates(text):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0

    while i < len(tokens):
        # Nếu token chứa chữ, cố gắng bóc tách số
        token = tokens[i]
        number = re.sub(r'\D', '', token)  # Xóa ký tự không phải số

        if number != '' and len(number) >= 6:
            num = float(number)
            if 330000 <= num <= 670000 or 1000000 <= num <= 2000000:
                coords.append(num)
                i += 1
                continue

        # Nếu token là số thực bình thường
        try:
            val = float(token.replace(',', '.'))
            coords.append(val)
            i += 1
        except ValueError:
            i += 1

    # Gom thành từng bộ (X, Y, H)
    parsed = []
    i = 0
    while i < len(coords) - 1:
        x = coords[i]
        y = coords[i+1]

        # Kiểm tra X, Y hợp lệ
        if not (1000000 <= x <= 2000000 and 330000 <= y <= 670000):
            i += 1
            continue

        # Nếu còn H thì lấy, không thì gán 0
        if i+2 < len(coords):
            h = coords[i+2]
            i += 3
        else:
            h = 0
            i += 2

        parsed.append((x, y, h))

    return parsed


# 🛫 Tabs chuyển đổi
tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    st.markdown("#### 🔢 Nhập tọa độ VN2000 (X Y [H]) – Space, Tab, Enter, STT được phép:")
    in_vn = st.text_area("", height=150, key="vn_in")
    lon0_vn = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_vn")
    if st.button("🔁 Chuyển sang WGS84", key="to_wgs84"):
        parsed = parse_coordinates(in_vn)
        if parsed:
            df = pd.DataFrame(
                [vn2000_to_wgs84_baibao(x, y, h, lon0_vn) for x, y, h in parsed],
                columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]
            )
            st.session_state.df = df
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần X Y [H]).")

with tab2:
    st.markdown("#### 🔢 Nhập tọa độ WGS84 (Lat Lon [H]) – Space, Tab, Enter, STT được phép:")
    in_wg = st.text_area("", height=150, key="wg_in")
    lon0_wg = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_wg")
    if st.button("🔁 Chuyển sang VN2000", key="to_vn2000"):
        parsed = parse_coordinates(in_wg)
        if parsed:
            df = pd.DataFrame(
                [wgs84_to_vn2000_baibao(lat, lon, h, lon0_wg) for lat, lon, h in parsed],
                columns=["X (m)", "Y (m)", "h (m)"]
            )
            st.session_state.df = df
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần Lat Lon [H]).")

# 📍 Nếu có kết quả
if "df" in st.session_state:
    df = st.session_state.df
    st.markdown("### 📊 Kết quả chuyển đổi")
    st.dataframe(df)

    # Nếu Lat/Lon thì vẽ bản đồ
    if {"Vĩ độ (Lat)", "Kinh độ (Lon)"}.issubset(df.columns):
        center_lat = df["Vĩ độ (Lat)"].mean()
        center_lon = df["Kinh độ (Lon)"].mean()
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri.WorldImagery"
        )
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]),
                radius=3,
                color="red",
                fill=True,
                fill_opacity=0.8
            ).add_to(m)
        st_folium(m, width=900, height=500)


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
