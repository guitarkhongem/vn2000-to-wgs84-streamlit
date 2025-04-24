import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="centered")

# Tiêu đề và Google My Maps embed
st.title("VN2000 ⇄ WGS84 Converter")
map_url = "https://www.google.com/maps/d/embed?mid=1gHTIagvnAKWB66oVKHlkAlpHyra8UF8&ll=16.70561447553423,106.67600750000003&z=10"
components.iframe(map_url, width=800, height=500)

# Logo và đơn vị
col_logo, col_title = st.columns([1, 5], gap="small")
with col_logo:
    st.image("logo.jpg", width=80)
with col_title:
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

import pandas as pd
import math
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

import folium
from streamlit_folium import st_folium
import re
import tempfile

def parse_coordinates(text, group=3):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i + group <= len(tokens):
        t0 = tokens[i]
        if re.search(r'[A-Za-z]', t0) or ('.' not in t0 and re.fullmatch(r'\d+', t0) and len(tokens) - i >= group+1):
            i += 1
            continue
        chunk = tokens[i : i+group]
        try:
            vals = [float(x.replace(',', '.')) for x in chunk]
            coords.append(vals)
            i += group
        except ValueError:
            i += 1
    return coords

def render_map(df, kml_file=None):
    if df is None or df.empty:
        st.warning("⚠️ Không có dữ liệu để hiển thị bản đồ.")
        return

    lat_col = "Vĩ độ (Lat)" if "Vĩ độ (Lat)" in df.columns else "latitude"
    lon_col = "Kinh độ (Lon)" if "Kinh độ (Lon)" in df.columns else "longitude"
    df_map = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})

    center_lat = float(df_map["latitude"].mean())
    center_lon = float(df_map["longitude"].mean())

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri.WorldImagery"
    )

    if kml_file is not None:
        tmp = tempfile.NamedTemporaryFile(suffix=".kml", delete=False)
        tmp.write(kml_file.getvalue())
        tmp.flush()
        folium.Kml(tmp.name, name="Overlay").add_to(m)
        folium.LayerControl().add_to(m)

    for _, row in df_map.iterrows():
        folium.CircleMarker(
            location=(row["latitude"], row["longitude"]),
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    st_folium(m, width=700, height=500)


tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    st.markdown("#### 🔢 Nhập tọa độ VN2000 (X Y Z – space/tab/newline hoặc kèm STT):")
    coords_input = st.text_area("", height=150, key="vn_in")
    lon0 = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_vn")
    if st.button("🔁 Chuyển WGS84"):
        parsed = parse_coordinates(coords_input, group=3)
        results = []
        for x, y, z in parsed:
            results.append(vn2000_to_wgs84_baibao(x, y, z, lon0))
        if results:
            df = pd.DataFrame(results, columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")
    st.markdown("#### 🌐 Overlay KML (tùy chọn)")
    kml_file1 = st.file_uploader("Upload file .kml của bạn", type="kml", key="kml1")

with tab2:
    st.markdown("#### 🔢 Nhập tọa độ WGS84 (Lat Lon H – space/tab/newline hoặc kèm STT):")
    coords_input = st.text_area("", height=150, key="wg_in")
    lon0 = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_wg")
    if st.button("🔁 Chuyển VN2000"):
        parsed = parse_coordinates(coords_input, group=3)
        results = []
        for lat, lon, h in parsed:
            results.append(wgs84_to_vn2000_baibao(lat, lon, h, lon0))
        if results:
            df = pd.DataFrame(results, columns=["X (m)", "Y (m)", "h (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")
    st.markdown("#### 🌐 Overlay KML (tùy chọn)")
    kml_file2 = st.file_uploader("Upload file .kml của bạn", type="kml", key="kml2")

# Gọi vẽ bản đồ với KML tương ứng tab
if "df" in st.session_state:
    # ưu tiên kml từ tab1 nếu có, ngược lại dùng tab2
    kml_to_use = kml_file1 or kml_file2
    render_map(st.session_state.df, kml_file=kml_to_use)

st.markdown("---")
st.markdown("Tác giả: Trần Trường Sinh  \nSố điện thoại: 0917.750.555  \n")
st.markdown("---")
st.markdown(
    "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ TRONG CÔNG NGHỆ MÁY BAY ...**  \n"
    "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
    "¹ Trường Đại học Mỏ - Địa chất  \n"
    "² Công ty CP Xây dựng và Thương mại QT Miền Bắc  \n"
    "_Hội nghị Quốc Gia Về Công Nghệ Địa Không Gian, 2021_"
)
