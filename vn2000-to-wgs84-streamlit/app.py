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
import re

def parse_coordinates(text):
    """
    Parse đầu vào thành list (x, y, h).
    Hỗ trợ:
    - STT, mã hiệu sẽ tự bỏ qua.
    - Nếu thiếu h thì gán h = 0.
    - Kiểm soát x, y hợp lệ.
    """
    tokens = re.split(r'[\s\t\n]+', text.strip())  # Chia space/tab/newline
    coords = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Nếu token có chữ (E00552071, N01839564) thì lọc số ra
        if re.search(r'[A-Za-z]', token):
            nums = re.findall(r'\d+', token)
            if nums:
                token = nums[0]
            else:
                i += 1
                continue

        try:
            num = float(token)
        except ValueError:
            i += 1
            continue

        # Phải có ít nhất 2 số liên tiếp (X, Y)
        if i+1 < len(tokens):
            next_token = tokens[i+1]

            if re.search(r'[A-Za-z]', next_token):
                nums = re.findall(r'\d+', next_token)
                if nums:
                    next_token = nums[0]

            try:
                num2 = float(next_token)
            except ValueError:
                i += 1
                continue

            x, y = num, num2
            h = 0  # Default

            # Có H hay không
            if i+2 < len(tokens):
                next_next_token = tokens[i+2]
                if re.search(r'[A-Za-z]', next_next_token):
                    nums = re.findall(r'\d+', next_next_token)
                    if nums:
                        next_next_token = nums[0]

                try:
                    h = float(next_next_token)
                    i += 3  # X Y H
                except ValueError:
                    i += 2  # X Y (không có H)
            else:
                i += 2

            # Kiểm soát X, Y hợp lệ
            if 1000000 <= x <= 2000000 and 330000 <= y <= 670000:
                coords.append((x, y, h))

        else:
            i += 1

    return coords


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
