import streamlit as st
import pandas as pd
from pyproj import CRS, Transformer

# Bảng kinh tuyến trục cho 63 tỉnh/thành
province_central_meridian = {
    "Lai Châu": 103.0, "Điện Biên": 103.0, "Sơn La": 104.0, "Lào Cai": 104.75,
    "Yên Bái": 104.75, "Hà Giang": 105.5, "Tuyên Quang": 106.0, "Phú Thọ": 104.75,
    "Vĩnh Phúc": 105.0, "Cao Bằng": 105.75, "Lạng Sơn": 107.25, "Bắc Kạn": 106.5,
    "Thái Nguyên": 106.5, "Bắc Giang": 107.0, "Bắc Ninh": 105.5, "Quảng Ninh": 107.75,
    "TP. Hải Phòng": 105.75, "Hải Dương": 105.5, "Hưng Yên": 105.5, "TP. Hà Nội": 105.0,
    "Hòa Bình": 106.0, "Hà Nam": 105.0, "Nam Định": 105.5, "Thái Bình": 105.5,
    "Ninh Bình": 105.0, "Thanh Hóa": 105.0, "Nghệ An": 104.75, "Hà Tĩnh": 105.5,
    "Quảng Bình": 106.0, "Quảng Trị": 106.25, "Thừa Thiên – Huế": 107.0, "TP. Đà Nẵng": 107.75,
    "Quảng Nam": 107.75, "Quảng Ngãi": 108.0, "Bình Định": 108.25, "Kon Tum": 107.5,
    "Gia Lai": 108.5, "Đắk Lắk": 108.5, "Đắk Nông": 108.5, "Phú Yên": 108.5,
    "Khánh Hòa": 108.25, "Ninh Thuận": 108.25, "Bình Thuận": 108.5, "Lâm Đồng": 107.75,
    "Bình Dương": 105.75, "Bình Phước": 106.25, "Đồng Nai": 107.75, "Bà Rịa – Vũng Tàu": 107.75,
    "Tây Ninh": 105.5, "Long An": 105.75, "Tiền Giang": 105.75, "Bến Tre": 105.75,
    "Đồng Tháp": 105.0, "Vĩnh Long": 105.5, "Trà Vinh": 105.5, "An Giang": 104.75,
    "Kiên Giang": 104.5, "TP. Cần Thơ": 105.0, "Hậu Giang": 105.0, "Sóc Trăng": 105.5,
    "Bạc Liêu": 105.0, "Cà Mau": 104.5, "TP. Hồ Chí Minh": 105.75
}

st.set_page_config(page_title="Chuyển đổi VN-2000 sang WGS84", layout="centered")
st.title("🛰️ Chuyển đổi tọa độ VN-2000 ➜ WGS84 (có cao độ Z)")

# Hàm chuyển đổi 3D an toàn
def convert_vn2000_to_wgs84(x, y, z, central_meridian):
    try:
        proj_string = (
            f"+proj=tmerc +lat_0=0 +lon_0={central_meridian} "
            "+k=0.9999 +x_0=500000 +y_0=0 "
            "+ellps=WGS84 +towgs84=-191.9,-39.3,-111.5,"
            "0.0093,-0.0198,0.0043,0.2529 +units=m +no_defs"
        )
        crs_vn2000 = CRS.from_string(proj_string)
        crs_wgs84 = CRS.from_epsg(4979)  # WGS84 + cao độ
        transformer = Transformer.from_crs(crs_vn2000, crs_wgs84, always_xy=True)
        lon, lat, h = transformer.transform(x, y, z)
        return lat, lon, h
    except Exception as e:
        st.error(f"Lỗi chuyển đổi: {e}")
        return None, None, None

# === Nhập tay ===
st.subheader("🔢 Nhập tọa độ X, Y, Z")
x = st.number_input("Tọa độ X (m)", format="%.3f")
y = st.number_input("Tọa độ Y (m)", format="%.3f")
z = st.number_input("Cao độ Z (m)", format="%.2f", value=0.0)
province = st.selectbox("Chọn tỉnh/thành", list(province_central_meridian.keys()))
lon0 = province_central_meridian[province]

if st.button("📍 Chuyển đổi"):
    lat, lon, h = convert_vn2000_to_wgs84(x, y, z, lon0)
    if lat is not None:
        st.success(f"✅ Kết quả:\n- Lat = {lat:.6f}\n- Lon = {lon:.6f}\n- Cao độ = {h:.2f} m")

# === Nhập file CSV ===
st.markdown("---")
st.subheader("📤 Chuyển đổi từ file CSV (X, Y, Z)")

uploaded_file = st.file_uploader("Tải lên file .csv chứa X, Y, Z", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ["X", "Y", "Z"]):
        st.error("❌ File phải có 3 cột: X, Y, Z")
    else:
        prov_batch = st.selectbox("Tỉnh áp dụng cho toàn bộ điểm", list(province_central_meridian.keys()), key="prov_batch")
        lon0_batch = province_central_meridian[prov_batch]

        df = df.dropna(subset=["X", "Y", "Z"])
        df["Lat"], df["Lon"], df["H"] = zip(*df.apply(
            lambda row: convert_vn2000_to_wgs84(row["X"], row["Y"], row["Z"], lon0_batch), axis=1
        ))
        st.success("✅ Đã chuyển đổi!")
        st.dataframe(df)

        st.download_button(
            "⬇️ Tải kết quả CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="converted_wgs84.csv",
            mime="text/csv"
        )
