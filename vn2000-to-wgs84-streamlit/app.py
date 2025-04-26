import streamlit as st
import pandas as pd
import math
import re
import folium
from streamlit_folium import st_folium
from functions import vn2000_to_wgs84_baibao
import analytics

# Set page config
st.set_page_config(page_title="VN2000 ⇄ WGS84", layout="wide")

conn, c = analytics.init_db()
analytics.log_visit(c, conn)

# Giao diện
col1, col2 = st.columns([1,5])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("VN2000 ⇄ WGS84 Converter")
    st.markdown("### BẤT ĐỘNG SẢN HUYỆN HƯỚNG HÓA")

def parse_coordinates(text):
    tokens = re.split(r'\s+', text.strip())
    coords = []
    i = 0
    while i < len(tokens):
        t0 = tokens[i]
        # Nếu chứa chữ hoặc là số dạng E00552071 thì tách
        if re.match(r'^[A-Za-z]+(\d+)$', t0):
            number = re.findall(r'\d+', t0)[0]
            coords.append(int(number))
            i += 1
            continue
        try:
            val = float(t0.replace(",", "."))
            coords.append(val)
            i += 1
        except:
            i += 1

    result = []
    i = 0
    while i + 1 < len(coords):
        x = coords[i]
        y = coords[i+1]
        h = coords[i+2] if i+2 < len(coords) else 0
        if 1e6 < x < 2e6 and 330000 < y < 670000 and -1000 < h < 3200:
            result.append((x, y, h))
        i += 3
    return result

st.subheader("🔢 Nhập tọa độ (space, tab hoặc enter):")
text_input = st.text_area("", height=250)
if st.button("🛰️ Chuyển đổi"):
    parsed = parse_coordinates(text_input)
    if parsed:
        df = pd.DataFrame([vn2000_to_wgs84_baibao(x, y, h, 106.25) for x, y, h in parsed],
                          columns=["Vĩ độ (Lat)", "Kinh độ (Lon)"])
        st.success("🎯 Kết quả:")
        st.dataframe(df)

        # Map
        m = folium.Map(
            location=[df["Vĩ độ (Lat)"].mean(), df["Kinh độ (Lon)"].mean()],
            zoom_start=14,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri.WorldImagery"
        )
        for _, row in df.iterrows():
            folium.CircleMarker(location=(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]),
                                radius=3, color="red", fill=True, fill_opacity=0.7).add_to(m)
        st_folium(m, width=900, height=600)
    else:
        st.warning("⚠️ Không có dữ liệu hợp lệ!")

# Sidebar
visits, likes = analytics.get_stats(c)
st.sidebar.markdown(f"👁️ Lượt xem: **{visits}**")
st.sidebar.markdown(f"❤️ Lượt thích: **{likes}**")
if st.sidebar.button("👍 Thích ứng dụng"):
    analytics.increment_like(c, conn)
    st.experimental_rerun()

st.markdown("---")
st.markdown("Tác giả: **Trần Trường Sinh** | 📞 0917.750.555")


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
