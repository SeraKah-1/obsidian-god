import streamlit as st
import time

# Kita import fungsi dari modul yang AKAN kita buat setelah ini
# Jangan khawatir jika masih merah/error di editor, itu karena file modules/ belum dibuat.
from modules.structure_manager import validate_inputs
from modules.generator import generate_note

# --- 1. KONFIGURASI HALAMAN & STATE ---
st.set_page_config(
    page_title="NeuroNote AI", 
    page_icon="🧠", 
    layout="wide"
)

# Inisialisasi Session State (Agar hasil generate tidak hilang saat klik tab/tombol lain)
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
    }
    .stButton>button:hover {
        background-color: #651fff;
        color: white;
    }

    /* Text Area Font (Monospace biar struktur terlihat rapi) */
    .stTextArea textarea {
        font-family: 'Consolas', 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (Pengaturan) ---
with st.sidebar:
    st.title("🧠 NeuroNote")
    st.caption("v2.0 • Strict Structure Mode")
    
    st.divider()
    
    # Input API Key
    api_key = st.text_input("🔑 Google AI API Key:", type="password", help="Wajib diisi untuk mengakses Gemini.")
    
    # Pilihan Model
    model_choice = st.selectbox(
        "🤖 Model AI:", 
        ["gemini-1.5-flash", "gemini-2.0-flash-exp"], 
        index=0,
        help="Gunakan Flash untuk kecepatan, 2.0 untuk logika yang lebih tajam."
    )
    
    st.divider()
    st.info(
        "**💡 Cara Pakai:**\n"
        "1. Minta ChatGPT/Gemini Web buatkan outline materi.\n"
        "2. Copy outline tersebut.\n"
        "3. Paste di kolom 'Struktur Bab' di kanan.\n"
        "4. Tools ini akan mengisi kontennya."
    )

# --- 4. UI UTAMA (Input Data) ---
st.title("Medical Note Generator")
st.caption("Human Structure × AI Content • Obsidian Ready")

# Layout 2 Kolom
col1, col2 = st.columns([1, 1])

with col1:
    # Input Topik & Materi Tambahan
    topic = st.text_input("🩺 Judul Topik / Penyakit:", placeholder="Contoh: Gagal Jantung Kongestif")
    material = st.text_area(
        "📚 Materi Mentah / Referensi (Opsional):", 
        height=200, 
        help="Jika kosong, AI akan menggunakan pengetahuan umumnya. Jika diisi, AI akan memprioritaskan teks ini.",
        placeholder="Paste teks dari buku ajar, jurnal, atau catatan kuliah di sini..."
    )

with col2:
    # Input Struktur (FOKUS UTAMA)
    structure = st.text_area(
        "📋 Struktur Bab (Wajib Diisi):", 
        height=275, 
        placeholder="1. Definisi & Klasifikasi\n2. Etiologi & Faktor Risiko\n3. Patofisiologi (Mekanisme)\n4. Manifestasi Klinis\n5. Tata Laksana...",
        help="AI DILARANG mengubah urutan ini. Dia hanya akan mengisi konten di bawah judul-judul ini."
    )

# Tombol Eksekusi
generate_btn = st.button("🚀 ISI STRUKTUR & GENERATE", use_container_width=True)

# --- 5. LOGIKA EKSEKUSI ---
if generate_btn:
    # A. Validasi Input dulu
    is_valid, error_msg = validate_inputs(topic, structure)
    
    if not api_key:
        st.error("⚠️ API Key belum diisi di Sidebar!")
    elif not is_valid:
        st.warning(f"⚠️ {error_msg}")
    else:
        # B. Proses Generate
        with st.status("Sedang bekerja...", expanded=True) as status:
            st.write("🔒 Mengunci Struktur User...")
            st.write("💉 Menyuntikkan Analisis Deep Dive & Klinis...")
            st.write("🎨 Mewarnai Diagram Mermaid & Formatting...")
            
            start_time = time.time()
            
            # Panggil Backend (generator.py)
            result = generate_note(api_key, model_choice, topic, structure, material)
            
            # C. Cek Hasil
            if result.startswith("ERROR_QUOTA"):
                status.update(label="Gagal!", state="error")
                st.error("🚨 KUOTA API HABIS (Error 429). Tunggu sebentar atau ganti akun.")
            elif result.startswith("ERROR_SYSTEM"):
                status.update(label="Error Sistem", state="error")
                st.error(f"Terjadi kesalahan: {result}")
            else:
                # SUKSES: Simpan ke Session State
                st.session_state.generated_result = result
                status.update(label="Selesai!", state="complete", expanded=False)
                st.success(f"Catatan selesai dibuat dalam {round(time.time() - start_time, 1)} detik!")

# --- 6. OUTPUT DISPLAY (Hasil) ---
# Tampilkan hanya jika ada hasil di session state
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
