import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

API_KEY = "MASUKKAN_API_KEY_KAMU"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

st.set_page_config(page_title="Perbandingan Cuaca", page_icon="🌦")

# MODE DARK/LIGHT
mode = st.sidebar.radio("🌗 Mode Tampilan", ["Light", "Dark"])
if mode == "Dark":
    st.markdown("<style>body{background-color:#1E1E1E;color:white;}</style>", unsafe_allow_html=True)

st.title("🌦️ Perbandingan Cuaca Dua Kota")

#  PILIH KOTA DARI CSV 
df_kota = pd.read_csv("kode_wilayah.csv")
list_kota = df_kota["nama_kota"].tolist()

city1 = st.selectbox("Pilih Kota Pertama:", list_kota, index=0)
city2 = st.selectbox("Pilih Kota Kedua:", list_kota, index=1)


def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    return requests.get(BASE_URL, params=params).json()


def format_time(timestamp, offset):
    tz = pytz.FixedOffset(offset // 60)
    return datetime.utcfromtimestamp(timestamp).astimezone(tz).strftime("%H:%M:%S")


# ACTION BUTTON
if st.button("Bandingkan Cuaca"):
    data1 = get_weather(city1)
    data2 = get_weather(city2)

    if data1.get("cod") != 200 or data2.get("cod") != 200:
        st.error("Data kota tidak ditemukan!")
    else:
        cuaca1 = {
            "Jam Lokal": format_time(data1["dt"], data1["timezone"]),
            "Suhu (°C)": data1["main"]["temp"],
            "Kelembapan (%)": data1["main"]["humidity"],
            "Kecepatan Angin (m/s)": data1["wind"]["speed"],
            "Jarak Pandang (m)": data1.get("visibility", "-")
        }

        cuaca2 = {
            "Jam Lokal": format_time(data2["dt"], data2["timezone"]),
            "Suhu (°C)": data2["main"]["temp"],
            "Kelembapan (%)": data2["main"]["humidity"],
            "Kecepatan Angin (m/s)": data2["wind"]["speed"],
            "Jarak Pandang (m)": data2.get("visibility", "-")
        }

        col1, col2 = st.columns(2)
        col1.subheader(city1)
        col1.table(pd.DataFrame(cuaca1, index=[0]))
        col2.subheader(city2)
        col2.table(pd.DataFrame(cuaca2, index=[0]))

        st.markdown("---")
        st.subheader("📊 Grafik Perbandingan")

        numeric_params = ["Suhu (°C)", "Kelembapan (%)", "Kecepatan Angin (m/s)", "Jarak Pandang (m)"]

        for param in numeric_params:
            fig, ax = plt.subplots()
            ax.bar([city1, city2], [cuaca1[param], cuaca2[param]])
            ax.set_title(param)
            st.pyplot(fig)

        st.markdown("---")
        st.subheader("🏆 Analisis Pemenang")
        def winner(p1, p2, text, higher=True):
            if p1 == p2:
                st.info(f"- {text}: Sama")
            else:
                pemenang = city1 if (p1 > p2) == higher else city2
                st.success(f"- {text}: **{pemenang} lebih unggul**")

        winner(cuaca1["Suhu (°C)"], cuaca2["Suhu (°C)"], "Suhu")
        winner(cuaca1["Kelembapan (%)"], cuaca2["Kelembapan (%)"], "Kelembapan", False)
        winner(cuaca1["Kecepatan Angin (m/s)"], cuaca2["Kecepatan Angin (m/s)"], "Kecepatan Angin")
        winner(cuaca1["Jarak Pandang (m)"], cuaca2["Jarak Pandang (m)"], "Jarak Pandang")

        st.markdown("---")

        #  EXPORT PDF 
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)

        c.drawString(50, 800, f"Laporan Perbandingan Cuaca {city1} vs {city2}")
        y = 770
        for k, v in cuaca1.items():
            c.drawString(50, y, f"{k} {city1}: {v}")
            y -= 15
        y -= 10
        for k, v in cuaca2.items():
            c.drawString(50, y, f"{k} {city2}: {v}")
            y -= 15

        c.save()
        pdf_buffer.seek(0)

        st.download_button(
            label="📥 Download Laporan PDF",
            data=pdf_buffer,
            file_name=f"Cuaca_{city1}_vs_{city2}.pdf",
            mime="application/pdf"
        )
