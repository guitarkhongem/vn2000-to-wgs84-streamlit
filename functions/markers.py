import folium
import pandas as pd

def add_numbered_markers(map_obj, df):
    """
    Vẽ các điểm đánh dấu trên bản đồ với tên trùng khớp 'Tên điểm'.
    Bỏ qua nếu 'Tên điểm' bị rỗng hoặc NaN.
    Yêu cầu DataFrame có cột: 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Tên điểm'.
    """

    df = df.reset_index(drop=True)

    for _, row in df.iterrows():
        lat = row["Vĩ độ (Lat)"]
        lon = row["Kinh độ (Lon)"]
        ten_diem = row.get("Tên điểm", "")

        # Nếu tên điểm rỗng hoặc NaN thì bỏ qua việc hiển thị tên
        if pd.isna(ten_diem) or str(ten_diem).strip() == "":
            ten_diem = None

        # Dấu cộng nhỏ ở tâm điểm
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html="""
                <div style='font-size:12px; color:red; font-weight:bold;'>+</div>
            """),
            tooltip=ten_diem if ten_diem else None
        ).add_to(map_obj)

        # Tên điểm nếu có
        if ten_diem:
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f"""
                    <div style='font-size:16px; font-weight:bold; color:red'>{ten_diem}</div>
                """)
            ).add_to(map_obj)
