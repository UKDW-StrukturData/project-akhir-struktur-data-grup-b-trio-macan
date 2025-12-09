import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.title("📊 Perbandingan Data Cuaca")

# === LOAD DROPDOWN KOTA ===
csv_path = "kode_wilayah.csv"

# CSV kamu TIDAK punya header → buat header manual
df_kota = pd.read_csv(csv_path, header=None, names=["adm4", "nama"])

city_names = df_kota["nama"].tolist()
st.write("Pilih kota untuk perbandingan:")

kota1 = st.selectbox("Kota Pertama", city_names, key="kota1")
kota2 = st.selectbox("Kota Kedua", city_names, key="kota2")

# Mapping adm4 dari CSV
def get_adm4(kota):
    return df_kota[df_kota["nama"] == kota]["adm4"].values[0]

# === FETCH DATA cuaca ===
def get_weather(adm4):
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["data"][0]["cuaca"][0]
        return {
            "Suhu": data["t"],
            "Kelembaban": data["hu"],
            "Kecepatan Angin": data["ws"]
        }
    else:
        st.error("Gagal mengambil data dari API")
        return None

btn = st.button("Bandingkan Cuaca")

if btn:
    data1 = get_weather(get_adm4(kota1))
    data2 = get_weather(get_adm4(kota2))

    if data1 and data2:
        st.subheader("📌 Hasil Perbandingan Cuaca")

        df_compare = pd.DataFrame([data1, data2], index=[kota1, kota2])
        st.table(df_compare)

        # === Grafik per parameter ===
        for parameter in df_compare.columns:
            fig, ax = plt.subplots()
            ax.bar(df_compare.index, df_compare[parameter])
            ax.set_title(f"Perbandingan {parameter}")
            st.pyplot(fig)

        # ========= EXPORT PDF ==========  
        def generate_pdf():
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, height - 40, "Laporan Perbandingan Cuaca BMKG")
            c.setFont("Helvetica", 10)
            c.drawString(30, height - 60, f"{kota1} vs {kota2}")

            y = height - 100
            c.setFont("Helvetica", 11)

            for param in df_compare.columns:
                val1 = df_compare[param][kota1]
                val2 = df_compare[param][kota2]
                c.drawString(30, y, f"{param}:")
                y -= 15
                c.drawString(50, y, f"{kota1}: {val1}")
                y -= 15
                c.drawString(50, y, f"{kota2}: {val2}")
                y -= 25

            # Screenshot grafik terakhir
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format="png")
            img_buffer.seek(0)
            c.drawImage(ImageReader(img_buffer), 30, 100, width=350, preserveAspectRatio=True)

            c.showPage()
            c.save()
            buffer.seek(0)
            return buffer

        pdf_buffer = generate_pdf()
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name="laporan_cuaca.pdf",
            mime="application/pdf"
        )

        # === Notifikasi indikator warna ===
        def warning_color(temp):
            if temp > 32:
                return "🔥 Suhu tinggi"
            elif temp < 24:
                return "❄ Suhu rendah"
            else:
                return "🌤 Normal"

        st.info(f"{kota1}: {warning_color(data1['Suhu'])}")
        st.info(f"{kota2}: {warning_color(data2['Suhu'])}")
