import streamlit as st

# ===============================
# Dữ liệu kinh tuyến trục VN-2000
# ===============================
LON0_BY_PROVINCE = {
    "Lai Châu": 103.0,
    "Sơn La": 104.0,
    "Kiên Giang": 104.5,
    "Cà Mau": 104.5,
    "Lào Cai": 104.75,
    "Yên Bái": 104.75,
    "Nghệ An": 104.75,
    "Phú Thọ": 104.75,
    "An Giang": 104.75,
    "Thanh Hóa": 105.0,
    "Vĩnh Phúc": 105.0,
    "Hà Tây": 105.0,
    "Đồng Tháp": 105.0,
    "Cần Thơ": 105.0,
    "Bạc Liêu": 105.0,
    "Hà Nội": 105.0,
    "Ninh Bình": 105.0,
    "Hà Nam": 105.0,
    "Hà Giang": 105.5,
    "Hải Dương": 105.5,
    "Hà Tĩnh": 105.5,
    "Bắc Ninh": 105.5,
    "Hưng Yên": 105.5,
    "Thái Bình": 105.5,
    "Nam Định": 105.5,
    "Tây Ninh": 105.5,
    "Vĩnh Long": 105.5,
    "Sóc Trăng": 105.5,
    "Trà Vinh": 105.5,
    "Cao Bằng": 105.75,
    "Long An": 105.75,
    "Tiền Giang": 105.75,
    "Bến Tre": 105.75,
    "Hải Phòng": 105.75,
    "TP. Hồ Chí Minh": 105.75,
    "Bình Dương": 105.75,
    "Tuyên Quang": 106.0,
    "Hòa Bình": 106.0,
    "Quảng Bình": 106.0,
    "Quảng Trị": 106.25,
    "Bình Phước": 106.25,
    "Bắc Kạn": 106.5,
    "Thái Nguyên": 106.5,
    "Bắc Giang": 107.0,
    "Thừa Thiên Huế": 107.0,
    "Lạng Sơn": 107.25,
    "Kon Tum": 107.5,
    "Quảng Ninh": 107.75,
    "Đồng Nai": 107.75,
    "Bà Rịa – Vũng Tàu": 107.75,
    "Quảng Nam": 107.75,
    "Lâm Đồng": 107.75,
    "Đà Nẵng": 107.75,
    "Quảng Ngãi": 108.0,
    "Ninh Thuận": 108.25,
    "Khánh Hòa": 108.25,
    "Bình Định": 108.25,
    "Đắk Lắk": 108.5,
    "Phú Yên": 108.5,
    "Gia Lai": 108.5,
    "Bình Thuận": 108.5
}

# ==================================
# UI chọn kinh tuyến trục (lon0)
# ==================================
def select_lon0():
    st.markdown("### 🫐 Chọn múi chiếu VN-2000")

    # Khởi tạo state
    if "lon0_value" not in st.session_state:
        st.session_state.lon0_value = 106.25
    if "province_select" not in st.session_state:
        st.session_state.province_select = "-- Không chọn --"

    col_province, col_lon0, _ = st.columns([1, 1, 2])

    # --- Chọn tỉnh ---
    with col_province:
        province = st.selectbox(
            "Chọn tỉnh / thành phố",
            ["-- Không chọn --"] + sorted(LON0_BY_PROVINCE.keys()),
            key="province_select"
        )

    # 👉 Nếu chọn tỉnh → cập nhật lon0 NGAY
    if province != "-- Không chọn --":
        st.session_state.lon0_value = LON0_BY_PROVINCE[province]

    # --- Nhập lon0 (LUÔN đọc từ session_state) ---
    with col_lon0:
        st.number_input(
            "Hoặc nhập kinh tuyến trục ",
            min_value=102.0,
            max_value=110.0,
            step=0.25,
            key="lon0_value"
        )

    # Hiển thị trạng thái
    if province != "-- Không chọn --":
        st.success(
            f"Kinh tuyến trục theo tỉnh **{province}**: "
            f"{st.session_state.lon0_value}"
        )
    else:
        st.info(
            f"Dùng kinh tuyến trục nhập tay: "
            f"{st.session_state.lon0_value}"
        )

    return st.session_state.lon0_value




