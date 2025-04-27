import streamlit as st
import pandas as pd
import folium
import re
import base64
import io
from streamlit_folium import st_folium
import analytics
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao

# --- Bảng kinh tuyến trục theo tỉnh (gom nhóm) ---
province_lon0 = {
    "104.5": ["Kiên Giang", "Cà Mau"],
    "104.75": ["Lào Cai", "Phú Thọ", "Nghệ An", "An Giang"],
    "105.0": ["Vĩnh Phúc", "Hà Nam", "Ninh Bình", "Thanh Hóa", "Đồng Tháp", "TP. Cần Thơ", "Hậu Giang", "Bạc Liêu"],
    "105.5": ["Hà Giang", "Bắc Ninh", "Hải Dương", "Hưng Yên", "Nam Định", "Thái Bình", "Hà Tĩnh", "Tây Ninh", "Vĩnh Long", "Trà Vinh"],
    "105.75": ["TP. Hải Phòng", "Bình Dương", "Long An", "Tiền Giang", "Bến Tre", "TP. Hồ Chí Minh"],
    "106.0": ["Tuyên Quang", "Hòa Bình", "Quảng Bình"],
    "106.25": ["Quảng Trị", "Bình Phước"],
    "106.5": ["Bắc Kạn", "Thái Nguyên"],
    "107.0": ["Bắc Giang", "Thừa Thiên – Huế"],
    "107.25": ["Lạng Sơn"],
    "107.5": ["Kon Tum"],
    "107.75": ["TP. Đà Nẵng", "Quảng Nam", "Đồng Nai", "Bà Rịa – Vũng Tàu"],
    "107.75": ["Quảng Nam", "TP. Đà Nẵng"],
    "108.0": ["Quảng Ngãi"],
    "108.25": ["Bình Định", "Khánh Hòa", "Ninh Thuận"],
    "108.5": ["Gia Lai", "Đắk Lắk", "Đắk Nông", "Phú Yên", "Bình Thuận"],
    "108.5": ["Gia Lai", "Đắk Lắk", "Đắk Nông", "Phú Yên", "Bình Thuận"],
    "107.75": ["Lâm Đồng"],
}

# --- Các hàm ---
def set_background(png_file):
    with open(png_file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
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

def parse_coordinates(text):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    stt_list = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if re.fullmatch(r"[EN]\d{8}", token):
            prefix = token[0]
            number = token[1:]
            if prefix == "E":
                y = int(number)
            else:
                x = int(number)
            if i+1 < len(tokens) and re.fullmatch(r"[EN]\d{8}", tokens[i+1]):
                next_prefix = tokens[i+1][0]
                next_number = tokens[i+1][1:]
                if next_prefix == "E":
                    y = int(next_number)
                else:
                    x = int(next_number)
                i += 1
            coords.append(["", x, y, 0])
            i += 1
            continue

        # Nhận STT
        if not re.fullmatch(r"\d+(\.\d+)?", token):
            stt = token
            i += 1
        else:
            stt = ""

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
            coords.append([stt] + chunk)
        else:
            i += 1

    filtered = []
    for stt, x, y, h in coords:
        if 1_000_000 <= x <= 2_000_000 and 330_000 <= y <= 670_000:
            filtered.append([stt, x, y, h])
    return filtered

def df_to_kml(df):
    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '  <Document>',
        '    <name>Converted Points</name>'
    ]
    for idx, row in df.iterrows():
        kml += [
            '    <Placemark>',
            f'      <name>Point {row["STT"] if row["STT"] else idx+1}</name>',
            '      <Point>',
            f'        <coordinates>{row["Kinh độ (Lon)"]},{row["Vĩ độ (Lat)"]},{row["H (m)"]}</coordinates>',
            '      </Point>',
            '    </Placemark>'
        ]
    kml.append('  </Document>')
    kml.append('</kml>')
    return "\n".join(kml)

# --- Main App ---
st.set_page_config(page_title="VN2000 ⇄ WGS84 Converter", layout="wide")
analytics.log_visit()
set_background("background.png")

col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.jpg", width=90)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

province = st.selectbox("Chọn tỉnh để tự động chọn kinh tuyến trục", sorted(set(sum(province_lon0.values(), []))))
lon0 = float(next(k for k, v in province_lon0.items() if province in v))

uploaded_file = st.file_uploader("📂 Tải file TXT/CSV toạ độ", type=["txt", "csv"])

tab1, tab2 = st.tabs(["➡️ VN2000 → WGS84", "⬅️ WGS84 → VN2000"])

with tab1:
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")
    else:
        text = st.text_area("🔢 Nhập tọa độ", height=200)

    if st.button("🔁 Chuyển sang WGS84"):
        parsed = parse_coordinates(text)
        if parsed:
            df = pd.DataFrame(
                [vn2000_to_wgs84_baibao(x, y, h, lon0) for _, x, y, h in parsed],
                columns=["Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]
            )
            df.insert(0, "STT", [stt for stt, _, _, _ in parsed])
            st.dataframe(df)

            m = folium.Map(location=[df["Vĩ độ (Lat)"].mean(), df["Kinh độ (Lon)"].mean()], zoom_start=15,
                           tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                           attr="Esri")
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]),
                    radius=3,
                    color="red",
                    fill=True,
                    fill_opacity=0.7
                ).add_to(m)
            st_folium(m, width=800, height=500)

            st.download_button("📥 Tải file KML", df_to_kml(df), file_name="converted.kml", mime="application/vnd.google-earth.kml+xml")
        else:
            st.error("⚠️ Không có dữ liệu hợp lệ!")

with tab2:
    st.warning("🚧 Chức năng này mình sẽ hoàn thiện nốt sau!")


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
