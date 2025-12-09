import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
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

st.title("Prakiraan Cuaca Indonesia dan Lokal")

try:
    df_kode = pd.read_csv(
        "kode_wilayah.csv", 
        header=None, 
        names=["kode", "nama", "level"], 
        dtype={"kode": str},
        on_bad_lines='skip' 
    )
    # Filter hanya Desa/Kelurahan (adm4)
    df_kode = df_kode[df_kode["level"] == "adm4"]
    
    st.caption("Masukkan wilayah Desa/Kelurahan yang anda inginkan. Contoh: Kemayoran.")
    wilayah_pilihan = st.selectbox(
        "Pilih Desa/Kelurahan", 
        df_kode["nama"].tolist(),
        index=None,
        placeholder="Pilih wilayah..."
    )
except Exception as e:
    st.error(f"Gagal memuat database wilayah: {e}")
    wilayah_pilihan = None

# Inisialisasi variabel default
kota = "-"
suhu = "-"
kondisi = "-"

def buat_pdf_lengkap(dataframe, nama_kota, gambar_grafik):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 1. Judul PDF
    title = Paragraph(f"Laporan Prakiraan Cuaca - {nama_kota}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 10))
    
    # 2. Subjudul Waktu
    waktu_str = datetime.now().strftime('%d %B %Y, %H:%M WIB')
    subtitle = Paragraph(f"Dicetak pada: {waktu_str}", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # 3. Masukkan Grafik (Gambar)
    if gambar_grafik:
        # Simpan gambar matplotlib ke memory agar bisa dibaca reportlab
        img_buffer = BytesIO()
        gambar_grafik.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        
        # Buat object Image reportlab
        im = RLImage(img_buffer, width=6*inch, height=3*inch)
        elements.append(im)
        elements.append(Spacer(1, 20))

    # 4. Tabel Data
    # Mengambil header kolom dan data isinya
    data_tabel = [dataframe.columns.to_list()] + dataframe.astype(str).values.tolist()

    t = Table(data_tabel)

    # Styling Tabel
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkcyan), # Header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    t.setStyle(style)

    elements.append(t)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


if wilayah_pilihan:
    adm4 = df_kode[df_kode["nama"] == wilayah_pilihan]["kode"].values[0]
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    if adm4 not in wilayah_pilihan: 
        st.success(f'Berhasil menampilkan untuk wilayah {wilayah_pilihan}')
    else:
        st.error('Masukkan wilayah yang spesifik')
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
            
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(df3["Jam"], df3["Suhu (°C)"], marker="o")
            ax.set_title("Perubahan Suhu per 3 Jam")
            ax.set_xlabel("Waktu")
            ax.set_ylabel("Suhu (°C)")
            ax.grid(True)
            # Simpan grafik untuk dikirim ke PDF
            gambar_grafik = fig

            pdf_buffer =  buat_pdf_lengkap(df, kota, gambar_grafik)
            st.download_button(
            label="Unduh Data",
            data=pdf_buffer,
            file_name="prakiraan_cuaca/3 jam.pdf",
            mime="application/pdf",
            )
            
            st.divider()
            
            import altair as alt
            df3["Jam"] = pd.to_datetime(df3["Jam"], errors="coerce")
            chart = alt.Chart(df3).mark_area(
                opacity=0.4,
                interpolate="monotone").encode(
                    x=alt.X("Jam:T", title="Waktu"),
                    y=alt.Y("Suhu (°C):Q", title="Suhu (°C)"), tooltip=["Jam", "Suhu (°C)"]).properties(width="container", height=300, title="Perubahan Suhu per 3 Jam (Area Chart)")
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

                    # ================================
        #   STRUKTUR DATA LINKED LIST
        # ================================
        class Node:
            def __init__(self, data):
                self.data = data      # isi: list prakiraan cuaca per hari
                self.next = None
                self.prev = None

        class LinkedList:
            def __init__(self, items):
                self.head = None
                self.tail = None
                self.size = 0
                self._build(items)

            def _build(self, items):
                prev_node = None
                for item in items:
                    node = Node(item)
                    if not self.head:
                        self.head = node
                    if prev_node:
                        prev_node.next = node
                        node.prev = prev_node
                    prev_node = node
                self.tail = prev_node
                self.size = len(items)

            def get(self, index):
                """Ambil node ke-index (0-based)"""
                if index < 0 or index >= self.size:
                    return None
                current = self.head
                for _ in range(index):
                    current = current.next
                return current


        # ================================
        #   INISIALISASI LINKED LIST HARIAN
        # ================================
        if isinstance(cuaca_harian, list) and len(cuaca_harian) > 0:

            # Buat linked list cuaca tiap hari
            hari_list = LinkedList(cuaca_harian)

            # Session state untuk indepx hari
            if "hari_index" not in st.session_state:
                st.session_state["hari_index"] = 0  # default hari pertama

            # Navigasi
            col_nav1, col_nav2 = st.columns(2)
            with col_nav1:
                if st.button("⬅️ Prev", use_container_width=True):
                    if st.session_state["hari_index"] > 0:
                        st.session_state["hari_index"] -= 1
                        st.rerun()

            with col_nav2:
                if st.button("Next ➡️", use_container_width=True):
                    if st.session_state["hari_index"] < hari_list.size - 1:
                        st.session_state["hari_index"] += 1
                        st.rerun()

            # Ambil data hari aktif dari linked list
            hari_ke = st.session_state["hari_index"]
            node_hari = hari_list.get(hari_ke)

            st.markdown(f"### Hari ke-{hari_ke + 1}")

            # Menampilkan isi hari
            if node_hari and isinstance(node_hari.data, list):
                for prakiraan in node_hari.data:

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
# API_KEY = st.secrets["GEMINI_API_KEY"]

API_KEY = st.session_state['token_api'] #Lokal
#API_KEY = st.secrets['GEMINI_KEY'] #Streamlit Online

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

st.divider()
col_pindah1, col_pindah2 = st.columns([3, 1])

with col_pindah1:
    st.markdown("Layanan Perbandingan Cuaca")
    st.caption("Ingin tahu perbedaan cuaca di sini dengan daerah lain? Cek selisih suhu dan kelembapannya.")

with col_pindah2:
    # Spacer agar tombol agak turun ke tengah vertikal
    st.write("") 
    if st.button("Bandingkan \nSekarang ➡️", use_container_width=True):
        try:
            # Pastikan nama file di dalam folder pages sesuai
            st.switch_page("pages/Perbandingan Cuaca.py") 
        except Exception as e:
            st.error(f"Halaman tidak ditemukan: {e}")

st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)