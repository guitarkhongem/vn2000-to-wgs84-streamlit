import streamlit as st
import pandas as pd
from pyproj import Transformer

st.set_page_config(page_title="Chuyển đổi VN-2000 sang WGS84", layout="centered")
st.title("🛰️ Chuyển đổi tọa độ VN-2000 ➜ WGS84")

# Hàm chuyển đổi VN-2000 ➜ WGS84
def convert_vn2000_to_wgs84(x, y, central_meridian):
    proj_vn2000 = f"+proj=tmerc +lat_0=0 +lon_0={central_meridian} +k=0.9999 +x_0=500000 +y_0=0 " \
                  "+ellps=WGS84 +towgs84=-191.9,-39.3,-111.5,0.0093,-0.0198,0.0043,0.2529 +units=m +no_defs"
    transformer = Transformer.from_pipeline(f"+proj=pipeline +step {proj_vn2000} +step +proj=unitconvert +xy_in=m +xy_out=deg")
    lon, lat = transformer.transform(x, y)
    return lat, lon

# --- Nhập liệu tay ---
st.subheader("🔢 Nhập tọa độ thủ công")
x = st.number_input("Tọa độ X (m)", format="%.3f")
y = st.number_input("Tọa độ Y (m)", format="%.3f")
lon0 = st.selectbox("Chọn kinh tuyến trục (múi 3°)", [102, 103, 104, 105, 106, 107, 108], index=3)

if st.button("📍 Chuyển đổi"):
    lat, lon = convert_vn2000_to_wgs84(x, y, lon0)
    st.success(f"Tọa độ WGS84:\n- Lat = {lat:.6f}\n- Lon = {lon:.6f}")

# --- Tải lên file dữ liệu ---
st.markdown("---")
st.subheader("📤 Chuyển đổi hàng loạt từ file CSV")
uploaded_file = st.file_uploader("Tải lên file .csv chứa cột X, Y", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if "X" not in df.columns or "Y" not in df.columns:
        st.error("❌ File phải có cột 'X' và 'Y'")
    else:
        lon0_batch = st.selectbox("Chọn kinh tuyến trục cho tất cả điểm", [102, 103, 104, 105, 106, 107, 108], index=3)
        df["Lat"], df["Lon"] = zip(*df.apply(lambda row: convert_vn2000_to_wgs84(row["X"], row["Y"], lon0_batch), axis=1))
        st.success("✅ Chuyển đổi thành công!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Tải kết quả CSV", data=csv, file_name="vn2000_to_wgs84_result.csv", mime="text/csv")
