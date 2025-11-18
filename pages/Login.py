import streamlit as st

username_input = st.text_input('Nama Pengguna')
password_input = st.text_input('Kata Sandi', type= 'password')
if st.button('Masuk'):
    st.switch_page('main.py')