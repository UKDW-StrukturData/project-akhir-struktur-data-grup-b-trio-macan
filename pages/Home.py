import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from PIL import Image
from io import BytesIO

# --- LIBRARY PDF REPORTLAB ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# untuk switch page Logout
if st.session_state.get("do_logout"):
    st.session_state.clear()
    st.switch_page("main.py")

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Hawa - Cuaca & Tips AI", page_icon="🌤️", layout="centered")

# --- KELAS STRUKTUR DATA (Dipindah ke atas biar aman) ---
class Node:
    def __init__(self, data):
        self.data = data
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
        if index < 0 or index >= self.size:
            return None
        current = self.head
        for _ in range(index):
            current = current.next
        return current

# --- CEK LOGIN ---
if "sudah_login" not in st.session_state or st.session_state["sudah_login"] is not True:
    try:
        st.switch_page("pages/Masuk.py")
    except:
        st.stop()

# --- LOGO ---
try:
    logo = Image.open("image.png")
    icon = Image.open("image.png")
    st.logo(image=logo,size="large",icon_image=icon)
except:
    logo = None

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if logo:
        st.image(logo, width=250)

st.title("Prakiraan Cuaca Indonesia dan Lokal")
st.write('')

# Selamat datang ke aplikasi
if "show_welcome" in st.session_state and st.session_state.show_welcome:
    st.success(f"Selamat datang {st.session_state.username}, semoga harimu menyenangkan.")
    st.write('')
    st.session_state.show_welcome = False

# --- LOAD DATA WILAYAH ---
try:
    df_kode = pd.read_csv(
        "kode_wilayah.csv", 
        header=None, 
        names=["kode", "nama", "level"], 
        dtype={"kode": str},
        on_bad_lines='skip' 
    )
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

# --- FUNGSI PEMBUAT PDF ---
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
        img_buffer = BytesIO()
        gambar_grafik.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        im = RLImage(img_buffer, width=6*inch, height=3*inch)
        elements.append(im)
        elements.append(Spacer(1, 20))

    # 4. Tabel Data
    data_tabel = [dataframe.columns.to_list()] + dataframe.astype(str).values.tolist()
    t = Table(data_tabel)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkcyan),
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
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- LOGIKA UTAMA ---
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

        # Info Lokasi
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

        # Prakiraan Per 3 Jam
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
                                        "Suhu": float(x.get("t", 0)),
                                        "Kelembapan": x.get("hu", "-"),
                                        "Angin": x.get("ws", "-"),
                                    })

            df = pd.DataFrame(forecast3jam)
            df_tampil = df.copy()
            df_tampil.columns = ["Jam", "Cuaca", "Suhu (°C)", "Kelembapan (%)", "Angin (km/j)"]

            st.subheader("Prakiraan Per 3 Jam")
            st.dataframe(df_tampil, use_container_width=True)
            
            # Grafik Matplotlib
            st.write("---")
            df["Jam_dt"] = pd.to_datetime(df["Jam"], errors='coerce')
            
            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.plot(df["Jam_dt"], df["Suhu"], marker="o", color='teal', linestyle='-')
            ax.fill_between(df["Jam_dt"], df["Suhu"], color="teal", alpha=0.3)
            
            ax.set_title(f"Grafik Suhu di {kota}")
            ax.set_xlabel("Waktu")
            ax.set_ylabel("Suhu (°C)")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate()
            
            st.pyplot(fig)
            
            # Tombol Download PDF
            pdf_bytes = buat_pdf_lengkap(df_tampil, kota, fig)
            st.download_button(
                label="Unduh Laporan Cuaca",
                data=pdf_bytes,
                file_name=f"Laporan_Cuaca_{kota}.pdf",
                mime="application/pdf",
                type="primary"
            )
            
            st.divider()

            if len(df) > 0:
                row0 = df.iloc[0]
                suhu = row0.get("Suhu", "-")
                kondisi = row0.get("Cuaca", "-")

            # Prakiraan Per Hari (Linked List)
            st.subheader("Detail Prakiraan Cuaca per Hari")
            cuaca_harian = forecast[0].get("cuaca", [])

            if isinstance(cuaca_harian, list) and len(cuaca_harian) > 0:
                # INISIALISASI LINKED LIST DI SINI (SUDAH AMAN)
                hari_list = LinkedList(cuaca_harian)

                if "hari_index" not in st.session_state:
                    st.session_state["hari_index"] = 0 

                col_nav1, col_nav2 = st.columns(2)
                with col_nav1:
                    if st.button("⬅️ Hari Sebelumnya", use_container_width=True):
                        if st.session_state["hari_index"] > 0:
                            st.session_state["hari_index"] -= 1
                            st.rerun()
                with col_nav2:
                    if st.button("Hari Berikutnya ➡️", use_container_width=True):
                        if st.session_state["hari_index"] < len(cuaca_harian) - 1:
                            st.session_state["hari_index"] += 1
                            st.rerun()

                hari_ke = st.session_state["hari_index"]
                node_hari = hari_list.get(hari_ke)
                
                st.markdown(f"##### Prakiraan Hari ke-{hari_ke + 1}")

                if node_hari and isinstance(node_hari.data, list):
                    for prakiraan in node_hari.data:
                        jam = prakiraan.get("local_datetime", "")
                        ket = prakiraan.get("weather_desc", "")
                        temp = prakiraan.get("t", "")
                        icon_url = prakiraan.get("image", "").replace(" ", "%20")
                        
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([1, 1, 2])
                            with c1:
                                if icon_url: st.image(icon_url, width=50)
                            with c2:
                                st.write(f"**{temp}°C**")
                            with c3:
                                st.write(f"{jam}")
                                st.caption(ket)
            else:
                st.info("Data harian tidak tersedia.")

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengakses API BMKG: {e}")
    except ValueError:
        st.error("Response bukan JSON yang valid.")

