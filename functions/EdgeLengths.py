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

    # Thêm cạnh nối điểm cuối và đầu nếu không trùng nhau
    if len(points) > 2 and points[0] != points[-1]:
        lat1, lon1 = points[-1]
        lat2, lon2 = points[0]
        g = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
        dist = g['s12']
        rows.append({
            "STT": len(points),
            "Cạnh": f"{len(points)}-1",
            "Độ dài (m)": round(dist, 2)
        })

    return pd.DataFrame(rows)

# --- Logic hiển thị bảng độ dài cạnh trong app.py (cột giữa) ---
# Đặt sau nút tải CSV/KML và chỉ hiển thị nếu đã nối điểm và bật hiển thị cạnh
if st.session_state.get("join_points", False) and st.session_state.get("show_lengths", False):
    df_sorted = df.sort_values(
        by="Tên điểm",
        key=lambda col: col.map(lambda x: int(x) if str(x).isdigit() else str(x)),
        ascending=True
    ).reset_index(drop=True)
    points = [(row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]) for _, row in df_sorted.iterrows()]

    if points:
        df_edges = compute_edge_lengths(points)
        st.markdown("### 📏 Bảng độ dài các cạnh")
        st.dataframe(df_edges, height=250)

        st.download_button(
            label="📤 Tải bảng độ dài cạnh (CSV)",
            data=df_edges.to_csv(index=False).encode("utf-8"),
            file_name="edge_lengths.csv",
            mime="text/csv"
        )
