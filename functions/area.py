from geographiclib.geodesic import Geodesic

def compute_polygon_area(points):
    """
    Tính diện tích và chu vi theo Geodesic WGS84 từ danh sách các điểm (lat, lon).
    Trả về tuple: (diện tích m², chu vi m)
    """
    if len(points) < 3:
        return 0.0, 0.0

    if points[0] != points[-1]:
        points.append(points[0])

    poly = Geodesic.WGS84.Polygon()
    for lat, lon in points:
        poly.AddPoint(lat, lon)
    _, perimeter, area = poly.Compute()
    return abs(area), perimeter

def shoelace_area(points):
    """
    Tính diện tích theo Shoelace formula từ các điểm (X, Y).
    """
    if len(points) < 3:
        return 0.0

    n = len(points)
    x_c = sum(p[0] for p in points) / n
    y_c = sum(p[1] for p in points) / n
    shifted = [(x - x_c, y - y_c) for x, y in points]

    area = 0.0
    for i in range(n):
        x0, y0 = shifted[i]
        x1, y1 = shifted[(i + 1) % n]
        area += x0 * y1 - x1 * y0

    return abs(area) / 2

def geodesic_area(points):
    """
    Tính diện tích theo Geodesic (lat/lon) WGS84.
    """
    if len(points) < 3:
        return 0.0

    if points[0] != points[-1]:
        points.append(points[0])

    poly = Geodesic.WGS84.Polygon()
    for lat, lon in points:
        poly.AddPoint(lat, lon)
    _, _, area = poly.Compute()
    return abs(area)

def compare_areas(flat_xy_points, latlon_points):
    """
    So sánh diện tích tính bằng Shoelace (VN2000) và Geodesic (WGS84)
    Trả về: (shoelace_area, geodesic_area, percent_diff, ha_shoelace, ha_geodesic)
    """
    A1 = shoelace_area(flat_xy_points)
    A2 = geodesic_area(latlon_points)
    if max(A1, A2) == 0:
        return round(A1, 1), round(A2, 1), 0.0, round(A1 / 10000, 1), round(A2 / 10000, 1)

    diff_percent = abs(A1 - A2) / max(A1, A2) * 100
    return round(A1, 1), round(A2, 1), round(diff_percent, 1), round(A1 / 10000, 1), round(A2 / 10000, 1)
