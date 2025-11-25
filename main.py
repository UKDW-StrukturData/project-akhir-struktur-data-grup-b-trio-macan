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
    st.write('Prakiraan Cuaca Indonesia dan Lokal')
    st.write('')
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button('Masuk'):
            st.switch_page('pages/Masuk.py')
    with btn_col2:
        if st.button('Mendaftar'):
            st.switch_page('pages/Mendaftar.py')