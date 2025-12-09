import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader 
from io import BytesIO
from PIL import Image

logo = Image.open("image.png")
icon = Image.open("image.png")
st.logo(image=logo,size="large",icon_image=icon)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(logo, use_container_width=True)


if 'sudah_login' not in st.session_state or st.session_state['sudah_login'] == False:
    st.error("Akses Ditolak!")
    st.markdown("Silakan login terlebih dahulu untuk membandingkan cuaca.")
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("Kembali ke Menu Utama"):
            st.switch_page("main.py")

    
    st.stop()

# Style CSS agar mirip screenshot (Dark Mode support)
st.markdown("""
<style>
    .stSuccess {
        background-color: #1e3a2f;
        color: #4cdbb9;
        border: 1px solid #2e8b57;
    }
</style>
""", unsafe_allow_html=True)

st.title("Perbandingan Cuaca Dua Wilayah")
st.caption("Membandingkan prakiraan cuaca (Waktu Terdekat dengan Saat Ini) dari dua wilayah.")

# --- 1. LOAD DATA WILAYAH ---
try:
    df_kode = pd.read_csv(
        "kode_wilayah.csv", 
        header=None, 
        names=["kode", "nama", "level"], 
        dtype={"kode": str},
        on_bad_lines='skip' 
    )
    df_kode = df_kode[df_kode["level"] == "adm4"]
    list_wilayah = df_kode["nama"].tolist()
except Exception as e:
    st.error(f"Gagal memuat database wilayah: {e}")
    list_wilayah = []

# --- 2. INPUT USER ---
col_input1, col_input2 = st.columns(2)

with col_input1:
    wilayah1 = st.selectbox("Pilih Wilayah Pertama", list_wilayah, index=0 if list_wilayah else None)

with col_input2:
    default_idx_2 = 1 if len(list_wilayah) > 1 else 0
    wilayah2 = st.selectbox("Pilih Wilayah Kedua", list_wilayah, index=default_idx_2)

# --- FUNGSI AMBIL DATA BMKG ---
def get_current_weather_bmkg(nama_wilayah):
    try:
        row = df_kode[df_kode["nama"] == nama_wilayah]
        if row.empty: return None
        
        adm4 = row["kode"].values[0]
        url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
        
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        forecast_data = data.get("data", [])
        if not forecast_data: return None

        waktu_sekarang = datetime.now()
        data_terdekat = None
        selisih_terkecil = float('inf')

        for entry in forecast_data:
            cuaca_list = entry.get("cuaca", [])
            for hari in cuaca_list:
                for jam in hari:
                    if isinstance(jam, dict):
                        str_waktu = jam.get("local_datetime")
                        if str_waktu:
                            try:
                                waktu_prakiraan = datetime.strptime(str_waktu, "%Y-%m-%d %H:%M:%S")
                                selisih = abs((waktu_sekarang - waktu_prakiraan).total_seconds())
                                if selisih < selisih_terkecil:
                                    selisih_terkecil = selisih
                                    data_terdekat = jam
                            except ValueError: continue
        
        if data_terdekat:
            return {
                "Jam Referensi": data_terdekat.get("local_datetime", "-"),
                "Cuaca": data_terdekat.get("weather_desc", "-"),
                "Suhu (°C)": float(data_terdekat.get("t", 0)),
                "Kelembapan (%)": float(data_terdekat.get("hu", 0)),
                "Kecepatan Angin (km/j)": float(data_terdekat.get("ws", 0)),
                "Arah Angin": data_terdekat.get("wd", "-"),
            }
        return None
    except: return None

