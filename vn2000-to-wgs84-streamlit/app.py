import streamlit as st
import folium
from folium.features import Kml
import tempfile
from streamlit_folium import st_folium

def render_map(df, kml_file=None):
    """
    Hiển thị bản đồ vệ tinh Esri + overlay KML (nếu có) + điểm nhỏ.
    """
    if df is None or df.empty:
        st.warning("⚠️ Không có dữ liệu để hiển thị bản đồ.")
        return

    # Chuẩn hóa tên cột lat/lon
    lat_col = "Vĩ độ (Lat)" if "Vĩ độ (Lat)" in df.columns else "latitude"
    lon_col = "Kinh độ (Lon)" if "Kinh độ (Lon)" in df.columns else "longitude"
    df_map = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})

    # Tọa độ trung tâm
    center_lat = float(df_map["latitude"].mean())
    center_lon = float(df_map["longitude"].mean())

    # Tạo map nền vệ tinh Esri
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri.WorldImagery"
    )

    # Overlay file KML nếu có
    if kml_file is not None:
        tmp = tempfile.NamedTemporaryFile(suffix=".kml", delete=False)
        tmp.write(kml_file.getvalue())
        tmp.flush()
        # Dùng Kml từ folium.features
        Kml(tmp.name, name="Overlay").add_to(m)
        folium.LayerControl().add_to(m)

    # Vẽ các điểm nhỏ
    for _, row in df_map.iterrows():
        folium.CircleMarker(
            location=(row["latitude"], row["longitude"]),
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    # Hiển thị
    st_folium(m, width=700, height=500)
