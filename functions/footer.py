import streamlit as st
from datetime import datetime

def show_footer():
    year = datetime.now().year  # Lấy năm hiện tại
    st.markdown("---")
    st.markdown(
        "📌 Tác giả: **Trần Trường Sinh**  \n"
        "📞 0917.750.555"
    )
    st.markdown(
        "🔍 **Nguồn công thức**: Bài báo khoa học: **CÔNG TÁC TÍNH CHUYỂN TỌA ĐỘ TRONG CÔNG NGHỆ MÁY BAY KHÔNG NGƯỜI LÁI CÓ ĐỊNH VỊ TÂM CHỤP CHÍNH XÁC**  \n"
        "Tác giả: Trần Trung Anh¹, Quách Mạnh Tuấn²  \n"
        "¹ Đại học Mỏ - Địa chất, ² Công ty CP Xây dựng và TM QT Miền Bắc  \n"
        "_Hội nghị KH Quốc gia về Công nghệ Địa không gian_"
    )
    st.markdown(
        f"© {year} Trần Trường Sinh."
    )
