import os
import streamlit as st
import pandas as pd
import re
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon, LineString
from PIL import Image
from functions.EdgeLengths import compute_edge_lengths

import tempfile

# --- Custom functions ---
from functions.background import set_background
from functions.parse import parse_coordinates
from functions.kml import df_to_kml
from functions.footer import show_footer
from functions.converter import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao
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

    st.markdown("""
        | STT | Định dạng nhập                            | Ghi chú                             |
        |-----|--------------------------------------------|--------------------------------------|
        | 1   | `E12345678 N56781234`                      | EN mã hiệu                           |
        | 2   | `A01 1838446.03 550074.77 37.98`           | STT X Y H                            |
        | 3   | `A01 1838446.03 550074.77`                | STT X Y _(khuyết H)_                  |
        | 4   | `1838446.03 550074.77`                    | X Y                                  |
        | 5   | `1838446.03 550074.77 37.98`              | X Y H                                |

        ✅ **Phân cách** có thể là: khoảng trắng, tab, hoặc xuống dòng.  
                """, unsafe_allow_html=True)

    selected_display = st.selectbox("🫐 Kinh tuyến trục", options=lon0_display, index=default_index)

    st.markdown("### 🔄 Chuyển đổi toạ độ")
    tab1, tab2 = st.tabs(["VN2000 ➔ WGS84", "WGS84 ➔ VN2000"])

with tab1:
    if st.button("➡️ Chuyển sang WGS84"):
        parsed, errors = parse_coordinates(coords_input)
        if parsed:
            df = pd.DataFrame(
                [(ten, *vn2000_to_wgs84_baibao(x, y, h, float(selected_display.split("–")[0].strip())
)) for ten, x, y, h in parsed],
                columns=["STT", "Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]
            )
            df["Tên điểm"] = df["STT"]
            st.session_state.df = df[["Tên điểm", "Vĩ độ (Lat)", "Kinh độ (Lon)", "H (m)"]]
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
                [(str(i+1), *wgs84_to_vn2000_baibao(lat, lon, h, float(selected_display.split("–")[0].strip()))) for i, (lat, lon, h) in enumerate(coords)],
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

# --- Output preview ---
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

        # 👉 THÊM NGAY DƯỚI ĐÂY (nằm trong col_mid)
        if st.session_state.get("join_points", False) and st.session_state.get("show_lengths", False):
            df_sorted = df.sort_values(
                by="Tên điểm",
                key=lambda col: col.map(lambda x: int(x) if str(x).isdigit() else str(x)),
                ascending=True
            ).reset_index(drop=True)
            points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]
            if points:
                df_edges = compute_edge_lengths(points)
                st.markdown("### 📏 Bảng độ dài các cạnh")
                st.dataframe(df_edges, height=250)
                st.download_button(
                    label="📤 Tải bảng độ dài cạnh (CSV)",
                    data=df_edges.to_csv(index=False).encode("utf-8"),
                    file_name="edge_lengths.csv",
                    mime="text/csv"
                )




# --- Map rendering ---
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

        m = folium.Map(
        location=[df_sorted.iloc[0]["Vĩ độ (Lat)"], df_sorted.iloc[0]["Kinh độ (Lon)"]],
        zoom_start=15,
        tiles=tileset
        )

        # === Marker dẫn đường ngay trên bản đồ ===
        first_point = df_sorted.iloc[0]
        lat = first_point["Vĩ độ (Lat)"]
        lon = first_point["Kinh độ (Lon)"]
        popup_html = f"""
        <b>{first_point['Tên điểm']}</b><br>
        <a href='https://www.google.com/maps/dir/?api=1&destination={lat},{lon}' target='_blank'>
        📍 Dẫn đường Google Maps</a>
        """

        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip="📍 Vị trí điểm đầu",
            icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
        ).add_to(m)

        # === Vẽ các điểm còn lại ===
        if st.session_state.get("join_points", False):
            points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]
            draw_polygon(m, points)
            add_numbered_markers(m, df_sorted)
            if st.session_state.get("show_lengths", False):
                add_edge_lengths(m, points)
        else:
            add_numbered_markers(m, df_sorted)

        st_folium(m, width="100%", height=400)

        # === Nút dẫn đường riêng bên dưới bản đồ ===
        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
        st.markdown(
            f"<a href='{maps_url}' target='_blank'>"
            f"<button style='padding:8px 16px; font-size:16px; background-color:#2d8cff; color:white; border:none; border-radius:5px;'>🧭 Dẫn đường Google Maps (điểm đầu)</button>"
            f"</a>",
            unsafe_allow_html=True
        )
   


# --- Footer ---
show_footer()
