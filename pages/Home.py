import streamlit as st
import random
import pandas as pd
import requests
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import csv
import altair

#PAGE CONFIG!
st.set_page_config(page_title="Hawa - Cuaca & Tips AI", page_icon="🌤️", layout="centered")

if "sudah_login" not in st.session_state or st.session_state["sudah_login"] is not True:
    st.switch_page("pages/Masuk.py")

#LOGO!
logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(image=logo,size="large",icon_image=icon)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=250)

st.set_page_config(page_title="Hawa", layout="centered")

st.title("Prakiraan Cuaca Indonesia dan Lokal")

# Input wilayah
df_kode = pd.read_csv("kode_wilayah.csv", header=None, names=["kode", "nama"])
st.caption("Masukkan wilayah Desa/Kelurahan yang anda inginkan. Contoh: Kemayoran.")
wilayah_pilihan = st.selectbox(
    "Pilih Desa/Kelurahan", 
    df_kode["nama"].tolist(),
    index=None,
    placeholder="Pilih wilayah..."
)

kota = "-"
suhu = "-"
kondisi = "-"

if wilayah_pilihan:
    adm4 = df_kode[df_kode["nama"] == wilayah_pilihan]["kode"].values[0]
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    st.success(f'Berhasil menampilkan untuk wilayah {wilayah_pilihan}')
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Menampilkan info lokasi
        lokasi = data.get("lokasi", {})
        forecast = data.get("data", [])
        if lokasi:
            kota = lokasi.get("desa", "-")
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
        if forecast:
            forecast3jam = []

            for entry in forecast:
                cuaca = entry.get("cuaca", [])
                if isinstance(cuaca, list) and len(cuaca) > 0:
                    for hari in cuaca:
                        if isinstance(hari, list):
                            for x in hari:
                                if isinstance(x, dict):
                                    forecast3jam.append({
                                        "Jam": x.get("local_datetime", "-"),
                                        "Cuaca": x.get("weather_desc", "-"),
                                        "Suhu (°C)": x.get("t", "-"),
                                        "Kelembapan (%)": x.get("hu", "-"),
                                        "Angin (km/j)": x.get("ws", "-"),
                                        "Arah Angin": x.get("wd", "-"),
                                    })

            df = pd.DataFrame(forecast3jam)
            st.subheader("Prakiraan Per 3 Jam")
            st.dataframe(df, use_container_width=True)
            # Setelah selesai mengisi forecast3jam
            df3 = pd.DataFrame(forecast3jam)

            import altair as alt

            chart = alt.Chart(df3).mark_line(point=True).encode(
            x="Jam:T",
            y="Suhu (°C):Q",
            tooltip=["Jam", "Suhu (°C)"]
            ).properties(
            width="container",
            height=300,
            title="Perubahan Suhu per 3 Jam"
)

            st.altair_chart(chart, use_container_width=True)


            # Ambil data baris pertama untuk Tips AI
            if len(df) > 0:
                row0 = df.iloc[0]
                suhu = row0.get("Suhu (°C)", "-")
                kondisi = row0.get("Cuaca", "-")

            # ------------------------------
            # 2) TAMPILKAN PRAKIRAAN PER HARI
            # ------------------------------
            st.subheader("Detail Prakiraan Cuaca per Hari")

            cuaca_harian = forecast[0].get("cuaca", [])

            if isinstance(cuaca_harian, list) and len(cuaca_harian) > 0:

                for index_hari, prakiraan_harian in enumerate(cuaca_harian):

                    st.markdown(f"### Hari ke-{index_hari + 1}")

                    if isinstance(prakiraan_harian, list):

                        for prakiraan in prakiraan_harian:

                            waktu_lokal = prakiraan.get("local_datetime", "N/A")
                            deskripsi = prakiraan.get("weather_desc", "N/A")
                            suhu_val = prakiraan.get("t", "N/A")
                            kelembapan = prakiraan.get("hu", "N/A")
                            kec_angin = prakiraan.get("ws", "N/A")
                            arah_angin = prakiraan.get("wd", "N/A")
                            jarak_pandang = prakiraan.get("vs_text", "N/A")

                            raw_img = prakiraan.get("image", "")
                            img_url = raw_img.replace(" ", "%20") if raw_img else None

                            with st.container(border=True):
                                st.write(f"**Jam:** {waktu_lokal}")
                                st.write(f"**Cuaca:** {deskripsi}")

                                if img_url:
                                    st.image(img_url, width=60)

                                st.write(f"**Suhu:** {suhu_val}°C")
                                st.write(f"**Kelembapan:** {kelembapan}%")
                                st.write(f"**Kecepatan Angin:** {kec_angin} km/j")
                                st.write(f"**Arah Angin:** dari {arah_angin}")
                                st.write(f"**Jarak Pandang:** {jarak_pandang}")

            else:
                st.info("Data cuaca harian tidak ada.")
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengakses API BMKG: {e}")
    except ValueError:
        st.error("Response bukan JSON yang valid.")

st.divider()

# Konfigurasi API Key Gemini AI
API_KEY = st.secrets["GEMINI_API_KEY"]
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    ai_connected = True
except Exception as e:
    ai_connected = False
    st.error(f"Gagal konek Gemini: {e}")
    
# Cek status login
status = False

if ('sudah_login' in st.session_state and st.session_state['sudah_login'] is True):
    status = True

if (status is False):
    st.switch_page('pages/Masuk.py')

# Konfigurasi halaman
st.set_page_config(page_title="Hawa", layout="centered")

# Inisialisasi Gemini AI
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    ai_connected = True
except Exception as e:
    st.error(f"Error koneksi Gemini AI: {e}")
    ai_connected = False

# Fungsi untuk mendapatkan tips sederhana dari Gemini
def get_simple_tips(kota, suhu, kondisi):
    prompt = f"""
    Berikan beberapa tips singkat dan friendly dalam bahasa Indonesia untuk cuaca di {kota} 
    dengan suhu {suhu}°C dan kondisi {kondisi}. 
    
    Sertakan:
    - Cocok dilakukan:
    - Tidak cocok dilakukan:

    Beri 1 baris kosong sebelum pindah bagian. Pakai bullet dan emoji yang relevan.
    Maksimal 60 kata.
    """

    try:
        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        if hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text.strip()
        return "AI tidak memberikan output."
    except Exception as e:
        return f"Error: {e}"

# Container untuk Tips AI
st.subheader("💡 Tips")

if ai_connected:
    if st.button("✨ Dapatkan Tips", type="primary", use_container_width=True):
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

# Footer
st.markdown("---")
st.caption(f"🕐 Diperbarui: {datetime.now().strftime('%H:%M')}")
st.caption('Sumber API : BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)')