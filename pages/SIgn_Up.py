import streamlit as st

email_input = st.text_input('Masukkan Email anda')
username_input = st.text_input('Buat Username ')
password_input = st.text_input('Password Baru', type= 'password')
confirm_password = st.text_input('Konfirmasi Password', type= 'password')

if st.button('Mendaftar'):
    st.switch_page('pages/Login.py')