
import math

def vn2000_to_wgs84_nnoisuy(x, y, h_vn2000, lon0_deg, ref_lat, ref_lon, ref_h):
    """
    Chuyển tọa độ VN2000 (x, y, h) sang WGS84 (lat, lon, h) bằng nội suy sai số XYZ từ điểm tham chiếu chuẩn.
    """
    # Hằng số
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 2 * f - f**2
    e4 = e2**2
    e6 = e2**3

    # TM3 hệ số
    A0 = 1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256
    A2 = 3 / 8 * (e2 + e4 / 4 + 15 * e6 / 128)
    A4 = 15 / 256 * (e4 + 3 * e6 / 4)
    A6 = 35 * e6 / 3072

    k0 = 0.9999
    x0 = 0
    y0 = 500000

    # B1: TM3 nghịch ➜ BL
    M = (x - x0) / k0
    mu = M / (a * A0)
    phi1 = mu + A2 * math.sin(2 * mu) + A4 * math.sin(4 * mu) + A6 * math.sin(6 * mu)
    e1sq = e2 / (1 - e2)
    C1 = e1sq * math.cos(phi1)**2
    T1 = math.tan(phi1)**2
    N1 = a / math.sqrt(1 - e2 * math.sin(phi1)**2)
    R1 = N1 * (1 - e2) / (1 - e2 * math.sin(phi1)**2)
    D = (y - y0) / (N1 * k0)

    B = phi1 - (N1 * math.tan(phi1) / R1) * (
        D**2 / 2 -
        (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e1sq) * D**4 / 24 +
        (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e1sq - 3*C1**2) * D**6 / 720
    )
    L = math.radians(lon0_deg) + (
        D - (1 + 2*T1 + C1) * D**3 / 6 +
        (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e1sq + 24*T1**2) * D**5 / 120
    ) / math.cos(phi1)

    # B2: BLH ➜ XYZ
    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X_vn = (N + h_vn2000) * math.cos(B) * math.cos(L)
    Y_vn = (N + h_vn2000) * math.cos(B) * math.sin(L)
    Z_vn = (N * (1 - e2) + h_vn2000) * math.sin(B)

    # Chuyển WGS84 chuẩn thực tế ➜ XYZ
    lat_rad = math.radians(ref_lat)
    lon_rad = math.radians(ref_lon)
    N_ref = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
    X_ref = (N_ref + ref_h) * math.cos(lat_rad) * math.cos(lon_rad)
    Y_ref = (N_ref + ref_h) * math.cos(lat_rad) * math.sin(lon_rad)
    Z_ref = (N_ref * (1 - e2) + ref_h) * math.sin(lat_rad)

    # B3: nội suy dịch chuyển
    X_wgs = X_vn + (X_ref - X_vn)
    Y_wgs = Y_vn + (Y_ref - Y_vn)
    Z_wgs = Z_vn + (Z_ref - Z_vn)

    # B4: XYZ ➜ BLH
    p = math.sqrt(X_wgs**2 + Y_wgs**2)
    lon = math.atan2(Y_wgs, X_wgs)
    lat = math.atan2(Z_wgs, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > 1e-12:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        h = p / math.cos(lat0) - N
        lat = math.atan2(Z_wgs, p * (1 - e2 * N / (N + h)))

    lat_deg = math.degrees(lat)
    lon_deg = math.degrees(lon)

    return round(lat_deg, 8), round(lon_deg, 8), round(h, 7), (
        round(lat_deg - ref_lat, 8),
        round(lon_deg - ref_lon, 8),
        round(h - ref_h, 7),
    )
