import streamlit as st
import math

# --- Hằng số ellipsoid WGS-84 ---
a = 6378137.0
f = 1 / 298.257223563
e2 = 2 * f - f ** 2
e4 = e2 ** 2
e6 = e2 ** 3

# --- 7 tham số Helmert (QĐ 05/2007) ---
dx = -191.90441429
dy = -39.30318279
dz = -111.45032835
rx = math.radians(-0.00928836 / 3600)
ry = math.radians(0.01975479 / 3600)
rz = math.radians(-0.00427372 / 3600)
s = 0.252906278 * 1e-6  # ppm ➜ hệ số

# --- TM3 chuỗi hệ số ---
A0 = 1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256
A2 = 3 / 8 * (e2 + e4 / 4 + 15 * e6 / 128)
A4 = 15 / 256 * (e4 + 3 * e6 / 4)
A6 = 35 * e6 / 3072

# --- Kinh tuyến trục và độ cao Geoid một số tỉnh ---
province_data = {
    "Thanh Hóa": {"lon0": 105.0, "geoid": 20.947},
    "Hà Nội": {"lon0": 105.0, "geoid": 20.0},
    "Quảng Trị": {"lon0": 106.25, "geoid": 18.0},
    "Đà Nẵng": {"lon0": 107.75, "geoid": 19.5},
    "TP. Hồ Chí Minh": {"lon0": 105.75, "geoid": 17.0},
    "Cà Mau": {"lon0": 104.5, "geoid": 15.5},
}

# --- B1: xy ➜ B, L, h ---
def xy2BL(x, y, lon0_deg, H0, geoid, k0=0.9999, x0=0, y0=500000):
    M = (x - x0) / k0
    mu = M / (a * A0)
    phi1 = mu + A2 * math.sin(2 * mu) + A4 * math.sin(4 * mu) + A6 * math.sin(6 * mu)
    e1sq = e2 / (1 - e2)
    C1 = e1sq * math.cos(phi1) ** 2
    T1 = math.tan(phi1) ** 2
    N1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    R1 = N1 * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2)
    D = (y - y0) / (N1 * k0)
    B = phi1 - (N1 * math.tan(phi1) / R1) * (
        D**2 / 2 - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e1sq) * D**4 / 24 +
        (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e1sq - 3*C1**2) * D**6 / 720
    )
    L0 = math.radians(lon0_deg)
    L = L0 + (
        D - (1 + 2*T1 + C1) * D**3 / 6 +
        (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e1sq + 24*T1**2) * D**5 / 120
    ) / math.cos(phi1)
    h = H0 + geoid
    return B, L, h

# --- B2: BLH ➜ XYZ ---
def BLH2XYZ(B, L, h):
    N = a / math.sqrt(1 - e2 * math.sin(B) ** 2)
    X = (N + h) * math.cos(B) * math.cos(L)
    Y = (N + h) * math.cos(B) * math.sin(L)
    Z = (N * (1 - e2) + h) * math.sin(B)
    return X, Y, Z

# --- B3: 7 tham số Helmert ---
def transform7(X, Y, Z):
    X2 = X + dx + s * X + (-rz) * Y + ry * Z
    Y2 = Y + dy + rz * X + s * Y + (-rx) * Z
    Z2 = Z + dz + (-ry) * X + rx * Y + s * Z
    return X2, Y2, Z2

# --- B4: XYZ ➜ BLH (WGS84) ---
def XYZ2BLH(X, Y, Z, eps=1e-11):
    p = math.sqrt(X**2 + Y**2)
    lon = math.atan2(Y, X)
    lat = math.atan2(Z, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > eps:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        h = p / math.cos(lat0) - N
        lat = math.atan2(Z, p * (1 - e2 * N / (N + h)))
    N = a / math.sqrt(1 - e2 * math.sin(lat)**2)
    h = p / math.cos(lat) - N
    return math.degrees(lat), math.degrees(lon), round(h, 3)

# --- Giao diện Streamlit ---
st.set_page_config(page_title="VN2000 ➜ WGS84 (4 bước kỹ thuật)", layout="centered")
st.title("🛰️ Chuyển VN-2000 ➜ WGS84 theo 4 bước kỹ thuật (TM3, 7 tham số)")

x = st.text_input("Nhập tọa độ X (m)", placeholder="VD: 2222373.588")
y = st.text_input("Nhập tọa độ Y (m)", placeholder="VD: 595532.212")
z = st.text_input("Nhập cao độ địa hình Z (H₀, m)", placeholder="VD: 135.604", value="0")
province = st.selectbox("Chọn tỉnh", list(province_data.keys()))

if st.button("📍 Chuyển đổi"):
    try:
        x, y, z = float(x), float(y), float(z)
        lon0 = province_data[province]["lon0"]
        geoid = province_data[province]["geoid"]

        # B1 ➜ B2 ➜ B3 ➜ B4
        B, L, h = xy2BL(x, y, lon0, z, geoid)
        X1, Y1, Z1 = BLH2XYZ(B, L, h)
        X2, Y2, Z2 = transform7(X1, Y1, Z1)
        lat, lon, h_final = XYZ2BLH(X2, Y2, Z2)

        st.success(f"""✅ Kết quả WGS84:
        • Vĩ độ (Lat): `{lat:.15f}`
        • Kinh độ (Lon): `{lon:.15f}`
        • Cao độ elipsoid (h): `{h_final:.3f} m`""")
    except:
        st.error("❌ Vui lòng nhập đúng định dạng số.")
