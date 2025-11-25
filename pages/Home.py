import streamlit as st
import random
import pandas as pd
import requests
import google.generativeai as genai
from datetime import datetime
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


st.set_page_config(page_title="Cuaca BMKG (ADM4)", page_icon="⛅", layout="centered")
st.title("Prakiraan Cuaca BMKG (3 hari, per 3 jam)")

st.caption("Masukkan kode wilayah ADM4 (Kelurahan/Desa). Contoh: 31.71.03.1001 untuk Kelurahan Kemayoran.")
adm4 = st.text_input("Kode ADM4", value="")

if adm4:
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Tampilkan informasi lokasi jika tersedia
        lokasi = data.get("lokasi", {})
        if lokasi:
            st.subheader("Lokasi")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Desa/Kelurahan**: {lokasi.get('desa', '-')}")
                st.write(f"**Kecamatan**: {lokasi.get('kecamatan', '-')}")
                st.write(f"**Kota/Kabupaten**: {lokasi.get('kotkab', '-')}")
                st.write(f"**Provinsi**: {lokasi.get('provinsi', '-')}")
            with col2:
                st.write(f"**Lat/Lon**: {lokasi.get('lat', '-')}, {lokasi.get('lon', '-')}")
                st.write(f"**Zona Waktu**: {lokasi.get('timezone', '-')}")
                st.write(f"**Analysis Date (UTC)**: {data.get('analysis_date', '-')}")

        # Koleksi elemen prakiraan
        forecast = data.get("data", [])
        if forecast:
            # Normalisasi list of dicts → DataFrame
            df = pd.DataFrame(forecast)
            # Ubah nama kolom agar lebih ramah
            rename_map = {
                "utc_datetime": "UTC",
                "local_datetime": "Lokal",
                "t": "Suhu (°C)",
                "hu": "RH (%)",
                "weather_desc": "Cuaca",
                "ws": "Angin (km/jam)",
                "wd": "Arah Angin",
                "tcc": "Awan (%)",
                "vs_text": "Jarak Pandang (km)"
            }
            df = df.rename(columns=rename_map)
            # Sort berdasarkan waktu lokal (jika ada)
            if "Lokal" in df.columns:
                df = df.sort_values("Lokal")

            st.subheader("Prakiraan per 3 jam")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Data prakiraan tidak tersedia untuk kode ADM4 tersebut.")

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengakses API BMKG: {e}")
    except ValueError:
        st.error("Response bukan JSON yang valid.")

st.divider()


# Konfigurasi API Key Gemini AI
API_KEY = "AIzaSyCeAfT7Z9unRCshEKMwNwXSmwsRimTgpeI"

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
st.title("Hawa")
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