st.divider()

# --- GEMINI AI TIPS ---
API_KEY = st.session_state.get('token_api', '') 
ai_connected = False
try:
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
        ai_connected = True
except:
    pass

def get_simple_tips(kota, suhu, kondisi):
    prompt = f"""
    Berikan tips singkat bahasa Indonesia untuk cuaca di {kota}, suhu {suhu}°C, kondisi {kondisi}.
    Format:
    - Cocok dilakukan: [aktivitas]
    - Tidak cocok: [aktivitas]
    Gunakan emoji. Maksimal 70 kata.
    """
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "AI tidak merespons."
    except:
        return "Gagal terhubung ke AI."

st.subheader("💡 Tips AI")

if ai_connected:
    if st.button("✨ Minta Tips Cuaca", use_container_width=True):
        with st.spinner("Sedang membuat tips..."):
            tips = get_simple_tips(kota, suhu, kondisi)
            st.markdown(
                f"""
                <div style='background-color:#e8f5e9;padding:15px;border-radius:10px;border-left:5px solid #2e7d32;'>
                {tips}
                </div>
                """, unsafe_allow_html=True
            )
else:
    st.warning("Gemini AI belum terhubung (Cek API Key).")

#Untuk LogOut
st.write('')
@st.dialog('Konfirmasi Logout')
def logut_dialog():
    st.write('Apakah anda yakin ingin keluar?')
    st.write('')

    if st.button('ya', use_container_width=True):
        st.session_state.do_logout = True
        st.rerun()

        try:
            st.switch_page("pages/Masuk.py")
        except:
            st.rerun()

st.write('')
if st.button('LogOut', type='primary'):
    logut_dialog()

# --- FOOTER ---
st.markdown("---")
col_pindah1, col_pindah2 = st.columns([3, 1])

with col_pindah1:
    st.markdown("### Bandingkan Cuaca")
    st.caption("Cek selisih suhu dan kelembapan dengan kota lain.")

with col_pindah2:
    st.write("") 
    if st.button("Bandingkan \nSekarang", use_container_width=True):
        try:
            st.switch_page("pages/Perbandingan Cuaca.py") 
        except Exception as e:
            st.error(f"Halaman tidak ditemukan.")

st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)