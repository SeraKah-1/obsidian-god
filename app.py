import streamlit as st
import time
# Pastikan modul-modul ini ada (kode di bawah)
from modules.structure_manager import validate_inputs
from modules.generator import generate_note

# --- KONFIG HALAMAN ---
st.set_page_config(page_title="NeuroNote AI", page_icon="🧠", layout="wide")

# CSS Custom (Dark Mode Optimized)
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .stButton>button {background-color: #7c4dff; color: white; border-radius: 8px; height: 3em; font-weight: bold;}
    h1 {color: #7c4dff;}
    .stTextArea textarea {font-family: 'Consolas', monospace;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Agar hasil gak hilang) ---
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 NeuroNote")
    api_key = st.text_input("API Key (Google):", type="password", help="Masukkan API Key Gemini di sini")
    model_choice = st.selectbox("Model:", ["gemini-1.5-flash", "gemini-2.0-flash-exp"], index=0)
    st.info("💡 **Workflow:**\n1. Bikin struktur di Gemini Web/ChatGPT.\n2. Paste di 'Struktur Bab'.\n3. Biar tools ini yang isi dagingnya.")

# --- UI UTAMA ---
st.title("Medical Note Generator")
st.caption("Human Structure x AI Content")

col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_input("Judul Topik:", placeholder="Cth: Diabetes Melitus Tipe 2")
    material = st.text_area("Materi Mentah (Opsional):", height=200, help="Paste teks buku/jurnal di sini kalau ada sumber khusus.")

with col2:
    structure = st.text_area("📋 Struktur Bab (Wajib):", height=275, 
                             placeholder="Paste Outline Bab disini...\n1. Definisi\n2. Patofisiologi\n...",
                             help="AI DILARANG mengubah urutan ini. Dia cuma akan mengisi konten di bawah sub-bab ini.")

btn = st.button("🚀 GENERATE CATATAN", use_container_width=True)

if btn:
    # 1. Validasi Input
    is_valid, msg = validate_inputs(topic, structure)
    
    if not api_key:
        st.error("⚠️ Masukkan API Key di sidebar dulu!")
    elif not is_valid:
        st.warning(msg)
    else:
        # 2. Proses
        with st.status("Sedang bekerja...", expanded=True) as status:
            st.write("🔒 Mengunci Struktur User...")
            st.write("💉 Menyuntikkan 'Daging' (Deep Dive & Clinical)...")
            st.write("🎨 Mewarnai Mermaid & Formatting Obsidian...")
            
            start = time.time()
            
            # Panggil Backend Generator
            result = generate_note(api_key, model_choice, topic, structure, material)
            
            # Handling Error dari Backend
            if result.startswith("ERROR_QUOTA"):
                status.update(label="Gagal!", state="error")
                st.error("🚨 KUOTA HABIS (Error 429). Ganti model atau tunggu sebentar.")
            elif result.startswith("ERROR_SYSTEM"):
                status.update(label="Error Sistem!", state="error")
                st.error(result)
            else:
                st.session_state.generated_result = result # Simpan ke session
                status.update(label="Selesai!", state="complete", expanded=False)
                st.success(f"Selesai dalam {round(time.time()-start, 1)} detik!")

# --- OUTPUT DISPLAY ---
if st.session_state.generated_result:
    st.divider()
    
    # Buat Tab biar rapi: Preview (Visual) vs Source Code (Buat Copas)
    tab_preview, tab_code = st.tabs(["👁️ Preview Render", "📝 Source Code (Copy Obsidian)"])
    
    with tab_preview:
        st.markdown(st.session_state.generated_result)
        
    with tab_code:
        st.markdown("Salin kode di bawah ini langsung ke Obsidian:")
        st.code(st.session_state.generated_result, language="markdown")
    
    # Download Button
    st.download_button(
        label="💾 Download File .md", 
        data=st.session_state.generated_result, 
        file_name=f"{topic.replace(' ', '_')}.md",
        mime="text/markdown"
    )
