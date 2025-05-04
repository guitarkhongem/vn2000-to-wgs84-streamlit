import folium

def add_numbered_markers(map_obj, df):
    """
    Vẽ các điểm đánh dấu trên bản đồ với tên trùng khớp 'Tên điểm'.
    Yêu cầu DataFrame có các cột: 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Tên điểm'.
    """

    df = df.reset_index(drop=True)  # Giữ nguyên thứ tự hiện tại

    for _, row in df.iterrows():
        lat = row["Vĩ độ (Lat)"]
        lon = row["Kinh độ (Lon)"]
        ten_diem = row["Tên điểm"]

        # Dấu cộng nhỏ đỏ ở tâm điểm
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html="""
                <div style='font-size:12px; color:red; font-weight:bold;'>+</div>
            """),
            tooltip=ten_diem
        ).add_to(map_obj)

        # Hiển thị Tên điểm to màu đỏ
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:16px; font-weight:bold; color:red'>{ten_diem}</div>
            """)
        ).add_to(map_obj)
