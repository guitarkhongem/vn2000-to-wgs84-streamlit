# functions/polygon.py

import folium

def draw_polygon(map_obj, points):
    """
    Nối các điểm thành polyline khép kín trên bản đồ folium.
    Không vẽ điểm tròn, chỉ vẽ đường nối (Polyline).
    """
    if len(points) < 2:
        return

    # Khép kín nếu chưa đóng
    if points[0] != points[-1]:
        points.append(points[0])

    folium.PolyLine(
        locations=points,
        weight=3,
        color="blue",
        tooltip="Polygon khép kín"
    ).add_to(map_obj)
