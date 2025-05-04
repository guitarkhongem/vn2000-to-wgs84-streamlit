import folium

def add_numbered_markers(map_obj, df):
    """
    Vẽ marker trên bản đồ theo đúng thứ tự STT từ DataFrame.
    DataFrame phải có cột: 'STT', 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Tên điểm' (có thể không cần nếu chỉ dùng STT).
    """
    # Sắp xếp theo STT nếu chưa chắc thứ tự đúng
    df = df.sort_values("STT").reset_index(drop=True)

    for _, row in df.iterrows():
        lat = row["Vĩ độ (Lat)"]
        lon = row["Kinh độ (Lon)"]
        stt = str(row["STT"])
        ten_diem = row.get("Tên điểm", f"Điểm {stt}")

        # Dấu "+"
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:12px; color:red; font-weight:bold;'>+</div>
            """),
            tooltip=f"{stt}: {ten_diem}"
        ).add_to(map_obj)

        # Số STT to
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:18px; font-weight:bold; color:red'>{stt}</div>
            """)
        ).add_to(map_obj)

