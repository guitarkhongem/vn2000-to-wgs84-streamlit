import streamlit as st
import pandas as pd
from pyproj import Transformer

# Bảng kinh tuyến trục theo tỉnh/thành phố
province_central_meridian = {
    "Hà Nội": 105.0,
    "TP. Hồ Chí Minh": 105.75,
    "Quảng Trị": 106.25,
    "Đà Nẵng": 107.75,
    "Cà Mau": 104.5,
    # ... (bạn có thể thêm đầy đủ 63 tỉnh như phần trước)
}

st.set_page_config(page_title="Chuyển đổi VN-2000 sang WGS84", layout="centered")
st.title("🛰️ Chuyển đổi tọa độ VN-2000 ➜ WGS84 (3D)")

# Chuyển đổi VN-2000 sang WGS84, có Z
def convert_vn2000_to_wgs84(x, y, z, central_meridian):
    proj_vn2000 = f"+proj=tmerc +lat_0=0 +lon_0={central_meridian} +k=0.9999 +x_0=500000 +y_0=0 " \
                  "+ellps=WGS84 +towgs84=-191.9,-39.3,-111.5,0.0093,-0.0198,0.0043,0.2529 +units=m +no_defs"
    transformer = Transformer.from_pipeline(
        f"+proj=pipeline +step {proj_vn2000} +step +proj=unitconvert +xy_in=m +xy_out=deg"
    )
    lon, lat, h = transformer.transform(x, y, z)
    return lat, lon, h

# --- Nhập liệu tay ---
st.subheader("🔢 Nhập tọa độ X, Y, Z thủ công")
x = st.number_input("Tọa độ X (m)", format="%.3f")
y = st.number_input("Tọa độ Y (m)", format="%.3f")
z = st.number_input("Cao độ Z (m)", format="%.2f", value=0.0)
province = st.selectbox("Chọn tỉnh/thành phố", list(province_central_meridian.keys()))
lon0 = province_central_meridian[province]

if st.button("📍 Chuyển đổi"):
    lat, lon, h = convert_vn2000_to_wgs84(x, y, z, lon0)
    st.success(f"""
    ✅ Kết quả chuyển đổi:
    - Lat = {lat:.6f}
    - Lon = {lon:.6f}
    - Cao độ WGS84 = {h:.2f} m
    """)

# --- Tải lên file dữ liệu ---
st.markdown("---")
st.subheader("📤 Chuyển đổi hàng loạt từ file CSV (có X, Y, Z)")
uploaded_file = st.file_uploader("Tải lên file .csv chứa cột X, Y, Z", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ["X", "Y", "Z"]):
        st.error("❌ File phải có đủ cột: 'X', 'Y', 'Z'")
    else:
        province_batch = st.selectbox("Chọn tỉnh/thành phố cho toàn bộ điểm", list(province_central_meridian.keys()), key="prov_batch")
        lon0_batch = province_central_meridian[province_batch]
        df["Lat"], df["Lon"], df["H"] = zip(*df.apply(lambda row: convert_vn2000_to_wgs84(row["X"], row["Y"], row["Z"], lon0_batch), axis=1))
        st.success("✅ Chuyển đổi thành công!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Tải kết quả CSV", data=csv, file_name="converted_wgs84_3D.csv", mime="text/csv")
