import folium

def generate_map(df):
    m = folium.Map(
        location=[df["Vĩ độ (Lat)"].mean(), df["Kinh độ (Lon)"].mean()],
        zoom_start=14,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri.WorldImagery"
    )
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Vĩ độ (Lat)"], row["Kinh độ (Lon)"]],
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)
    return m
