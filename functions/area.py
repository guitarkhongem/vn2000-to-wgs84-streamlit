from geographiclib.geodesic import Geodesic

def compute_polygon_area(points):
    """
    Tính diện tích và chu vi theo WGS84 từ danh sách các điểm (lat, lon).
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
