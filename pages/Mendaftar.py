import streamlit as st
from PIL import Image
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
st.markdown("<h2 style='text-align:center;'>Pendaftaran Akun</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(logo, width=250)

    email_input = st.text_input('Masukkan Email anda')
    username_input = st.text_input('Buat Username')
    password_input = st.text_input('Password Baru', type='password')
    confirm_password = st.text_input('Konfirmasi Password', type='password')
    
    st.write("")

    bcol1, bcol2, bcol3 = st.columns([1, 1, 1])
    with bcol1:
        if st.button('Kembali'):
            st.switch_page('pages/Masuk.py')
    with bcol2:
        daftar = st.button('Daftar')
        if daftar:
            if not email_valid(email_input):
                st.error("Format email tidak valid.")
            elif password_input != confirm_password:
                st.error("Password dan konfirmasi password tidak sesuai.")
            elif len(password_input) < 6:
                st.error("Password harus terdiri dari minimal 6 karakter.")
            else:
                daftar_baru(username_input, email_input, password_input)
                st.success("Akun berhasil dibuat! Silakan klik kembali dan masuk.")
