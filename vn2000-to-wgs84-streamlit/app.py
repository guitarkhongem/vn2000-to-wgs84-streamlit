import streamlit as st
import pandas as pd
from functions import vn2000_to_wgs84_baibao, wgs84_to_vn2000_baibao
import re

# Sau khi đã tính ra df và lưu vào st.session_state.df
df = st.session_state.get("df", None)

# Google Maps JS + KML Layer + Markers
if df is not None:
    # Tạo mảng điểm JS
    points_js = ",".join([
        "{{lat: {lat:.8f}, lng: {lng:.8f}}}".format(lat=row["Vĩ độ (Lat)"], lng=row["Kinh độ (Lon)"])
        for _, row in df.iterrows()
    ])
    html = f"""
    <div id="map" style="width:100%;height:500px;"></div>
    <script>
      function initMap() {{
        const map = new google.maps.Map(document.getElementById('map'), {{
          center: {{lat: {df["Vĩ độ (Lat)"].mean():.8f}, lng: {df["Kinh độ (Lon)"].mean():.8f} }},
          zoom: 14
        }});
        // Nền My Maps của bạn dưới dạng KML
        const kmlUrl = 'https://www.google.com/maps/d/kml?mid=1gHTIagvnAKWB66oVKHlkAlpHyra8UF8';
        new google.maps.KmlLayer({{url: kmlUrl, map: map}});
        // Các điểm tính được
        const pts = [{points_js}];
        pts.forEach(pt => {{
          new google.maps.Marker({{
            position: pt,
            map: map,
            icon: {{
              path: google.maps.SymbolPath.CIRCLE,
              scale: 5,
              fillColor: 'red',
              fillOpacity: 0.8,
              strokeWeight: 0
            }}
          }});
        }});
      }}
    </script>
    <script async defer
      src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
    """
    st.components.v1.html(html, height=520)
