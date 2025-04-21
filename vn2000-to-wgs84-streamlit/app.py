import streamlit as st
import pandas as pd
from pyproj import CRS, Transformer

# Kinh tuyến trục theo tỉnh/thành (chuẩn TM3 - múi 3°)
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

st.set_page_config(page_title="Chuyển VN-2000 ➜ WGS84", layout="centered")
st.title("🛰️ Chuyển đổi tọa độ VN-2000 ➜ WGS84 (chuẩn TM3 + hỗ trợ cao độ Z)")

# Hàm chuyển đổi
def convert_vn2000_to_wgs84(x, y, z, lon0, use_towgs84=False):
    try:
        towgs84 = "-191.90441429,-39.30318279,-111.45032835,-0.00928836,0.01975479,-0.00427372,0.252906278"
        towgs84_str = f"+towgs84={towgs84} " if use_towgs84 else ""
        proj_string = (
            f"+proj=tmerc +lat_0=0 +lon_0={lon0} "
            "+k=0.9999 +x_0=500000 +y_0=0 "
            "+ellps=WGS84 " +
            towgs84_str +
            "+units=m +no_defs"
        )
        crs_vn2000 = CRS.from_string(proj_string)
        crs_wgs84 = CRS.from_epsg(4979)  # WGS84 + cao độ
        transformer = Transformer.from_crs(crs_vn2000, crs_wgs84, always_xy=True)
        lon, lat, h = transformer.transform(x, y, z)
        return lat, lon, h
    except Exception as e:
        st.error(f"Lỗi chuyển đổi: {e}")
        return None, None, None

# --- Nhập tay ---
st.subheader("🔢 Nhập tọa độ thủ công")
col1, col2, col3 = st.columns(3)
x = col1.number_input("X (m)", format="%.3f")
y = col2.number_input("Y (m)", format="%.3f")
z = col3.number_input("Z (m - cao độ)", format="%.2f", value=0.0)

province = st.selectbox("Chọn tỉnh/tỉnh thành", list(province_central_meridian.keys()))
lon0 = province_central_meridian[province]
use_towgs84 = st.checkbox("Áp dụng bộ 7 tham số (+towgs84)", value=False)

if st.button("📍 Chuyển đổi"):
    lat, lon, h = convert_vn2000_to_wgs84(x, y, z, lon0, use_towgs84)
    if lat is not None:
        st.success(f"""✅ Kết quả:
        • Vĩ độ (Lat): {lat:.6f}
        • Kinh độ (Lon): {lon:.6f}
        • Cao độ (WGS84): {h:.2f} m
        """)

# --- Nhập file CSV ---
st.markdown("---")
st.subheader("📤 Chuyển đổi từ file .csv có cột X, Y, Z")

uploaded_file = st.file_uploader("Tải file .csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ["X", "Y", "Z"]):
        st.error("❌ File phải chứa đủ 3 cột: X, Y, Z")
    else:
        province_batch = st.selectbox("Tỉnh áp dụng cho toàn bộ dữ liệu", list(province_central_meridian.keys()), key="prov_batch")
        lon0_batch = province_central_meridian[province_batch]
        use_towgs84_batch = st.checkbox("Áp dụng +towgs84 cho toàn bộ dữ liệu", value=False, key="towgs84_batch")

        df = df.dropna(subset=["X", "Y", "Z"])
        df["Lat"], df["Lon"], df["H"] = zip(*df.apply(
            lambda row: convert_vn2000_to_wgs84(row["X"], row["Y"], row["Z"], lon0_batch, use_towgs84_batch),
            axis=1
        ))
        st.success("✅ Chuyển đổi hoàn tất")
        st.dataframe(df)
        st.download_button("⬇️ Tải kết quả CSV", df.to_csv(index=False).encode("utf-8"), file_name="vn2000_to_wgs84.csv")
