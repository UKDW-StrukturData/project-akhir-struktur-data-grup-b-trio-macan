import streamlit as st
from PIL import Image
import time
import re
import sqlite3

def daftar_baru(username, email, password):
    # Simpan data ke database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()
    


conn = sqlite3.connect('database.db')
c = conn.cursor()
# Membuat tabel jika belum ada
c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )''')

# Fungsi validasi email sederhana
def email_valid(email):
    pola = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pola, email) is not None

# Load logo & icon
logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(image=logo,size="large",icon_image=icon)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(logo, use_container_width=True)

col_kiri, col_tengah, col_kanan = st.columns([1, 3, 1])
with col_tengah:
    st.markdown("<h2 style='text-align:center;'>Pendaftaran Akun</h2>", unsafe_allow_html=True)
    email_input = st.text_input('Masukkan Email anda')
    username_input = st.text_input('Buat Username')
    password_input = st.text_input('Password Baru', type='password')
    confirm_password = st.text_input('Konfirmasi Password', type='password')
    
    st.write("")
    pesan_placeholder = st.empty()
    bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
    with bcol1:
        if st.button('Kembali'):
            st.switch_page('pages/Masuk.py')
    with bcol2:
        daftar = st.button('Daftar', type='primary')
        if daftar:
            if not email_valid(email_input):
                pesan_placeholder.error("Format email tidak valid.")
            elif not username_input:
                pesan_placeholder.error('Username masih kosong')
            elif not password_input:
                pesan_placeholder.error('Password masih kosong')
            elif len(password_input) < 6:
                pesan_placeholder.error("Password harus terdiri dari minimal 6 karakter.")
            elif not confirm_password:
                pesan_placeholder.error('Konfirmasi password masih kosong')
            elif password_input != confirm_password:
                pesan_placeholder.error("Password dan konfirmasi password tidak sesuai.")
            else:
                conn_check = sqlite3.connect('database.db')
                c_check = conn_check.cursor()

                c_check.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username_input, email_input))
                data_exist = c_check.fetchone()
                conn_check.close()
                if data_exist:
                    if data_exist[0] == username_input:
                        pesan_placeholder.error("Username sudah terdaftar!\n\n Silakan gunakan username lain.")
                    elif data_exist[1] == email_input:
                        pesan_placeholder.error("Email sudah terdaftar! Silakan gunakan email lain.")
                else:
                    daftar_baru(username_input, email_input, password_input)
                    pesan_placeholder.success("Akun berhasil dibuat!")
                    time.sleep(2)
                    st.switch_page('pages/Masuk.py')
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)