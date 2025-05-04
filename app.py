import os
import streamlit as st
import pandas as pd
import re
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon, LineString
from PIL import Image
import tempfile

# --- Custom functions ---
from functions.background import set_background
from functions.parse import parse_coordinates
from functions.kml import df_to_kml
from functions.footer import show_footer
from functions.converter import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao
from functions.area import compute_polygon_area
from functions.edges import add_edge_lengths
from functions.markers import add_numbered_markers
from functions.polygon import draw_polygon
from functions.area import compare_areas
# --- Page setup ---
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")
set_background("assets/background.png")

st.markdown("""
<style>
div.stButton > button, div.stDownloadButton > button {
    color: #B30000;
    font-weight: bold;
}
iframe {
    height: 400px !important;
    min-height: 400px !important;
}
.css-1aumxhk { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.jpg", width=90)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# --- Longitude zone selector ---
lon0_choices = {
    104.5: "Kiên Giang, Cà Mau",
    104.75: "Lào Cai, Phú Thọ, Nghệ An, An Giang",
    105.0: "Vĩnh Phúc, Hà Nam, Ninh Bình, Thanh Hóa, Đồng Tháp, TP. Cần Thơ, Hậu Giang, Bạc Liêu",
    105.5: "Hà Giang, Bắc Ninh, Hải Dương, Hưng Yên, Nam Định, Thái Bình, Hà Tĩnh, Tây Ninh, Vĩnh Long, Trà Vinh",
    105.75: "TP. Hải Phòng, Bình Dương, Long An, Tiền Giang, Bến Tre, TP. HỒ Chí Minh",
    106.0: "Tuyên Quang, Hòa Bình, Quảng Bình",
    106.25: "Quảng Trị, Bình Phước",
    106.5: "Bắc Kạn, Thái Nguyên",
    107.0: "Bắc Giang, Thừa Thiên – Huế",
    107.25: "Lạng Sơn",
    107.5: "Kon Tum",
    107.75: "TP. Đà Nẵng, Quảng Nam, Đồng Nai, Bà Rịa – Võng Tàu, Lâm Đồng",
    108.0: "Quảng Ngãi",
    108.25: "Bình Định, Khánh Hòa, Ninh Thuận",
    108.5: "Gia Lai, Đắk Lắk, Đắk Nông, Phú Yên, Bình Thuận"
}
lon0_display = [f"{lon} – {province}" for lon, province in lon0_choices.items()]
default_index = list(lon0_choices.keys()).index(106.25)

col_left, col_mid, col_map = st.columns([1, 1, 2])

# --- Input column ---
with col_left:
    st.markdown("## 📄 Upload hoặc nhập toạ độ")
    uploaded_file = st.file_uploader("Tải file TXT hoặc CSV", type=["txt", "csv"])

    content = ""
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")

    coords_input = st.text_area("Nội dung toạ độ", value=content, height=180)

    col1, col2, col3 = st.columns([3, 4, 3])

with col1:
    st.subheader("📅 Nhập dữ liệu toạ độ")
    input_text = st.text_area("Dán hoặc gõ toạ độ vào đây:", height=200)

    with st.expander("📘 Xem định dạng toạ độ hỗ trợ"):
        st.markdown("""
        | STT | Định dạng nhập                            | Ghi chú                             |
        |-----|--------------------------------------------|--------------------------------------|
        | 1   | `E12345678 N56781234`                      | EN mã hiệu                           |
        | 2   | `A01 1838446.03 550074.77 37.98`           | STT X Y H                            |
        | 3   | `A01 1838446.03 550074.77`                | STT X Y _(khuyết H)_ ✅ **Mới**      |
        | 4   | `1838446.03 550074.77`                    | X Y                                  |
        | 5   | `1838446.03 550074.77 37.98`              | X Y H                                |

        ✅ **Phân cách** có thể là: khoảng trắng, tab, hoặc xuống dòng.  
        ❌ **Toạ độ ngoài miền hợp lệ** (X, Y, H) sẽ được liệt kê ở bảng lỗi.
        """, unsafe_allow_html=True)

# --- Footer ---
show_footer()

# --- Map rendering update fix ---
if "df" in st.session_state and {"Vĩ độ (Lat)", "Kinh độ (Lon)"}.issubset(st.session_state.df.columns):
    df_sorted = st.session_state.df.copy()
    df_sorted["Tên điểm"] = df_sorted["Tên điểm"].astype(str)
    df_sorted = df_sorted.sort_values(
        by="Tên điểm",
        key=lambda col: col.map(lambda x: int(x) if x.isdigit() else x),
        ascending=True
    ).reset_index(drop=True)


        map_type = st.selectbox("Chế độ bản đồ", options=["Giao Thông", "Vệ tinh"], index=0)
        tileset = "OpenStreetMap" if map_type == "Giao Thông" else "Esri.WorldImagery"

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🔵 Nối các điểm"):
                st.session_state.join_points = not st.session_state.get("join_points", False)

        with col_btn2:
            if "df" in st.session_state and {"Vĩ độ (Lat)", "Kinh độ (Lon)"} <= set(st.session_state.df.columns):
                if st.button("📐 Tính diện tích VN2000 / WGS84"):
                    parsed, errors = parse_coordinates(coords_input)

                    if not parsed:
                        st.warning("⚠️ Dữ liệu đầu vào không hợp lệ hoặc chưa có.")
                    else:
                        xy_points = [(x, y) for _, x, y, _ in parsed]
                        latlon_points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in st.session_state.df.iterrows()]
                        A1, A2, diff, ha1, ha2 = compare_areas(xy_points, latlon_points)
                        st.markdown(f"""
                        ### 📐 So sánh diện tích
                        🧮 Shoelace (VN2000): `{A1:,.1f} m²` (~{ha1:.1f} ha)  
                        🌍 Geodesic (WGS84): `{A2:,.1f} m²` (~{ha2:.1f} ha)  
                        """)
                       
        with col_btn3:
            if st.button("📏 Hiện kích thước cạnh"):
                st.session_state.show_lengths = not st.session_state.get("show_lengths", False)

        m = folium.Map(location=[df_sorted.iloc[0]["Vĩ độ (Lat)"], df_sorted.iloc[0]["Kinh độ (Lon)"]], zoom_start=15, tiles=tileset)

        if st.session_state.get("join_points", False):
            points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]
            draw_polygon(m, points)
            add_numbered_markers(m, df_sorted)
            if st.session_state.get("show_lengths", False):
                add_edge_lengths(m, points)
        else:
            add_numbered_markers(m, df_sorted)

        st_folium(m, width="100%", height=400)
   


# --- Footer ---
show_footer()
