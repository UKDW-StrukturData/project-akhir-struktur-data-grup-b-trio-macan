import streamlit as st

username_input = st.text_input('Nama Pengguna')
password_input = st.text_input('Kata Sandi', type= 'password')


if st.button('Masuk'):
    if username_input == "admin" and password_input == "admin123":

        st.session_state['sudah_login'] = True
        st.switch_page('pages/Home.py')
    else:
        st.error("username atau password salah")
