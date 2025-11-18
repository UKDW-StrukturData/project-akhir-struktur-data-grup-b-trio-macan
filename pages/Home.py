import streamlit as st
import pandas as pd

# Judul aplikasi
st.title("🌤️ Weather Forecast Dashboard")

# Data untuk 5 hari forecast
st.header("📅 5 Days Forecast")
forecast_data = {
    "Day": ["Friday", "Saturday", "Sunday", "Monday", "Tuesday"],
    "Date": ["1 Sep", "2 Sep", "3 Sep", "4 Sep", "5 Sep"],
    "Temperature": ["20°C", "22°C", "27°C", "18°C", "16°C"]
}

# Tampilkan data forecast dalam tabel
forecast_df = pd.DataFrame(forecast_data)
st.dataframe(forecast_df, use_container_width=True)

# Garis pemisah
st.divider()

# Weather Details
st.header("📊 Weather Details")

# Buat 4 kolom untuk details
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Fahrenheit", "72°")
with col2:
    st.metric("Pressure", "134 mph")
with col3:
    st.metric("UV Index", "0.2")
with col4:
    st.metric("Humidity", "48%")

# Garis pemisah
st.divider()

# Calendar Section
st.header("📆 Calendar - August 2020")

# Info cuaca hari ini
st.write("⛅ Partly Cloudy - 72°F")

# Tampilkan kalender sederhana
calendar_data = {
    "Mon": ["3", "7", "14", "21", "28"],
    "Tue": ["1", "8", "15", "22", "29"],
    "Wed": ["2", "9", "16", "23", "30"],
    "Thu": ["3", "10", "17", "24", "1"],
    "Fri": ["4", "11", "18", "25", "2"],
    "Sat": ["5", "12", "19", "26", ""],
    "Sun": ["6", "13", "20", "27", ""]
}

# Tampilkan kalender sebagai tabel
calendar_df = pd.DataFrame(calendar_data)
st.table(calendar_df)

# Tandai tanggal hari ini
st.caption("Note: Today is August 15, 2020")

# Garis pemisah
st.divider()

# Hourly Forecast
st.header("🕒 Hourly Forecast")

# Data hourly forecast
hourly_data = {
    "Time": ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
    "Temperature": ["24°C", "28°C", "27°C", "27°C", "25°C", "22°C"],
    "Wind Speed": ["2 km/h", "3 km/h", "2 km/h", "2 km/h", "3 km/h", "3 km/h"]
}

# Tampilkan hourly forecast dalam tabel
hourly_df = pd.DataFrame(hourly_data)
st.dataframe(hourly_df, use_container_width=True)

# Tambahkan chart sederhana untuk suhu per jam
st.subheader("📈 Temperature Chart")
chart_data = pd.DataFrame({
    "Time": [10, 12, 14, 16, 18, 20],
    "Temperature": [24, 28, 27, 27, 25, 22]
})
st.line_chart(chart_data.set_index("Time"))

# Informasi tambahan
st.sidebar.title("About This App")
st.sidebar.write("""
This is a simple weather dashboard built with Streamlit.

**Features:**
- 5-day weather forecast
- Current weather details
- Calendar view
- Hourly temperature predictions

**Built with:**
- Python
- Streamlit
- Pandas
""")

st.sidebar.info("Made with ❤️ using Streamlit")