import streamlit as st
import math

# --- Các hằng số của ellipsoid WGS-84 ---
a = 6378137.0
f = 1 / 298.257223563
e2 = 2 * f - f ** 2
e4 = e2 ** 2
e6 = e2 ** 3

# --- Các hệ số chuỗi nghịch TM3 ---
A0 = 1 - (e2 / 4) - (3 * e4 / 64) - (5 * e6 / 256)
A2 = (3 / 8) * (e2 + (e4 / 4) + (15 * e6 / 128))
A4 = (15 / 256) * (e4 + (3 * e6 / 4))
A6 = (35 * e6) / 3072

# --- Danh sách tỉnh/thành và kinh tuyến trục ---
province_lon0 = {
    "Hà Nội": 105.0, "Thanh Hóa": 105.0, "Nghệ An": 104.75,
    "Quảng Trị": 106.25, "Huế": 107.0, "Đà Nẵng": 107.75,
    "TP. Hồ Chí Minh": 105.75, "Cà Mau": 104.5, "Lào Cai": 104.75,
    # thêm các tỉnh khác nếu cần
}

# --- Hàm nghịch TM3 (từ bài báo) ---
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

# === Streamlit Giao diện ===
st.set_page_config(page_title="Chuyển VN2000 ➜ WGS84 (TM3)", layout="centered")
st.title("🛰️ Chuyển đổi VN2000 ➜ WGS84 (theo thuật toán bài báo)")

st.subheader("🔢 Nhập tọa độ phẳng VN-2000")
x = st.text_input("Tọa độ X (m)", placeholder="Ví dụ: 2222373.588")
y = st.text_input("Tọa độ Y (m)", placeholder="Ví dụ: 595532.212")
province = st.selectbox("Chọn tỉnh/thành", list(province_lon0.keys()))
lon0 = province_lon0[province]

if st.button("📍 Chuyển đổi tọa độ"):
    try:
        x_val = float(x)
        y_val = float(y)
        lat, lon = inverse_tm3(x_val, y_val, lon0)
        st.success(f"""
        ✅ Kết quả chuyển đổi:
        • Vĩ độ (Latitude): `{lat:.15f}`
        • Kinh độ (Longitude): `{lon:.15f}`
        """)
    except:
        st.error("Vui lòng nhập tọa độ X, Y hợp lệ (dạng số).")
