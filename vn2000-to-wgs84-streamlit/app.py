
import streamlit as st
from vn2000_to_wgs84_noisuy import vn2000_to_wgs84_nnoisuy

st.set_page_config(page_title="Chuyển đổi VN2000 → WGS84 (nội suy)", layout="centered")
st.title("🛰️ Chuyển đổi VN2000 → WGS84 theo phương pháp nội suy")

st.markdown("### 📥 Nhập tọa độ VN2000 và điểm tham chiếu WGS84")

col1, col2 = st.columns(2)

with col1:
    x = st.number_input("Tọa độ X (Northing)", value=1855759.3584, step=0.0001)
    y = st.number_input("Tọa độ Y (Easting)", value=546151.8072, step=0.0001)
    h_vn = st.number_input("Cao độ elipsoid (VN2000)", value=846.1115, step=0.0001)
    lon0 = st.number_input("Kinh tuyến trục (độ)", value=106.25)

with col2:
    ref_lat = st.number_input("Lat tham chiếu (độ)", value=16.77839862)
    ref_lon = st.number_input("Lon tham chiếu (độ)", value=106.6847777)
    ref_h = st.number_input("Cao độ tham chiếu (WGS84)", value=832.2537252)

if st.button("🔄 Chuyển đổi"):
    lat, lon, h, diff = vn2000_to_wgs84_nnoisuy(x, y, h_vn, lon0, ref_lat, ref_lon, ref_h)

    st.success("✅ Kết quả chuyển đổi (WGS84):")
    st.write(f"📍 Vĩ độ (Lat): `{lat}`")
    st.write(f"📍 Kinh độ (Lon): `{lon}`")
    st.write(f"📍 Cao độ elipsoid: `{h} m`")

    st.markdown("---")
    st.write("📏 **Sai số so với điểm tham chiếu thực tế:**")
    st.write(f"- ΔLat: `{diff[0]}` độ")
    st.write(f"- ΔLon: `{diff[1]}` độ")
    st.write(f"- Δh: `{diff[2]} m`")
