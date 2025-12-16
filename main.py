import streamlit as st
from PIL import Image
from streamlit.errors import StreamlitAPIException

# Konfigurasi Halaman (Harus di baris pertama setelah import)
st.set_page_config(
    page_title="Prakiraan Cuaca Indonesia",
    page_icon="🌦️",
    layout="centered"
)

# --- MOCKING API KEY (Hanya simulasi jika file apikey.py tidak ada) ---
try:
    from apikey import keykey
except ImportError:
    keykey = "dummy_token_12345"

if 'token_api' not in st.session_state:
    st.session_state['token_api'] = keykey

try:
    logo_img = Image.open("image.png")
except:
    logo_img = None

if hasattr(st, "logo") and logo_img:
    st.logo(image=logo_img, icon_image=logo_img)

logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(image=logo,size="large",icon_image=icon)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(logo, width=250)
    
    st.title('Prakiraan Cuaca ID')
    st.markdown("""
    **HAWA** - informasi cuaca terkini, akurat, dan terpercaya untuk seluruh wilayah Indonesia.
    """)
    st.divider() # Garis pemisah estetis
    
    # Layout Tombol
    col_btn1, col_btn2 = st.columns(2, gap="medium")
    
    with col_btn1:
        if st.button('Masuk', use_container_width=True, type="primary"):
            # Cek apakah file page ada sebelum switch untuk menghindari error runtime
            try:
                st.switch_page('pages/Masuk.py')
            except StreamlitAPIException:
                st.warning("Halaman 'pages/Masuk.py' belum dibuat.")
                
    with col_btn2:
        if st.button('Mendaftar', use_container_width=True):
            try:
                st.switch_page('pages/Mendaftar.py')
            except StreamlitAPIException:
                 st.warning("Halaman 'pages/Mendaftar.py' belum dibuat.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# Footer Sederhana
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)