# --- 3. EKSEKUSI TOMBOL ---
if st.button("Bandingkan Cuaca Saat Ini", type="primary"):
    if not wilayah1 or not wilayah2:
        st.warning("Mohon pilih kedua wilayah terlebih dahulu.")
    else:
        with st.spinner(f"Sedang membandingkan data..."):
            data_w1 = get_current_weather_bmkg(wilayah1)
            data_w2 = get_current_weather_bmkg(wilayah2)

        if not data_w1 or not data_w2:
            st.error("Data cuaca tidak ditemukan.")
        else:
            # === TAMPILAN DI LAYAR ===
            st.success(f"Estimasi Waktu Data: {data_w1['Jam Referensi']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(wilayah1)
                st.dataframe(pd.DataFrame([data_w1]), hide_index=True)
            with col2:
                st.subheader(wilayah2)
                st.dataframe(pd.DataFrame([data_w2]), hide_index=True)

            st.markdown("---")
            st.subheader("Grafik Perbandingan")

            # === MEMBUAT GRAFIK ===
            numeric_params = ["Suhu (°C)", "Kelembapan (%)", "Kecepatan Angin (km/j)"]
            fig, axs = plt.subplots(1, 3, figsize=(12, 4)) # Ukuran disesuaikan
            colors = ['#E57373', '#64B5F6'] # Merah pastel & Biru pastel mirip screenshot

            for i, param in enumerate(numeric_params):
                ax = axs[i]
                nilai1 = data_w1[param]
                nilai2 = data_w2[param]
                
                ax.bar([wilayah1, wilayah2], [nilai1, nilai2], color=colors)
                ax.set_title(param, fontsize=10)
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
                # Menambah label angka di atas batang
                ax.text(0, nilai1, f"{nilai1}", ha='center', va='bottom', fontsize=9, fontweight='bold')
                ax.text(1, nilai2, f"{nilai2}", ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.tight_layout()
            st.pyplot(fig) # Tampilkan di Layar

            # === SIMPAN GRAFIK KE MEMORY UNTUK PDF ===
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)

            st.markdown("---")
            st.subheader("Analisis Singkat")

            # Variabel untuk menampung teks analisis (biar bisa diprint ke PDF)
            analisis_text = []

            def compare_stats(val1, val2, label, higher_is_better=True):
                v1, v2 = float(val1), float(val2)
                if v1 == v2:
                    msg = f"{label}: Setara ({v1})"
                    st.info(msg)
                else:
                    is_w1_better = (v1 > v2) if higher_is_better else (v1 < v2)
                    winner = wilayah1 if is_w1_better else wilayah2
                    diff = abs(v1 - v2)
                    msg = f"{label}: {winner} lebih unggul (Selisih {diff:.1f})"
                    st.success(msg) # Tampilan hijau di layar
                
                analisis_text.append(msg) # Simpan ke list untuk PDF

            compare_stats(data_w1["Suhu (°C)"], data_w2["Suhu (°C)"], "Suhu (Lebih Panas)")
            compare_stats(data_w1["Kelembapan (%)"], data_w2["Kelembapan (%)"], "Kelembapan (Lebih Rendah)", higher_is_better=False)
            compare_stats(data_w1["Kecepatan Angin (km/j)"], data_w2["Kecepatan Angin (km/j)"], "Angin (Lebih Kencang)")

            # === MEMBUAT PDF ===
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            
            # 1. Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Laporan Perbandingan Cuaca")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Waktu Cetak: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            y_pos = height - 100
            
            # 2. Data Tabel (Manual Text)
            def print_wilayah_pdf(nama, data, y):
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"Wilayah: {nama}")
                y -= 20
                c.setFont("Helvetica", 10)
                for k, v in data.items():
                    c.drawString(70, y, f"{k}: {v}")
                    y -= 15
                return y - 10

            y_pos = print_wilayah_pdf(wilayah1, data_w1, y_pos)
            y_pos = print_wilayah_pdf(wilayah2, data_w2, y_pos)

            # 3. Menempelkan Grafik
            y_pos -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_pos, "Grafik Perbandingan:")
            y_pos -= 210 # Siapkan ruang untuk gambar

            try:
                img_chart = ImageReader(img_buffer)
                # Mengatur posisi gambar (X, Y, Lebar, Tinggi)
                # Y di ReportLab dihitung dari Bawah ke Atas
                c.drawImage(img_chart, 50, y_pos, width=500, height=200, preserveAspectRatio=True)
            except Exception as e:
                c.drawString(50, y_pos, "Gagal memuat grafik.")

            # 4. Menulis Analisis
            y_pos -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_pos, "Hasil Analisis:")
            y_pos -= 20
            c.setFont("Helvetica", 10)
            
            for line in analisis_text:
                c.drawString(60, y_pos, f"• {line}")
                y_pos -= 15

            c.save()
            pdf_buffer.seek(0)
            
            st.markdown("---")
            st.download_button(
                label="Unduh Data Perbandingan Cuaca",
                data=pdf_buffer,
                file_name=f"Laporan_{wilayah1}_{wilayah2}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if st.button("Kembali", type="primary"):
    st.switch_page("main.py")

st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2025 HAWA Trio Macan. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)