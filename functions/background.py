import base64
import streamlit as st

# --- Hàm đặt background có lớp phủ mờ ---
def set_background(png_file_path):
    with open(png_file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    page_bg_img = f'''
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.6), rgba(255,255,255,0.6)),
                    url("data:image/png;base64,{b64}") no-repeat center center fixed;
        background-size: cover;
    }}

    /* Fix màu chữ cho dễ đọc */
    body, .stApp, .css-10trblm, .css-1d391kg {{
        color: #111 !important;  /* Chữ đậm hơn */
    }}
    </style>
    '''

    st.markdown(page_bg_img, unsafe_allow_html=True)