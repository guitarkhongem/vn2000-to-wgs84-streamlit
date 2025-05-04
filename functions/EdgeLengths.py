from geographiclib.geodesic import Geodesic
import pandas as pd

def compute_edge_lengths(points):
    """
    Tính chiều dài các cạnh giữa các điểm liên tiếp theo WGS84.
    Trả về pandas.DataFrame: STT, Cạnh, Độ dài (m)
    """
    rows = []
    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]
        g = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
        dist = g['s12']
        rows.append({
            "STT": i + 1,
            "Cạnh": f"{i+1}-{i+2}",
            "Độ dài (m)": round(dist, 2)
        })
    return pd.DataFrame(rows)
