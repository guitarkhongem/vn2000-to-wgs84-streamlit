import os
import streamlit as st
import pandas as pd
import re
import folium

from streamlit_folium import st_folium
from shapely.geometry import Polygon, LineString
from geographiclib.geodesic import Geodesic

from functions.background import set_background
from functions.parse import parse_coordinates
from functions.kml import df_to_kml
from functions.footer import show_footer
from functions.converter import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

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
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚcNG HÓA")

lon0_choices = {
    104.5: "Kiên Giang, Cà Mau",
    104.75: "Lào Cai, Phú Thọ, Nghệ An, An Giang",
    105.0: "Vĩnh Phúc, Hà Nam, Ninh Bình, Thanh Hóa, Đồng Tháp, TP. Cần Thơ, Hậu Giang, Bạc Liêu",
    105.5: "Hà Giang, Bắc Ninh, Hải Dương, Hưng Yên, Nam Định, Thái Bình, Hà Tĩnh, Tây Ninh, Vĩnh Long, Trà Vinh",
    105.75: "TP. Hải Phòng, Bình Dương, Long An, Tiền Giang, Bến Tre, TP. Hồ Chí Minh",
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

import tempfile
from PIL import Image

with col_left:
    st.markdown("## 📄 Upload hoặc nhập toạ độ")
    uploaded_file = st.file_uploader("Tải file TXT hoặc CSV", type=["txt", "csv"])

    content = ""
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")

    coords_input = st.text_area("Nội dung toạ độ", value=content, height=180)

    st.markdown("""
    <small>
    📌 <b>Hướng dẫn nhập toạ độ</b>:
    <ul>
  <li>Nhập mỗi dòng theo cú pháp: <code>STT X Y [Z]</code></li>
  <li>Ví dụ:</li>
    </ul>
    </small>

    <pre style='background-color:#f8f8f8; padding: 6px; border-radius: 6px; font-size: 6px'>
    <li>1 2304567.23 543219.77 35.2
    <li>2 2304568.88 543220.55
    <li>3 2304569.00 543221.10 34
    </pre>

    <small>
    <ul>
  <li>Có thể tải file <code>.txt</code> / <code>.csv</code></li>
  <li>Dấu cách, tab hoặc dấu phẩy đều được chấp nhận</li>
  <li>Nếu không có Z (cao độ) sẽ mặc định là <code>0.0</code></li>
    </ul>
    </small>
""", unsafe_allow_html=True)

    selected_display = st.selectbox("🧽️ Chọn kinh tuyến trục", options=lon0_display, index=default_index)

    st.markdown("### 🔄 Chuyển đổi toạ độ")
    tab1, tab2 = st.tabs(["VN2000 ➔ WGS84", "WGS84 ➔ VN2000"])

    with tab1:
        if st.button("➡️ Chuyển sang WGS84"):
            parsed, errors = parse_coordinates(coords_input)
            if parsed:
                df = pd.DataFrame(
                    [(ten, *vn2000_to_wgs84_baibao(x, y, h, float(selected_display.split("\u2013")[0].strip()))) for ten, x, y, h in parsed],
                    columns=["Tên điểm", "Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]
                )
                st.session_state.df = df
                st.session_state.textout = "\n".join(
                    f"{row['Tên điểm']} {row['Vĩ độ (Lat)']} {row['Kinh độ (Lon)']} {row['H (m)']}"
                    for _, row in df.iterrows()
                )
                st.success(f"✅ Đã xử lý {len(df)} điểm hợp lệ.")
            else:
                st.error("⚠️ Không có dữ liệu hợp lệ!")

    with tab2:
        if st.button("⬅️ Chuyển sang VN2000"):
            tokens = re.split(r"[\s\n]+", coords_input.strip())
            coords = []
            i = 0
            while i < len(tokens):
                chunk = []
                for _ in range(3):
                    if i < len(tokens):
                        try:
                            chunk.append(float(tokens[i].replace(",", ".")))
                        except:
                            break
                        i += 1
                if len(chunk) == 2:
                    chunk.append(0.0)
                if len(chunk) == 3:
                    coords.append(chunk)
                else:
                    i += 1

            if coords:
                df = pd.DataFrame(
                    [("", *wgs84_to_vn2000_baibao(lat, lon, h, float(selected_display.split("\u2013")[0].strip()))) for lat, lon, h in coords],
                    columns=["Tên điểm", "X (m)", "Y (m)", "h (m)"]
                )
                st.session_state.df = df
                st.session_state.textout = "\n".join(
                    f"{row['Tên điểm']} {row['X (m)']} {row['Y (m)']} {row['h (m)']}"
                    for _, row in df.iterrows()
                )
                st.success(f"✅ Đã xử lý {len(df)} điểm.")
            else:
                st.error("⚠️ Không có dữ liệu hợp lệ!")

with col_mid:
    st.markdown("### 📊 Kết quả")
    if "df" in st.session_state:
        df = st.session_state.df
        st.dataframe(df, height=250)
        st.text_area("📄 Text kết quả", st.session_state.get("textout", ""), height=200)

        col_csv, col_kml = st.columns(2)
        with col_csv:
            st.download_button(
                label="📀 Tải CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="converted_points.csv",
                mime="text/csv"
            )
        with col_kml:
            kml = df_to_kml(df)
            if kml:
                st.download_button(
                    label="📀 Tải KML",
                    data=kml,
                    file_name="converted_points.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )


with col_map:
    st.markdown("### 🗺️ Bản đồ")
    if "df" in st.session_state and {"Vĩ độ (Lat)", "Kinh độ (Lon)"}.issubset(st.session_state.df.columns):
        df_sorted = st.session_state.df.sort_values(by="Tên điểm", key=lambda col: col.map(lambda x: int(x) if str(x).isdigit() else str(x)), ascending=True).reset_index(drop=True)

        map_type = st.selectbox("Chế độ bản đồ", options=["Giao Thông", "Vệ tinh"], index=0)
        tileset = "OpenStreetMap" if map_type == "Giao Thông" else "Esri.WorldImagery"

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🔵 Nối các điểm"):
                st.session_state.join_points = not st.session_state.get("join_points", False)

        with col_btn2:
            if st.session_state.get("join_points", False):
                if st.button("📐 Tính diện tích WGS84"):
                    points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]
                    if len(points) >= 3:
                        if points[0] != points[-1]:
                            points.append(points[0])
                        poly = Geodesic.WGS84.Polygon()
                        for lat, lon in points:
                            poly.AddPoint(lat, lon)
                        num, perimeter, area = poly.Compute()
                        area = abs(area)
                        st.markdown(f"📏 Diện tích theo WGS84: {area:,.2f} m²  |  ~ {area / 10000:.2f} ha")

        with col_btn3:
            if st.button("📏 Hiện kích thước cạnh"):
                st.session_state.show_lengths = not st.session_state.get("show_lengths", False)

        m = folium.Map(location=[df_sorted.iloc[0]["Vĩ độ (Lat)"], df_sorted.iloc[0]["Kinh độ (Lon)"]], zoom_start=15, tiles=tileset)

        if st.session_state.get("join_points", False):
            points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]
            if points[0] != points[-1]:
                points.append(points[0])
            folium.PolyLine(locations=points, weight=3, color="blue", tooltip="Polygon khép kín").add_to(m)

            for i in range(len(points) - 1):
                lat1, lon1 = points[i]
                lat2, lon2 = points[i + 1]
                g = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
                dist = g['s12']
                mid_lat = (lat1 + lat2) / 2
                mid_lon = (lon1 + lon2) / 2
                angle = g['azi1']

                folium.CircleMarker(location=[lat1, lon1], radius=6, color='black', fill=True, fill_color='white', fill_opacity=1, tooltip=f"Điểm {i + 1}").add_to(m)
                folium.Marker(location=[lat1, lon1], icon=folium.DivIcon(html=f"<div style='font-size:18px;font-weight:bold;color:red'>{i+1}</div>")).add_to(m)

                if st.session_state.get("show_lengths", False):
                    offset_lat = mid_lat + 0.0001
                    offset_lon = mid_lon + 0.0001
                    folium.Marker(
                        location=[offset_lat, offset_lon],
                        icon=folium.DivIcon(html=f"""
                            <div style='transform: rotate({angle - 90:.1f}deg); transform-origin: center; font-size:14px; color:red; white-space:nowrap;'>
                                {dist:.2f} m
                            </div>"""),
                    ).add_to(m)
        else:
            for i, row in df_sorted.iterrows():
                folium.Marker(
                    location=[row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]],
                    icon=folium.Icon(icon="plus", color="red"),
                    tooltip=f"{i + 1}: {row['Tên điểm']}"
                ).add_to(m)

        st_folium(m, width="100%", height=400)

show_footer()