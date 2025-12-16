import streamlit as st
from PIL import Image
import sqlite3
import time

def login(username, password):
    # Cek apakah username dan password cocok
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if (user is not None):
        return True
    return False

logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo( image=logo, size="large", icon_image=icon)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    c_img_1, c_img_2, c_img_3 = st.columns([1, 2, 1])
    with c_img_2:
        if 'logo' in locals():
            st.image(logo, use_container_width=True)
    st.markdown("<h2 style='text-align:center;'>Halaman Masuk</h2>", unsafe_allow_html=True)
    username_input = st.text_input('Username')
    password_input = st.text_input('Kata Sandi', type= 'password')

    if st.button('Masuk', type='primary', use_container_width=True):
        if (login(username_input, password_input)):
            st.session_state['sudah_login'] = True
            st.session_state.username = username_input
            st.session_state.show_welcome = True
            st.success("Berhasil masuk!")
            time.sleep(2)
            st.switch_page('pages/Home.py')
        else:
            st.error("Username atau password salah!")

@st.dialog('Konfirmasi pembuatan akun')
def buat_akun():
    st.write('Apakah anda ingin membuat akun baru ?')
    if st.button('Ya', use_container_width=True, type='primary'):
        st.switch_page("pages/Mendaftar.py")
    if st.button('Tidak', use_container_width=True):
        st.rerun()  # Tutup dialog


col1, col2, col3 = st.columns([1, 0.8, 1])
with col2:
    if st.button('Belum punya akun ?', type='primary'):
        buat_akun()

st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)