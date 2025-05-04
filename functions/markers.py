import folium

def add_numbered_markers(map_obj, df):
    df = df.reset_index(drop=True)  # Bắt buộc để đảm bảo đánh số từ 1 theo thứ tự hiện tại
    for i, row in df.iterrows():
        lat = row["Vĩ độ (Lat)"]
        lon = row["Kinh độ (Lon)"]
        label = str(i + 1)
        ten_diem = row["Tên điểm"]

        # Dấu "+"
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:12px; color:red; font-weight:bold;'>+</div>
            """),
            tooltip=f"{label}: {ten_diem}"
        ).add_to(map_obj)

        # Số thứ tự
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:18px; font-weight:bold; color:red'>{label}</div>
            """)
        ).add_to(map_obj)
