import streamlit as st
from PIL import Image
import re

# Contoh daftar username yang sudah ada (bisa diganti database)
daftar_username = ["admin", "user123", "testakun"]

# Fungsi validasi email sederhana
def email_valid(email):
    pola = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pola, email) is not None

# Load logo & icon
logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(image=logo, size="large", icon_image=icon)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(logo, width=250)

    email_input = st.text_input('Masukkan Email anda')
    username_input = st.text_input('Buat Username')
    password_input = st.text_input('Password Baru', type='password')
    confirm_password = st.text_input('Konfirmasi Password', type='password')

    if st.button('Mendaftar'):

        # === VALIDASI EMAIL ===
        if not email_valid(email_input):
            st.error("Format email tidak valid! Contoh: nama@gmail.com")
        
        # === VALIDASI FIELD KOSONG ===
        elif not email_input or not username_input or not password_input:
            st.warning("Semua field wajib diisi!")

        # === CEK USERNAME APAKAH SUDAH TERPAKAI ===
        elif username_input in daftar_username:
            st.error("Username sudah dipakai! Silakan gunakan username lain.")
        
        # === CEK PASSWORD SAMA ===
        elif password_input != confirm_password:
            st.error("Password dan konfirmasi password tidak cocok!")
        
        else:
            # Simpan ke session state
            st.session_state['email'] = email_input
            st.session_state['username'] = username_input
            st.session_state['password'] = password_input
            st.session_state['sudah_daftar'] = True

            st.success(f"Registrasi berhasil! Username **{username_input}** telah dibuat.")

            # Berpindah ke halaman login
            st.switch_page('pages/Masuk.py')
