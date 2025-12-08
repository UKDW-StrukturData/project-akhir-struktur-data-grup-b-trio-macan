import streamlit as st
import base64
from PIL import Image, ImageDraw
import requests
import io
from streamlit.errors import StreamlitAPIException

# Konfigurasi Halaman (Harus di baris pertama setelah import)
st.set_page_config(
    page_title="Prakiraan Cuaca Indonesia",
    page_icon="🌦️",
    layout="centered"
)

# --- MOCKING API KEY (Hanya simulasi jika file apikey.py tidak ada) ---
try:
    from apikey import keykey
except ImportError:
    keykey = "dummy_token_12345"

if 'token_api' not in st.session_state:
    st.session_state['token_api'] = keykey

# --- FUNGSI UTAMA ---

@st.cache_data(show_spinner=False)
def get_base64_from_url(url):
    """
    Mengunduh gambar dari URL dan mengubahnya ke Base64.
    Menggunakan cache agar tidak mendownload ulang setiap rerun.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Cek jika link error
        return base64.b64encode(response.content).decode()
    except Exception as e:
        st.error(f"Gagal memuat background: {e}")
        return None

def set_background_and_style(url):
    """Mengatur CSS untuk background dan styling container utama"""
    bin_str = get_base64_from_url(url)
    
    if bin_str:
        bg_css = f"""
        <style>
        /* Mengatur Background Utama */
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Mengatur Container Putih (Card UI) */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95); /* Sedikit lebih solid */
            border-radius: 15px;
            padding: 3rem;
            max-width: 700px;
            margin-top: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(5px); /* Efek blur di belakang kotak putih */
        }}

        /* Styling Judul agar lebih menarik */
        h1 {{
            color: #2c3e50;
            font-family: 'Helvetica Neue', sans-serif;
        }}
        
        /* Styling Tombol Primary */
        div.stButton > button:first-child {{
            border-radius: 10px;
            height: 3em;
            font-weight: bold;
        }}
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)

# --- LOAD ASSETS ---

# 1. Setup Background
BG_URL = "https://png.pngtree.com/thumb_back/fh260/background/20231012/pngtree-aesthetic-sky-fluffy-white-clouds-on-a-blue-background-image_13642352.png"
set_background_and_style(BG_URL)

# 2. Setup Logo (Dengan Fallback Generator)
def load_logo():
    try:
        # Coba load file lokal
        return Image.open("image.png")
    except FileNotFoundError:
        # Jika tidak ada, buat logo dummy secara otomatis
        img = Image.new('RGB', (200, 200), color='#3498db')
        d = ImageDraw.Draw(img)
        # Gambar matahari sederhana
        d.ellipse([50, 50, 150, 150], fill='#f1c40f', outline=None)
        return img

logo_img = load_logo()

# Menampilkan Logo di Sidebar (Fitur baru st.logo)
# Catatan: st.logo butuh Streamlit versi 1.35+, jika error kita skip
if hasattr(st, 'logo'):
    st.logo(image=logo_img, icon_image=logo_img)

# --- KONTEN HALAMAN ---

# Menggunakan kolom kosong di kiri/kanan untuk centering (opsional, karena layout="centered")
col_spacer1, col_content, col_spacer2 = st.columns([0.5, 3, 0.5])

with col_content:
    # Menampilkan Logo di tengah
    st.image(logo_img, width=150)
    
    st.title('Prakiraan Cuaca ID')
    st.markdown("""
    **Selamat Datang!** Dapatkan informasi cuaca terkini, akurat, dan terpercaya untuk seluruh wilayah Indonesia.
    """)
    
    st.divider() # Garis pemisah estetis
    
    # Layout Tombol
    col_btn1, col_btn2 = st.columns(2, gap="medium")
    
    with col_btn1:
        if st.button('🔐 Masuk', use_container_width=True, type="primary"):
            # Cek apakah file page ada sebelum switch untuk menghindari error runtime
            try:
                st.switch_page('pages/Masuk.py')
            except StreamlitAPIException:
                st.warning("Halaman 'pages/Masuk.py' belum dibuat.")
                
    with col_btn2:
        if st.button('📝 Mendaftar', use_container_width=True):
            try:
                st.switch_page('pages/Mendaftar.py')
            except:
                 st.warning("Halaman 'pages/Mendaftar.py' belum dibuat.")

# Footer Sederhana
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em; margin-top: 50px;'>
        © 2024 WeatherApp Indonesia. All rights reserved.
    </div>
    """, 
    unsafe_allow_html=True
)