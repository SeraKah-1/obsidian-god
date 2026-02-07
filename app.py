import streamlit as st
import time

# Import modul backend
from modules.structure_manager import validate_inputs
from modules.generator import generate_note

# --- 1. KONFIGURASI HALAMAN & STATE ---
st.set_page_config(
    page_title="NeuroNote AI", 
    page_icon="🧠", 
    layout="wide"
)

# Inisialisasi Session State
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None

# --- 2. CSS CUSTOM (Dark Mode & Tampilan Rapi) ---
st.markdown("""
<style>
    /* Background & Warna Dasar */
    .stApp {background-color: #0e1117;}
    h1, h2, h3 {color: #7c4dff !important;}
    
    /* Tombol Utama */
    .stButton>button {
        background-color: #7c4dff; 
        color: white; 
        border-radius: 8px; 
        height: 3em; 
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #651fff;
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(124, 77, 255, 0.4);
    }

    /* Text Area Font (Monospace biar struktur terlihat rapi) */
    .stTextArea textarea {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* Info Box di Sidebar */
    .css-1544g2n {
        padding: 1rem;
        background-color: #1e1e1e;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD SECRETS (API KEY) ---
# Mengambil API Key dari .streamlit/secrets.toml
try:
    # Sesuaikan dengan nama variabel di secrets.toml kamu
    # Biasanya: [general] GOOGLE_API_KEY = "..."
    if "general" in st.secrets:
        api_key = st.secrets["general"]["GOOGLE_API_KEY"]
    else:
        api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ File `.streamlit/secrets.toml` tidak ditemukan! Buat file tersebut dan isi API Key Google Anda.")
    st.stop()
except KeyError:
    st.error("⚠️ API Key belum diset di secrets.toml. Pastikan formatnya benar.")
    st.stop()

# --- 4. SIDEBAR (PENGATURAN AI) ---
with st.sidebar:
    st.title("🧠 NeuroNote")
    st.caption("v2.1 • Strict Structure Mode")
    
    st.divider()
    
    st.subheader("🤖 Konfigurasi Model")
    
    # 1. Pilihan Model (Lengkap)
    model_options = [
        "gemma-3-27b-it",  # Paling Cepat & Baru (Experimental)
        "gemini-3-flash-preview",        # Paling Pintar (Context Window Besar)
        "gemini-2.5-flash",      # Standard Cepat & Stabil
        "gemini-2.5-flash-lite",   # Versi Ringan
        "gemini-2.5-pro",
    ]
    
    model_choice = st.selectbox(
        "Pilih Model:", 
        model_options,
        index=0,
        help="Gunakan 'Pro' untuk analisis mendalam, 'Flash' untuk kecepatan."
    )
    
    # 2. Pengaturan Kreativitas (Temperature)
    st.markdown("<br>", unsafe_allow_html=True)
    temperature = st.slider(
        "🌡️ Temperature (Kreativitas):",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.1,
        help="Rendah (0.2) = Sangat patuh struktur. Tinggi (0.7) = Lebih kreatif membuat analogi."
    )
    
    st.divider()
    
    with st.expander("💡 Cara Penggunaan"):
        st.markdown("""
        1. **Siapkan Kerangka:** Minta ChatGPT/Gemini Web buatkan outline materi yang detail.
        2. **Copy-Paste:** Tempel outline ke kolom kanan.
        3. **Isi Materi (Opsional):** Jika ada sumber khusus (PDF/Jurnal), tempel teksnya di kiri.
        4. **Generate:** NeuroNote akan mengisi "daging" ke dalam "tulang" tersebut.
        """)

# --- 5. UI UTAMA (Input Data) ---
st.title("Medical Note Generator")
st.caption("Human Structure × AI Content • Obsidian Ready")

# Layout 2 Kolom
col1, col2 = st.columns([1, 1])

with col1:
    # Input Topik & Materi Tambahan
    topic = st.text_input("🩺 Judul Topik / Penyakit:", placeholder="Contoh: Gagal Jantung Kongestif")
    material = st.text_area(
        "📚 Materi Mentah / Referensi (Opsional):", 
        height=300, 
        help="Jika kosong, AI menggunakan databasenya sendiri. Jika diisi, AI akan memprioritaskan teks ini.",
        placeholder="Paste teks dari buku ajar, jurnal, atau catatan kuliah di sini untuk diolah..."
    )

with col2:
    # Input Struktur (FOKUS UTAMA)
    structure = st.text_area(
        "📋 Struktur Bab (Wajib Diisi):", 
        height=375, # Sedikit lebih tinggi biar enak lihat outline panjang
        placeholder="1. Definisi & Klasifikasi\n2. Etiologi & Faktor Risiko\n3. Patofisiologi (Mekanisme)\n4. Manifestasi Klinis\n5. Tata Laksana...",
        help="AI DILARANG mengubah urutan ini. Dia hanya akan mengisi konten di bawah judul-judul ini."
    )

# Tombol Eksekusi
generate_btn = st.button("🚀 ISI STRUKTUR & GENERATE", use_container_width=True)

# --- 6. LOGIKA EKSEKUSI ---
if generate_btn:
    # A. Validasi Input dulu
    is_valid, error_msg = validate_inputs(topic, structure)
    
    if not is_valid:
        st.warning(f"⚠️ {error_msg}")
    else:
        # B. Proses Generate
        with st.status("Sedang bekerja...", expanded=True) as status:
            st.write("🔒 Mengunci Struktur User...")
            st.write(f"🤖 Menghubungi {model_choice}...")
            st.write("💉 Menyuntikkan Analisis Deep Dive & Klinis...")
            
            start_time = time.time()
            
            # Panggil Backend (generator.py)
            # Perhatikan: Kita kirim temperature juga sekarang (nanti update generator.py sedikit untuk terima param ini, atau biarkan default)
            # Untuk sekarang kita kirim parameter standar dulu.
            result = generate_note(api_key, model_choice, topic, structure, material)
            
            # C. Cek Hasil
            if result.startswith("ERROR_QUOTA"):
                status.update(label="Gagal!", state="error")
                st.error("🚨 KUOTA API HABIS (Error 429). Tunggu sebentar atau ganti akun Google.")
            elif result.startswith("ERROR_SYSTEM"):
                status.update(label="Error Sistem", state="error")
                st.error(f"Terjadi kesalahan: {result}")
            else:
                # SUKSES: Simpan ke Session State
                st.session_state.generated_result = result
                status.update(label="Selesai!", state="complete", expanded=False)
                st.success(f"Catatan selesai dibuat dalam {round(time.time() - start_time, 1)} detik!")

# --- 7. OUTPUT DISPLAY (Hasil) ---
if st.session_state.generated_result:
    st.divider()
    st.subheader("📂 Hasil Output")
    
    # Tabs: Preview Visual vs Source Code
    tab_preview, tab_code = st.tabs(["👁️ Preview Render", "📝 Source Code (Copy ke Obsidian)"])
    
    with tab_preview:
        st.markdown(st.session_state.generated_result)
        
    with tab_code:
        st.info("Klik tombol di pojok kanan atas kotak kode untuk menyalin semua.")
        st.code(st.session_state.generated_result, language="markdown")
    
    # Tombol Download File
    st.download_button(
        label="💾 Download File (.md)",
        data=st.session_state.generated_result,
        file_name=f"{topic.replace(' ', '_')}.md",
        mime="text/markdown",
        type="primary"
    )
