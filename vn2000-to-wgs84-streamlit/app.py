import streamlit as st
import pandas as pd
import math
import re
import folium
from streamlit_folium import st_folium
import analytics  # file thống kê lượt truy cập
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao  # file thuật toán

# ✅ Cấu hình page
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")

# ✅ Ghi nhận lượt truy cập
analytics.log_visit()

# ✅ Set background
import base64  # cần import thêm

def set_background(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background("background.png")  # file nền bạn đã upload

# ✅ Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.jpg", width=90)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

# ✅ Hàm parse đầu vào
def parse_coordinates(text):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Nhận dạng kiểu mã hiệu đặc biệt: E00552071 hoặc N01839564
        if re.fullmatch(r"[EN]\d{8}", token):
            prefix = token[0]
            number = token[1:]
            if prefix == "E":
                y = int(number)
            else:
                x = int(number)

            # Tìm tiếp đối xứng nếu có
            if i+1 < len(tokens) and re.fullmatch(r"[EN]\d{8}", tokens[i+1]):
                next_prefix = tokens[i+1][0]
                next_number = tokens[i+1][1:]
                if next_prefix == "E":
                    y = int(next_number)
                else:
                    x = int(next_number)
                i += 1  # ăn thêm 1 token

            coords.append([float(x), float(y), 0])  # Gán h=0
            i += 1
            continue

        # Kiểu nhập thông thường: 1839564 552071 hoặc 1839629.224 552222.889 414.540
        chunk = []
        for _ in range(3):
            if i < len(tokens):
                try:
                    num = float(tokens[i].replace(",", "."))
                    chunk.append(num)
                except:
                    break
                i += 1
        if len(chunk) == 2:
            chunk.append(0.0)  # thiếu h thì gán h=0
        if len(chunk) == 3:
            coords.append(chunk)
        else:
            i += 1  # nhảy tới nếu không hợp lệ

    # ✅ Lọc theo điều kiện hợp lệ X, Y
    filtered = []
    for x, y, h in coords:
        if 1_000_000 <= x <= 2_000_000 and 330_000 <= y <= 670_000 and -1000 <= h <= 3200:
            filtered.append([x, y, h])
    return filtered

# ✅ Hàm export ra KML
def df_to_kml(df):
    if not {"Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"}.issubset(df.columns):
        return None
    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '  <Document>',
        '    <name>Computed Points (WGS84)</name>'
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

# ✅ Tabs
tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    st.markdown("#### 📝 Nhập toạ độ VN2000 (X Y H hoặc mã hiệu đặc biệt E/N)")
    coords_input = st.text_area("Mỗi dòng một điểm", height=180)
    if st.button("🔁 Chuyển sang WGS84"):
        parsed = parse_coordinates(coords_input)
        if parsed:
            df = pd.DataFrame(
                [vn2000_to_wgs84_baibao(x, y, h, 106.25) for x, y, h in parsed],
                columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]
            )
            st.session_state.df = df
            st.success(f"✅ Đã xử lý {len(df)} điểm.")
        else:
            st.error("⚠️ Không có dữ liệu hợp lệ!")

with tab2:
    st.markdown("#### 📝 Nhập toạ độ WGS84 (Lat Lon H)")
    coords_input = st.text_area("Mỗi dòng một điểm", height=180, key="wgs84input")
    if st.button("🔁 Chuyển sang VN2000"):
        tokens = re.split(r'\s+', coords_input.strip())
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
                [wgs84_to_vn2000_baibao(lat, lon, h, 106.25) for lat, lon, h in coords],
                columns=["X (m)", "Y (m)", "h (m)"]
            )
            st.session_state.df = df
            st.success(f"✅ Đã xử lý {len(df)} điểm.")
        else:
            st.error("⚠️ Không có dữ liệu hợp lệ!")

# ✅ Hiển thị kết quả
if "df" in st.session_state:
    df = st.session_state.df
    st.markdown("### 📊 Kết quả")
    st.dataframe(df)

    if {"Vĩ độ (Lat)", "Kinh độ (Lon)"}.issubset(df.columns):
        st.markdown("### 🌍 Bản đồ vệ tinh")
        m = folium.Map(
            location=[df["Vĩ độ (Lat)"].mean(), df["Kinh độ (Lon)"].mean()],
            zoom_start=14,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri.WorldImagery"
        )
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]],
                radius=3,
                color="red",
                fill=True,
                fill_opacity=0.7
            ).add_to(m)
        st_folium(m, width="100%", height=550)

        # Xuất file KML
        kml = df_to_kml(df)
        if kml:
            st.download_button(
                label="📥 Tải xuống file KML",
                data=kml,
                file_name="converted_points.kml",
                mime="application/vnd.google-earth.kml+xml"
            )

# ✅ Footer
st.markdown("---")
st.markdown(
    "📌 Tác giả: **Trần Trường Sinh**  \n"
    "📞 0917.750.555"
)
st.markdown(
    "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ TRONG CÔNG NGHỆ MÁY BAY KHÔNG NGƯỜI LÁI CÓ ĐỊNH VỊ TÂM CHỤP CHÍNH XÁC**  \n"
    "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
    "¹ Đại học Mỏ - Địa chất, ² Công ty CP Xây dựng và TM QT Miền Bắc  \n"
    "_Hội nghị KH Quốc gia về Công nghệ Địa không gian_"
) 