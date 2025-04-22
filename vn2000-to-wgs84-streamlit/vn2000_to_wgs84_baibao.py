
import math

def vn2000_to_wgs84_baibao(x, y, h, lon0_deg):
    # Elipsoid WGS-84 theo bài báo
    a = 6378137.0
    e2 = 0.00669437999013
    af = 1 / 298.257223563
    e_ = e2 / (1 - e2)
    k0 = 0.9999
    y0 = 500000
    lon0_rad = math.radians(lon0_deg)

    # B1: TM3 nghịch theo công thức (1)
    mu = (x / k0) / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    a1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    B1 = (mu
        + (3 * a1 / 2 - 27 * a1**3 / 32) * math.sin(2 * mu)
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

    # B2: BLH → XYZ (Công thức 4)
    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X_vn = (N + h) * math.cos(B) * math.cos(L)
    Y_vn = (N + h) * math.cos(B) * math.sin(L)
    Z_vn = ((1 - e2) * N + h) * math.sin(B)

    # B3: Helmert (Công thức 7)
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

    # B4: XYZ → BLH (Công thức 5)
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
