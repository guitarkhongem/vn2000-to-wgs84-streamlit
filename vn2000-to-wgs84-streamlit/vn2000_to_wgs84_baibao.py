
import math

def vn2000_to_wgs84_baibao(x, y, z, lon0_deg):
    # Tham số Ellipsoid WGS84
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 0.00669437999013
    ep2 = e2 / (1 - e2)
    k0 = 0.9999
    lon0 = math.radians(lon0_deg)
    y0 = 500000

    # Công thức (1) - TM3 nghịch
    m = x / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))

    B1 = (mu
        + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
        + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
        + (151 * e1 ** 3 / 96) * math.sin(6 * mu))

    N1 = a / math.sqrt(1 - e2 * math.sin(B1) ** 2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(B1) ** 2) ** 1.5
    C1 = ep2 * math.cos(B1) ** 2
    T1 = math.tan(B1) ** 2
    D = (y - y0) / (k0 * N1)

    B = B1 - (N1 * math.tan(B1) / R1) * (
        D**2 / 2
        - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*ep2) * D**4 / 24
        + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*ep2 - 3*C1**2) * D**6 / 720
    )

    L = lon0 + (1 / math.cos(B1)) * (
        D - (1 + 2*T1 + C1) * D**3 / 6
        + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*ep2 + 24*T1**2) * D**5 / 120
    )

    # Công thức (4) - BLH to XYZ
    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X_vn = (N + z) * math.cos(B) * math.cos(L)
    Y_vn = (N + z) * math.cos(B) * math.sin(L)
    Z_vn = ((1 - e2) * N + z) * math.sin(B)

    # Công thức (7) - Helmert thuận
    dX, dY, dZ = -191.90441429, -39.30318279, -111.45032835
    rx = math.radians(-0.00928836 / 3600)
    ry = math.radians(0.01975479 / 3600)
    rz = math.radians(-0.00427372 / 3600)
    k = 1.000000252906278

    X_wgs = dX + k * (X_vn + rz * Y_vn - ry * Z_vn)
    Y_wgs = dY + k * (-rz * X_vn + Y_vn + rx * Z_vn)
    Z_wgs = dZ + k * (ry * X_vn - rx * Y_vn + Z_vn)

    # Công thức (5) - XYZ to BLH
    p = math.sqrt(X_wgs**2 + Y_wgs**2)
    lat = math.atan2(Z_wgs, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > 1e-12:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        h = p / math.cos(lat0) - N
        lat = math.atan2(Z_wgs, p * (1 - e2 * N / (N + h)))

    lon = math.atan2(Y_wgs, X_wgs)

    return round(math.degrees(lat), 8), round(math.degrees(lon), 8), round(h, 7)


def wgs84_to_vn2000_baibao(lat_deg, lon_deg, h, lon0_deg):
    # Công thức (4) - BLH to XYZ
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 0.00669437999013
    ep2 = e2 / (1 - e2)
    B = math.radians(lat_deg)
    L = math.radians(lon_deg)
    L0 = math.radians(lon0_deg)
    k0 = 0.9999
    y0 = 500000

    N = a / math.sqrt(1 - e2 * math.sin(B)**2)
    X = (N + h) * math.cos(B) * math.cos(L)
    Y = (N + h) * math.cos(B) * math.sin(L)
    Z = ((1 - e2) * N + h) * math.sin(B)

    # Công thức (8) - Helmert ngược
    dX, dY, dZ = -191.90441429, -39.30318279, -111.45032835
    rx = math.radians(-0.00928836 / 3600)
    ry = math.radians(0.01975479 / 3600)
    rz = math.radians(-0.00427372 / 3600)
    k = 1.000000252906278

    X_vn = (1/k) * (X - dX - rz * (Y - dY) + ry * (Z - dZ))
    Y_vn = (1/k) * (rz * (X - dX) + (Y - dY) - rx * (Z - dZ))
    Z_vn = (1/k) * (-ry * (X - dX) + rx * (Y - dY) + (Z - dZ))

    # Công thức (5) - XYZ to BLH
    p = math.sqrt(X_vn**2 + Y_vn**2)
    lat = math.atan2(Z_vn, p * (1 - e2))
    lat0 = 0
    while abs(lat - lat0) > 1e-12:
        lat0 = lat
        N = a / math.sqrt(1 - e2 * math.sin(lat0)**2)
        H = p / math.cos(lat0) - N
        lat = math.atan2(Z_vn, p * (1 - e2 * N / (N + H)))

    lon = math.atan2(Y_vn, X_vn)
    l = lon - L0
    eta = math.sqrt(ep2) * math.cos(lat)
    T = math.tan(lat) ** 2
    C = ep2 * math.cos(lat)**2
    A = l * math.cos(lat)

    A1 = 1 + 3/4*e2 + 45/64*e2**2
    A2 = 3/8*e2 + 15/32*e2**2
    A3 = 15/256*e2**2
    XB = a * (1 - e2) * (A1 * lat - A2 * math.sin(2*lat) + A3 * math.sin(4*lat))

    A1x = (math.cos(lat)**2 * (5 - T + 9 * eta**2 + 4 * eta**4)) / 12
    A2x = (math.cos(lat)**4 * (61 - 58 * T + T**2)) / 360
    A1y = (math.cos(lat)**2 * (1 - T + eta**2)) / 6
    A2y = (math.cos(lat)**4 * (5 - 18 * T + T**2 + 14 * eta**2 - 58 * T * eta**2)) / 120

    x = k0 * (XB + A**2 / 2 * N * math.sin(2 * lat) * (1 + A1x * A**2 + A2x * A**4))
    y = k0 * A * N * math.cos(lat) * (1 + A1y * A**2 + A2y * A**4) + y0

    return round(x, 4), round(y, 4), round(H, 4)
