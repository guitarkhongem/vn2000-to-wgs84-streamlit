import streamlit as st

NEW_URL = "https://guitarkhongem.github.io/vn2000-to-wgs84-Plus/"

st.set_page_config(page_title="VN2000 ⇄ WGS84 – Đã chuyển địa chỉ", page_icon="🔁")

st.title("🔁 Ứng dụng đã chuyển sang địa chỉ mới")
st.write(
    "Phiên bản mới **VN2000 to WGS84 Plus** nhanh hơn và có thêm tính năng. "
    "Vui lòng nhấp nút bên dưới để tiếp tục:"
)

st.link_button("👉 Mở phiên bản mới", NEW_URL, type="primary", use_container_width=True)

st.caption(f"Hoặc truy cập trực tiếp: {NEW_URL}")
