import streamlit as st
from PIL import Image
logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(
    image=logo,
    size="large",
    icon_image=icon)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=250)
email_input = st.text_input('Masukkan Email anda')
username_input = st.text_input('Buat Username ')
password_input = st.text_input('Password Baru', type= 'password')
confirm_password = st.text_input('Konfirmasi Password', type= 'password')

if st.button('Mendaftar'):
    st.session_state['email'] = email_input
    st.session_state['username'] = username_input
    st.session_state['password'] = password_input
    st.session_state['sudah_daftar'] = True
    st.switch_page('pages/Masuk.py')