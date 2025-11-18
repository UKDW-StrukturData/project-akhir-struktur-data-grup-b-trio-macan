import streamlit as st

username_input = st.text_input('Username')
password_input = st.text_input('Password', type= 'password')
if st.button('Login'):
    st.switch_page('main.py')