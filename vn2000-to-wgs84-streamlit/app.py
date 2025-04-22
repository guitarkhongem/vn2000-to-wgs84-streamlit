import streamlit as st
import math

# --- Hằng số ellipsoid WGS-84 ---
a = 6378137.0
f = 1 / 298.257223563
e2 = 2 * f - f ** 2
e4 = e2 ** 2
e6 = e2 ** 3

# --- Các hệ số chuỗi TM3 ---
A0 = 1 - (e2 / 4) - (3 * e4 / 64) - (5 * e6 / 256)
A2 = (3 / 8) * (e2 + (e4 / 4) + (15 * e6 / 128))
A4 = (15 / 256) * (e4 + (3 * e6 / 4))
A6 = (35 * e6) / 3072

# --- Bảng kinh tuyến trục theo tỉnh ---
province_lon0 = {
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


# --- Mô hình độ cao Geoid trung bình theo địa phương (có thể mở rộng sau) ---
geoid_height_by_province = {
    "Thanh Hóa": 20.947,
    "Hà Nội": 20.0,
    "Quảng Trị": 18.0,
    "TP. Hồ Chí Minh": 17.0,
    "Đà Nẵng": 19.5,
    # Tạm ước lượng, có thể thay bằng mô hình EGM sau
}

# --- Thuật toán nghịch TM3 ---
def inverse_tm3(x, y, lon0_deg, k0=0.9999, x0=0, y0=500000):
    M = (x - x0) / k0
    mu = M / (a * A0)
    phi1 = mu + A2 * math.sin(2 * mu) + A4 * math.sin(4 * mu) + A6 * math.sin(6 * mu)
    e1sq = e2 / (1 - e2)
    C1 = e1sq * math.cos(phi1) ** 2
    T1 = math.tan(phi1) ** 2
    N1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    R1 = N1 * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2)
    D = (y - y0) / (N1 * k0)
    lat = phi1 - (N1 * math.tan(phi1) / R1) * (
        (D ** 2) / 2 -
        (5 + 3 * T1 + 10 * C1 - 4 * C1 ** 2 - 9 * e1sq) * D ** 4 / 24 +
        (61 + 90 * T1 + 298 * C1 + 45 * T1 ** 2 - 252 * e1sq - 3 * C1 ** 2) * D ** 6 / 720
    )
    lon0 = math.radians(lon0_deg)
    lon = lon0 + (
        D -
        (1 + 2 * T1 + C1) * D ** 3 / 6 +
        (5 - 2 * C1 + 28 * T1 - 3 * C1 ** 2 + 8 * e1sq + 24 * T1 ** 2) * D ** 5 / 120
    ) / math.cos(phi1)
    return round(math.degrees(lat), 15), round(math.degrees(lon), 15)

# --- Hàm tính h (cao độ elipsoid) ---
def convert_height_geoid_to_ellipsoid(H0, N=20.947):
    return round(H0 + N, 3)

# === Giao diện Streamlit ===
st.set_page_config(page_title="Chuyển VN2000 ➜ WGS84 (có cao độ)", layout="centered")
st.title("🛰️ Chuyển VN2000 ➜ WGS84 theo thuật toán bài báo (TM3 + cao độ)")

st.subheader("🔢 Nhập tọa độ phẳng và cao độ địa hình")
x = st.text_input("Tọa độ X (m)", placeholder="Ví dụ: 2222373.588")
y = st.text_input("Tọa độ Y (m)", placeholder="Ví dụ: 595532.212")
z = st.text_input("Cao độ Z (theo mực nước biển - H₀, m)", placeholder="Ví dụ: 135.604", value="0")

province = st.selectbox("Chọn tỉnh/thành", list(province_lon0.keys()))
lon0 = province_lon0[province]
geoid_N = geoid_height_by_province.get(province, 20.0)  # fallback

if st.button("📍 Chuyển đổi"):
    try:
        x_val = float(x)
        y_val = float(y)
        z_val = float(z)
        lat, lon = inverse_tm3(x_val, y_val, lon0)
        h = convert_height_geoid_to_ellipsoid(z_val, geoid_N)

        st.success(f"""
        ✅ Kết quả chuyển đổi:
        • Vĩ độ (Latitude): `{lat:.15f}`
        • Kinh độ (Longitude): `{lon:.15f}`
        • Cao độ địa hình (H₀): `{z_val:.3f} m`
        • Cao độ elipsoid (h): `{h:.3f} m` (H₀ + N với N = {geoid_N} m)
        """)
    except:
        st.error("Vui lòng nhập số hợp lệ cho X, Y, Z.")
