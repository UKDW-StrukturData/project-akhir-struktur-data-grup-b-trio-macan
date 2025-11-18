import streamlit as st

email_input = st.text_input('Masukkan Email anda')
username_input = st.text_input('Buat Nama Pengguna ')
password_input = st.text_input('Kata Sandi Baru', type= 'password')
confirm_password = st.text_input('Konfirmasi Kata Sandi', type= 'password')

if st.button('Sign Up'):
    st.switch_page('pages/Login.py')