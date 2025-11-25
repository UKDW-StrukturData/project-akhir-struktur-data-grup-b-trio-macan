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
username_input = st.text_input('Nama Pengguna')
password_input = st.text_input('Kata Sandi', type= 'password')


if st.button('Masuk'):
    if username_input == "admin" and password_input == "admin123":

        st.session_state['sudah_login'] = True
        st.switch_page('pages/Home.py')
    else:
        st.error("username atau password salah")
