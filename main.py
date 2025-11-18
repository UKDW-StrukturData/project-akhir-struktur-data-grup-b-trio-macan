import streamlit as st

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title('Hawa')
    st.write('Prakiraan Cuaca Indonesia dan Lokal')
    st.write('')
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button('Masuk'):
            st.switch_page('pages/Login.py')
    with btn_col2:
        if st.button('Mendaftar'):
            st.switch_page('pages/Sign_Up.py')