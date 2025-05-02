import math
import streamlit as st

# ------------------- Hàm chuyển đổi VN2000 → WGS84 -------------------
def vn2000_to_wgs84_baibao(x, y, h, lon0_deg):
    a = 6378137.0
    e2 = 0.00669437999013
    af = 1 / 298.257223563
    e_ = e2 / (1 - e2)
    k0 = 0.9999
    y0 = 500000
    lon0_rad = math.radians(lon0_deg)

    mu = (x / k0) / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    a1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    B1 = mu + (3 * a1 / 2 - 27 * a1**3 / 32) * math.sin(2 * mu)         + (21 * a1**2 / 16 - 55 * a1**4 / 32) * math.sin(4 * mu)         + (151 * a1**3 / 96) * math.sin(6 * mu)

    N1 = a / math.sqrt(1 - e2 * math.sin(B1)**2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(B1)**2)**1.5
    C1 = e_ * math.cos(B1)**2
    T1 = math.tan(B1)**2
    D = (y - y0) / (k0 * N1)

    B = B1 - (N1 * math.tan(B1) / R1) * (
        D**2 / 2
        - (5 + 3 * T1 + 10 * C1 - 4 * C1**2 - 9 * e_) * D**4 / 24
        + (61 + 90 * T1 + 298 * C1 + 45 * T1**2 - 252 * e_ - 3 * C1**2) * D**6 / 720
    )

    L = lon0_rad + (1 / math.cos(B1)) * (
        D
        - (1 + 2 * T1 + C1) * D**3 / 6
        + (5 - 2 * C1 + 28 * T1 - 3 * C1**2 + 8 * e_ + 24 * T1**2) * D**6 / 120
    )

    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X_vn = (N + h) * math.cos(B) * math.cos(L)
    Y_vn = (N + h) * math.cos(B) * math.sin(L)
    Z_vn = ((1 - e2) * N + h) * math.sin(B)

    dX = -191.90441429
    dY = -39.30318279
    dZ = -111.45032835
    rx = math.radians(-0.00928836 / 3600)
    ry = math.radians(0.01975479 / 3600)
    rz = math.radians(-0.00427372 / 3600)
    k = 1.000000252906278

    X_wgs = dX + k * (X_vn + rz * Y_vn - ry * Z_vn)
    Y_wgs = dY + k * (-rz * X_vn + Y_vn + rx * Z_vn)
    Z_wgs = dZ + k * (ry * X_vn - rx * Y_vn + Z_vn)

    p = math.sqrt(X_wgs ** 2 + Y_wgs ** 2)
    lon = math.atan2(Y_wgs, X_wgs)
    lat = math.atan2(Z_wgs, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > 1e-12:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        h2 = p / math.cos(lat0) - N
        lat = math.atan2(Z_wgs, p * (1 - e2 * N / (N + h2)))

    return round(math.degrees(lat), 8), round(math.degrees(lon), 8), round(h2, 7)

# ------------------- Hàm chuyển đổi WGS84 → VN2000 -------------------
def wgs84_to_vn2000_baibao(lat_deg, lon_deg, h, lon0_deg):
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 0.00669437999013
    ep2 = e2 / (1 - e2)
    k0 = 0.9999
    y0 = 500000

    B = math.radians(lat_deg)
    L = math.radians(lon_deg)
    L0 = math.radians(lon0_deg)

    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    Xw = (N + h) * math.cos(B) * math.cos(L)
    Yw = (N + h) * math.cos(B) * math.sin(L)
    Zw = ((1 - e2) * N + h) * math.sin(B)

    dX = -191.90441429
    dY = -39.30318279
    dZ = -111.45032835
    rx = math.radians(-0.00928836 / 3600)
    ry = math.radians(0.01975479 / 3600)
    rz = math.radians(-0.00427372 / 3600)
    k = 1.000000252906278

    Xs = Xw - dX
    Ys = Yw - dY
    Zs = Zw - dZ

    Xv = (1 / k) * (Xs - rz * Ys + ry * Zs)
    Yv = (1 / k) * (rz * Xs + Ys - rx * Zs)
    Zv = (1 / k) * (-ry * Xs + rx * Ys + Zs)

    p = math.sqrt(Xv**2 + Yv**2)
    gamma = math.atan((Zv / p) * (1 - f + (a * e2) / math.sqrt(Xv**2 + Yv**2 + Zv**2)))
    B_vn = math.atan((Zv * (1 - f) + a * e2 * math.sin(gamma)**3) / ((1 - f) * (p - a * e2 * math.cos(gamma)**3)))
    L_vn = math.atan2(Yv, Xv)
    if L_vn < 0:
        L_vn += 2 * math.pi
    H_vn = math.cos(B_vn) * p + Zv * math.sin(B_vn) - a * math.sqrt(1 - e2 * math.sin(B_vn)**2)

    l = L_vn - L0
    eta = math.sqrt(ep2) * math.cos(B_vn)
    T = math.tan(B_vn)**2
    C = ep2 * math.cos(B_vn)**2
    N = a / math.sqrt(1 - e2 * math.sin(B_vn)**2)

    A1x = (math.cos(B_vn)**2 * (5 - T + 9 * eta**2 + 4 * eta**4)) / 12
    A2x = (math.cos(B_vn)**4 * (61 - 58 * T + T**2)) / 360
    A1y = (math.cos(B_vn)**2 * (1 - T + eta**2)) / 6
    A2y = (math.cos(B_vn)**4 * (5 - 18 * T + T**2 + 14 * eta**2 - 58 * T * eta**2)) / 120

    A1 = 1 + 3/4 * e2 + 45/64 * e2**2
    A2 = 3/8 * e2 + 15/32 * e2**2
    A3 = 15/256 * e2**2
    XB = a * (1 - e2) * (A1 * B_vn - A2 * math.sin(2 * B_vn) + A3 * math.sin(4 * B_vn))

    x = k0 * (XB + l**2 / 4 * N * math.sin(2 * B_vn) * (1 + A1x * l**2 + A2x * l**4))
    y = k0 * l * N * math.cos(B_vn) * (1 + A1y * l**2 + A2y * l**4) + y0

    return round(x, 4), round(y, 4), round(H_vn, 4)