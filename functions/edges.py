import folium
from geographiclib.geodesic import Geodesic

def add_edge_lengths(map_obj, points):
    """
    Thêm độ dài cạnh vào bản đồ folium, tính theo WGS84.
    - map_obj: đối tượng folium.Map
    - points: danh sách [(lat, lon), ...] đã được khép kín
    """
    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]

        # Tính khoảng cách và hướng
        g = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
        dist = g['s12']
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2
        angle = g['azi1']

        # Offset để dễ đọc
        offset_lat = mid_lat + 0.0001
        offset_lon = mid_lon + 0.0001

        folium.Marker(
            location=[offset_lat, offset_lon],
            icon=folium.DivIcon(html=f"""
                <div style='transform: rotate({angle - 90:.1f}deg); transform-origin: center; font-size:14px; color:red; white-space:nowrap;'>
                    {dist:.2f} m
                </div>"""),
        ).add_to(map_obj)
