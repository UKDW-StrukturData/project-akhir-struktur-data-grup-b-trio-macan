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
st.logo(
    image=logo,
    size="large",
    icon_image=icon)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=250)
username_input = st.text_input('Nama Pengguna')
password_input = st.text_input('Kata Sandi', type= 'password')


if st.button('Masuk'):
    if (login(username_input, password_input)):
        st.session_state['sudah_login'] = True
        st.success("Berhasil masuk!")
        
        time.sleep(2)
        st.switch_page('pages/Home.py')
    else:
        st.error("Username atau password salah!")
