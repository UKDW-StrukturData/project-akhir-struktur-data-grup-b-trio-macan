import streamlit as st

status = False
if ('sudah_login' in st.session_state and st.session_state['sudah_login'] is True):
    status = True

if (status is False):
    st.switch_page('pages/Masuk.py')

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Cuaca", page_icon="🌤️")

# Judul aplikasi
st.title("🌤️ Aplikasi Prakiraan Cuaca")

# Search bar
kota_pencarian = st.text_input("🔍 Cari kota", placeholder="Masukkan nama kota...")

# Kota default (jika tidak ada input)
if not kota_pencarian:
    kota_pencarian = "Madrid"

# Header dengan nama kota
st.header(f"{kota_pencarian}")
st.write("Kemungkinan hujan: 0%")

# Suhu saat ini
st.metric(label="Suhu Saat Ini", value="31°C")

# Garis pemisah
st.divider()

# PRAKIRAAN HARI INI
st.subheader("PRAKIRAAN HARI INI")

# Data untuk prakiraan hari ini
waktu = ["6:00 Pagi", "9:00 Pagi", "12:00 Siang", "3:00 Sore", "6:00 Sore", "9:00 Malam"]
suhu = ["25°", "28°", "33°", "34°", "32°", "30°"]

# Tampilkan dalam kolom
kolom = st.columns(6)
for i in range(6):
    with kolom[i]:
        st.write(f"**{waktu[i]}**")
        st.write(f"**{suhu[i]}**")

# Garis pemisah
st.divider()

# KONDISI UDARA
st.subheader("KONDISI UDARA")

# Buat 2 kolom untuk kondisi udara
kol1, kol2 = st.columns(2)

with kol1:
    st.metric("Terasa Seperti", "30°")
    st.metric("Kemungkinan hujan", "0%")

with kol2:
    st.metric("Angin", "0.2 km/jam")
    st.metric("Indeks UV", "3")

# Garis pemisah
st.divider()

# PRAKIRAAN 7 HARI
st.subheader("PRAKIRAAN 7 HARI")

# Data untuk prakiraan 7 hari
data_prakiraan = [
    {"Hari": "Hari Ini", "Cuaca": "Cerah", "Suhu": "36/22"},
    {"Hari": "Selasa", "Cuaca": "Cerah", "Suhu": "37/21"},
    {"Hari": "Rabu", "Cuaca": "Cerah", "Suhu": "37/21"},
    {"Hari": "Kamis", "Cuaca": "Berawan", "Suhu": "37/21"},
    {"Hari": "Jumat", "Cuaca": "Berawan", "Suhu": "37/21"},
    {"Hari": "Sabtu", "Cuaca": "Hujan", "Suhu": "37/21"},
    {"Hari": "Minggu", "Cuaca": "Badai", "Suhu": "37/21"}
]

# Tampilkan prakiraan 7 hari
for data in data_prakiraan:
    kol1, kol2, kol3 = st.columns([1, 2, 1])
    
    with kol1:
        st.write(f"**{data['Hari']}**")
    
    with kol2:
        # Tambahkan emoji berdasarkan cuaca
        if data['Cuaca'] == 'Cerah':
            st.write(f"☀️ {data['Cuaca']}")
        elif data['Cuaca'] == 'Berawan':
            st.write(f"☁️ {data['Cuaca']}")
        elif data['Cuaca'] == 'Hujan':
            st.write(f"🌧️ {data['Cuaca']}")
        elif data['Cuaca'] == 'Badai':
            st.write(f"⛈️ {data['Cuaca']}")
    
    with kol3:
        st.write(f"**{data['Suhu']}°**")

# Sidebar dengan informasi tambahan
with st.sidebar:
    st.title("Tentang")
    st.write("Aplikasi Cuaca Sederhana")
    st.write("Fitur:")
    st.write("• Pencarian kota")
    st.write("• Prakiraan hari ini")
    st.write("• Kondisi udara")
    st.write("• Prakiraan 7 hari")
    
    st.divider()
    st.write("Dibuat dengan Streamlit ❤️")