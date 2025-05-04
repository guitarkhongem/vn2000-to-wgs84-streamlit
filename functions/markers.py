import folium

def add_numbered_markers(map_obj, df):
    """
    Đánh số thứ tự các điểm trên bản đồ folium từ DataFrame có cột 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Tên điểm'.
    """
    for i, row in df.iterrows():
        lat = row["Vĩ độ (Lat)"]
        lon = row["Kinh độ (Lon)"]
        label = str(i + 1)
        ten_diem = row["Tên điểm"]

        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:12px; color:red; font-weight:bold;'>+</div>
            """),
            tooltip=f"{label}: {ten_diem}"
        ).add_to(map_obj)

        # Đánh số to màu đỏ
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:18x; font-weight:bold; color:red'>{label}</div>
            """)
        ).add_to(map_obj)
