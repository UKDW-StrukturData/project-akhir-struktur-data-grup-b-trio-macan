import streamlit as st
import random
import google.generativeai as genai
from datetime import datetime

# Konfigurasi API Key Gemini AI
API_KEY = "AIzaSyBJTxjRoVcI5jYI63AQZ1mt8rmY_CXFvrM"

status = False
if ('sudah_login' in st.session_state and st.session_state['sudah_login'] is True):
    status = True

if (status is False):
    st.switch_page('pages/Masuk.py')

# Konfigurasi halaman
st.set_page_config(page_title="Weather Tips AI", page_icon="💡", layout="centered")

# Inisialisasi Gemini AI
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    ai_connected = True
except Exception as e:
    st.error(f"Error koneksi Gemini AI: {e}")
    ai_connected = False

# Fungsi untuk mendapatkan tips sederhana dari Gemini
def get_simple_tips(kota, suhu, kondisi):
    prompt = f"""
    Berikan satu kalimat tips singkat dan friendly dalam bahasa Indonesia untuk cuaca di {kota} dengan suhu {suhu}°C dan kondisi {kondisi}.
    
    Format: 
    [emoji] [kalimat tips singkat dan positif]
    
    Contoh:
    ☀️ Perfect untuk jalan-jalan di taman!
    🌧️ Cocok untuk nonton film di rumah dengan hot chocolate!
    
    Buat hanya SATU kalimat saja, maksimal 10 kata. Gunakan tone yang positif dan friendly.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Judul aplikasi
st.title("🌤️ Weather Tips")
st.caption("Dapatkan tips sederhana untuk aktivitas harianmu")

# Data cuaca sederhana
kota = st.selectbox("Pilih kota:", ["Jakarta", "Bandung", "Surabaya", "Bali", "Yogyakarta"])
suhu = random.randint(25, 35)
kondisi = random.choice(["Cerah", "Berawan", "Hujan", "Panas"])

# Tampilkan info cuaca sederhana
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Suhu", f"{suhu}°C")
with col2:
    st.metric("Kota", kota)
with col3:
    st.metric("Kondisi", kondisi)

st.markdown("---")

# Container untuk Tips AI
st.subheader("💡 Tips")

if ai_connected:
    if st.button("🎯 Dapatkan Tips", type="primary", use_container_width=True):
        with st.spinner("AI sedang memberikan tips..."):
            tips = get_simple_tips(kota, suhu, kondisi)
            
            # Tampilkan tips dalam box yang clean
            st.markdown(
                f"""
                <div style='
                    background-color: #f0f8ff;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #4CAF50;
                    margin: 10px 0;
                '>
                    <h3 style='margin: 0; color: #2c3e50;'>{tips}</h3>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Tombol untuk tips baru
            st.button("🔄 Tips Lain", use_container_width=True)
else:
    st.error("Gemini AI tidak terhubung. Periksa API key Anda.")

# Contoh tips default (jika AI tidak aktif)
if not ai_connected:
    st.info(
        """
        <div style='
            background-color: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
        '>
            <h3 style='margin: 0; color: #2c3e50;'>🌞 Perfect untuk hangout dengan teman!</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Footer
st.markdown("---")
st.caption(f"🕐 Diperbarui: {datetime.now().strftime('%H:%M')}")