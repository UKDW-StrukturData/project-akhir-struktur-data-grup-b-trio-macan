import streamlit as st

username_input = st.text_input('Buat Username ')
password_input = st.text_input('Password Baru', type= 'password')
confirm_password = st.text_input('Konfirmasi Password', type= 'password')
if st.button('Sign Up'):
    st.switch_page('pages/Login.py')