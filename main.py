import streamlit as st
import base64
from PIL import Image
import requests
import base64

# Fungsi background sederhana
def set_simple_background(image_url):
    try:
        response = requests.get(image_url)
        encoded_string = base64.b64encode(response.content).decode()
        
        bg_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Container putih untuk konten */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 10px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading background: {e}")

# Set background
background_url = "https://png.pngtree.com/thumb_back/fh260/background/20231012/pngtree-aesthetic-sky-fluffy-white-clouds-on-a-blue-background-image_13642352.png"
set_simple_background(background_url)

# Load logo (ganti dengan path logo Anda)
try:
    logo = Image.open("image.png")
    icon = Image.open("image.png")
except:
    # Fallback - buat logo sederhana
    from PIL import ImageDraw
    logo = Image.new('RGB', (100, 100), color='lightblue')
    icon = logo

st.logo(image=logo, size="large", icon_image=icon)

# Konten
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=200)
    st.title('Prakiraan Cuaca Indonesia')
    st.subheader('Informasi cuaca terkini untuk seluruh wilayah')
    
    st.write('')
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button('Masuk', use_container_width=True, type="primary"):
            st.switch_page('pages/Masuk.py')
    with col_btn2:
        if st.button('Mendaftar', use_container_width=True):
            st.switch_page('pages/Mendaftar.py')