
import streamlit as st
from vn2000_to_wgs84_baibao import vn2000_to_wgs84_baibao

st.set_page_config(page_title="VN2000 ➜ WGS84 (chuẩn bài báo)", layout="centered")
st.title("📐 Chuyển đổi tọa độ VN2000 ➜ WGS84 (Công thức bài báo khoa học)")

st.markdown("#### 🔢 Nhập tọa độ VN-2000")

x = st.number_input("Tọa độ X (Northing)", value=1855759.3584, format="%.4f")
y = st.number_input("Tọa độ Y (Easting)", value=546151.8072, format="%.4f")
h = st.number_input("Cao độ elipsoid (H)", value=846.1115, format="%.4f")
lon0 = st.number_input("Kinh tuyến trục (VD: 106.25)", value=106.25)

if st.button("🔄 Chuyển đổi"):
    lat, lon, h_out = vn2000_to_wgs84_baibao(x, y, h, lon0)

    st.success("✅ Kết quả chuyển đổi (WGS84):")
    st.write(f"📍 Vĩ độ (Lat): `{lat}`")
    st.write(f"📍 Kinh độ (Lon): `{lon}`")
    st.write(f"📍 Cao độ elipsoid (H): `{h_out}`")
