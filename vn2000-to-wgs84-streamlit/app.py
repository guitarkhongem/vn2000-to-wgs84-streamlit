import streamlit as st
import streamlit.components.v1 as components

st.title("VN2000 ⇄ WGS84 Converter")

# Nhúng Google My Maps (Google Earth) làm nền
# Lưu ý: Map của bạn phải được chia sẻ “public”
map_url = "https://www.google.com/maps/d/embed?mid=1gHTIagvnAKWB66oVKHlkAlpHyra8UF8&ll=16.70561447553423,106.67600750000003&z=10"
components.iframe(map_url, width=800, height=500)


import pandas as pd
import math
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

# Hiển thị logo và tên đơn vị ngang hàng
col_logo, col_title = st.columns([1, 5], gap="small")
with col_logo:
    st.image("logo.jpg", width=80)
with col_title:
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# Thư viện Folium
import folium
from streamlit_folium import st_folium

import re

def parse_coordinates(text, group=3):
    """
    Chia token space/tab/newline thành nhóm `group` float.
    Bỏ qua token STT nếu
     - chứa ký tự chữ (A10, PT01…)
     - hoặc là số nguyên không chứa dấu '.' khi nó đứng trước đủ group+1 token (ví dụ '10' trước X Y Z)
    """
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i + group <= len(tokens):
        t0 = tokens[i]
        # Bỏ STT chứa chữ hoặc số nguyên mà kế tiếp có đủ group giá trị
        if re.search(r'[A-Za-z]', t0) or ('.' not in t0 and re.fullmatch(r'\d+', t0) and len(tokens) - i >= group+1):
            i += 1
            continue

        # Lấy nhóm group token
        chunk = tokens[i : i+group]
        try:
            vals = [float(x.replace(',', '.')) for x in chunk]
            coords.append(vals)
            i += group
        except ValueError:
            # chunk chưa đúng, bỏ qua token đầu và thử lại
            i += 1

    return coords

st.markdown("#### 🌐 Overlay KML (tùy chọn)")
kml_file = st.file_uploader("Upload file .kml của bạn", type="kml")

    # Hiển thị trong Streamlit
    st_folium(m, width=700, height=500)


st.title("VN2000 ⇄ WGS84 Converter")

tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    st.markdown("#### 🔢 Nhập tọa độ VN2000 (X Y Z – space/tab/newline):")
    coords_input = st.text_area("", height=150, key="vn_in")
    lon0 = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_vn")
    if st.button("🔁 Chuyển WGS84"):
        parsed = parse_coordinates(coords_input, group=3)
        results = []
        for x, y, z in parsed:
            lat, lon, h = vn2000_to_wgs84_baibao(x, y, z, lon0)
            results.append((lat, lon, h))
        if results:
            df = pd.DataFrame(results, columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")
st.markdown("#### 🌐 Overlay KML (tùy chọn)")
kml_file = st.file_uploader("Upload file .kml của bạn", type="kml")

with tab2:
    st.markdown("#### 🔢 Nhập tọa độ WGS84 (Lat Lon H – space/tab/newline):")
    coords_input = st.text_area("", height=150, key="wg_in")
    lon0 = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_wg")
    if st.button("🔁 Chuyển VN2000"):
        parsed = parse_coordinates(coords_input, group=3)
        results = []
        for lat, lon, h in parsed:
            x, y, h_vn = wgs84_to_vn2000_baibao(lat, lon, h, lon0)
            results.append((x, y, h_vn))
        if results:
            df = pd.DataFrame(results, columns=["X (m)", "Y (m)", "h (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")

# ... sau khi st.session_state.df đã được gán
if "df" in st.session_state:
    render_map(st.session_state.df, kml_bytes=kml_file)


st.markdown("---")
st.markdown(
    "Tác giả: Trần Trường Sinh  \n"
    "Số điện thoại: 0917.750.555  \n"
)
st.markdown("---")
st.markdown(
    "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ TRONG CÔNG NGHỆ MÁY BAY KHÔNG NGƯỜI LÁI...**  \n"
    "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
    "¹ Trường Đại học Mỏ - Địa chất  \n"
    "² Công ty CP Xây dựng và Thương mại QT Miền Bắc  \n"
    "_Hội nghị Quốc Gia Về Công Nghệ Địa Không Gian, 2021_"
)
