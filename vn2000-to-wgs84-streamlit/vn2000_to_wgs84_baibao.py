
import math

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
    B1 = (mu + (3 * a1 / 2 - 27 * a1**3 / 32) * math.sin(2 * mu)
        + (21 * a1**2 / 16 - 55 * a1**4 / 32) * math.sin(4 * mu)
        + (151 * a1**3 / 96) * math.sin(6 * mu))

    N1 = a / math.sqrt(1 - e2 * math.sin(B1)**2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(B1)**2) ** 1.5
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
        + (5 - 2 * C1 + 28 * T1 - 3 * C1**2 + 8 * e_ + 24 * T1**2) * D**5 / 120
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


def wgs84_to_vn2000_baibao(lat_deg, lon_deg, h, lon0_deg):
    a = 6378137.0
    e2 = 0.00669437999013
    af = 1 / 298.257223563
    e_ = e2 / (1 - e2)
    B = math.radians(lat_deg)
    L = math.radians(lon_deg)
    L0 = math.radians(lon0_deg)
    k0 = 0.9999
    y0 = 500000

    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X_wgs = (N + h) * math.cos(B) * math.cos(L)
    Y_wgs = (N + h) * math.cos(B) * math.sin(L)
    Z_wgs = ((1 - e2) * N + h) * math.sin(B)

    dX = -191.90441429
    dY = -39.30318279
    dZ = -111.45032835
    rx = math.radians(-0.00928836 / 3600)
    ry = math.radians(0.01975479 / 3600)
    rz = math.radians(-0.00427372 / 3600)
    k = 1.000000252906278

    Xs = X_wgs - dX
    Ys = Y_wgs - dY
    Zs = Z_wgs - dZ

    X_vn = (1 / k) * (Xs - rz * Ys + ry * Zs)
    Y_vn = (1 / k) * (rz * Xs + Ys - rx * Zs)
    Z_vn = (1 / k) * (-ry * Xs + rx * Ys + Zs)

    p = math.sqrt(X_vn**2 + Y_vn**2)
    lon = math.atan2(Y_vn, X_vn)
    lat = math.atan2(Z_vn, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > 1e-12:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        h_vn = p / math.cos(lat0) - N
        lat = math.atan2(Z_vn, p * (1 - e2 * N / (N + h_vn)))

    l = lon - L0
    eta = math.sqrt(e_) * math.cos(lat)
    T = math.tan(lat) ** 2
    C = e_ * math.cos(lat)**2
    A = l * math.cos(lat)

    A1x = (math.cos(lat)**2 * (5 - T + 9 * eta**2 + 4 * eta**4)) / 12
    A2x = (math.cos(lat)**4 * (61 - 58 * T + T**2)) / 360
    A1y = (math.cos(lat)**2 * (1 - T + eta**2)) / 6
    A2y = (math.cos(lat)**4 * (5 - 18 * T + T**2 + 14 * eta**2 - 58 * T * eta**2)) / 120

    A1 = 1 + (3 / 4) * e2 + (45 / 64) * e2**2
    A2 = (3 / 8) * e2 + (15 / 32) * e2**2
    A3 = (15 / 256) * e2**2
    XB = a * (1 - e2) * (A1 * lat - A2 * math.sin(2 * lat) + A3 * math.sin(4 * lat))

    x = k0 * (XB + A**2 / 2 * N * math.sin(2 * lat) * (1 + A1x * A**2 + A2x * A**4))
    y = k0 * A * N * math.cos(lat) * (1 + A1y * A**2 + A2y * A**4) + y0

    return round(x, 4), round(y, 4), round(h_vn, 4)
