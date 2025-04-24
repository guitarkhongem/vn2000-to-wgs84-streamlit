import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import re
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

# Cấu hình trang
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")

# 1) Nhúng Google My Maps (Google Earth) làm nền
st.markdown("## Bản đồ nền Google Earth/My Maps")
map_url = (
    "https://www.google.com/maps/d/embed?"
    "mid=1gHTIagvnAKWB66oVKHlkAlpHyra8UF8"
    "&ll=16.70561447553423%2C106.67600750000003"
    "&z=10"
)
components.iframe(map_url, width=800, height=450)

# 2) Logo và tiêu đề đơn vị
col1, col2 = st.columns([1, 5], gap="small")
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# 3) Hàm parse đầu vào (hỗ trợ space/tab/newline & STT dạng số hoặc ký tự)
def parse_coordinates(text, group=3):
    """
    Chia mọi token space/tab/newline thành nhóm `group` float.
    Bỏ qua token STT nếu:
     - chứa ký tự chữ (A10, PT01…)
     - hoặc là số nguyên không chứa '.' khi đứng trước đủ group+1 token
    """
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i + group <= len(tokens):
        t0 = tokens[i]
        # Skip STT chứa chữ hoặc số nguyên (no dot) với đủ group+1 token
        if (re.search(r'[A-Za-z]', t0) 
            or ('.' not in t0 and re.fullmatch(r'\d+', t0) and len(tokens)-i >= group+1)):
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

# 4) Hàm xuất KML cho các điểm tính được
def df_to_kml(df):
    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '  <Document>',
        '    <name>Computed Points</name>'
    ]
    for idx, row in df.iterrows():
        kml += [
            '    <Placemark>',
            f'      <name>Point {idx+1}</name>',
            '      <Point>',
            f'        <coordinates>{row["Kinh độ (Lon)"]},{row["Vĩ độ (Lat)"]},{row["H (m)"]}</coordinates>',
            '      </Point>',
            '    </Placemark>'
        ]
    kml += ['  </Document>', '</kml>']
    return "\n".join(kml)

# 5) Giao diện chuyển đổi
tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    st.markdown("#### 🔢 Nhập tọa độ VN2000 (X Y Z – space/tab/newline hoặc kèm STT):")
    in_vn = st.text_area("", height=120, key="vn_in")
    lon0_vn = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_vn")
    if st.button("🔁 Chuyển WGS84"):
        parsed = parse_coordinates(in_vn, group=3)
        results = [vn2000_to_wgs84_baibao(x, y, z, lon0_vn) for x, y, z in parsed]
        if results:
            df = pd.DataFrame(results, columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")

with tab2:
    st.markdown("#### 🔢 Nhập tọa độ WGS84 (Lat Lon H – space/tab/newline hoặc kèm STT):")
    in_wg = st.text_area("", height=120, key="wg_in")
    lon0_wg = st.number_input("🌐 Kinh tuyến trục (°)", value=106.25, format="%.4f", key="lon0_wg")
    if st.button("🔁 Chuyển VN2000"):
        parsed = parse_coordinates(in_wg, group=3)
        results = [wgs84_to_vn2000_baibao(lat, lon, h, lon0_wg) for lat, lon, h in parsed]
        if results:
            df = pd.DataFrame(results, columns=["X (m)", "Y (m)", "h (m)"])
            st.session_state.df = df
            st.dataframe(df)
        else:
            st.warning("⚠️ Không có dữ liệu hợp lệ (cần 3 số mỗi bộ).")

# 6) Khi đã có kết quả, cho phép xuất KML và hiển thị biểu đồ nhỏ
if "df" in st.session_state:
    df = st.session_state.df
    st.markdown("### 📥 Xuất file KML tọa độ tính được")
    kml_str = df_to_kml(df)
    st.download_button(
        label="Tải xuống KML (computed_points.kml)",
        data=kml_str,
        file_name="computed_points.kml",
        mime="application/vnd.google-earth.kml+xml"
    )
    # Nếu muốn xem tạm trên Folium (tùy chọn)
    with st.expander("🔍 Xem nhanh trên bản đồ Folium"):
        import folium
        from streamlit_folium import st_folium
        center_lat = float(df["Vĩ độ (Lat)"].mean())
        center_lon = float(df["Kinh độ (Lon)"].mean())
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri.WorldImagery"
        )
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]],
                radius=3, color="red", fill=True, fill_opacity=0.7
            ).add_to(m)
        st_folium(m, width=700, height=400)

# 7) Chân trang
st.markdown("---")
st.markdown(
    "Tác giả: Trần Trường Sinh  \n"
    "Số điện thoại: 0917.750.555"
)
st.markdown(
    "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ…**  \n"
    "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
    "¹ Trường Đại học Mỏ - Địa chất  \n"
    "² Công ty CP Xây dựng và Thương mại QT Miền Bắc  \n"
    "_HỘI NGHỊ KHOA HỌC QUỐC GIA VỀ CÔNG NGHỆ ĐỊA KHÔNG GIAN TRONG KHOA HỌC TRÁI ĐẤT VÀ MÔI TRƯỜNG_"
)
