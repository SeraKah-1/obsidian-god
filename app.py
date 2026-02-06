import streamlit as st
import google.generativeai as genai

# Import modul buatan kita sendiri
from modules import prompts
from modules import database as db
from modules.formatter import convert_tags_to_obsidian

# --- CONFIG ---
st.set_page_config(page_title="MedWiki Crowdsourced", page_icon="🧬", layout="wide")

# Setup Google Gemini
try:
    genai.configure(api_key=st.secrets["general"]["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API Key Google belum diset di .streamlit/secrets.toml")

# --- CORE LOGIC ---
def process_new_topic(topic):
    """
    Fungsi ini menjalankan orkestrasi:
    Prompting -> AI Generating -> Formatting (Tag to Obsidian) -> Saving DB
    """
    # 1. Tentukan Struktur Bab (Bisa dibuat dinamis nanti)
    structure = """
    1. Definisi & Klasifikasi (The Map)
    2. Patofisiologi & Mekanisme Molekuler (The Deep Dive)
    3. Manifestasi Klinis & Red Flags (The Clinical Anchor)
    """
    
    # 2. Ambil Prompt "Trojan Horse"
    final_prompt = prompts.get_main_prompt(topic, structure)
    
    # 3. Panggil Koki (Gemini)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    with st.spinner(f"🧠 Sedang membedah molekuler '{topic}'..."):
        try:
            response = model.generate_content(final_prompt)
            raw_text = response.text
            
            # 4. POST-PROCESSING (The Magic Step)
            # Ubah tag <<<...>>> menjadi format Obsidian > [!note]
            clean_text = convert_tags_to_obsidian(raw_text)
            
            return clean_text
        except Exception as e:
            st.error(f"Gagal generate: {e}")
            return None

# --- UI FRONTEND ---
st.title("🧬 Medical Knowledge Base")
st.caption("Active Prediction Engine • Crowdsourced • Obsidian Ready")

# Input Area
col1, col2 = st.columns([3, 1])
with col1:
    topic_input = st.text_input("Topik Medis:", placeholder="Contoh: Gagal Jantung Kongestif")
with col2:
    force_regen = st.checkbox("Paksa Generate Ulang", help="Abaikan database, minta AI buat baru.")

# Tombol Eksekusi
if st.button("Bedah Topik Ini 🚀", type="primary"):
    if not topic_input:
        st.warning("Isi dulu topiknya, Dok.")
    else:
        final_content = None
        source_info = ""
        
        # A. STRATEGI: CEK DATABASE DULU
        if not force_regen:
            db_data = db.fetch_note_from_db(topic_input)
            if db_data:
                final_content = db_data['content_md']
                source_info = "⚡ **DATABASE CACHE** (Cepat & Hemat Token)"
                st.toast("Data ditemukan di Supabase!", icon="✅")
        
        # B. STRATEGI: GENERATE JIKA KOSONG / DIPAKSA
        if not final_content:
            final_content = process_new_topic(topic_input)
            if final_content:
                source_info = "🧠 **AI GENERATED** (Fresh from Gemini)"
                # Simpan hasil yang SUDAH DIFORMAT ke Database
                db.save_note_to_db(topic_input, final_content)
                st.toast("Data baru disimpan ke Supabase!", icon="💾")

        # C. TAMPILKAN HASIL
        if final_content:
            st.divider()
            st.markdown(f"<small>{source_info}</small>", unsafe_allow_html=True)
            
            # Render Markdown di Layar
            st.markdown(final_content)
            
            st.divider()
            st.subheader("📂 Siap Masuk Obsidian")
            st.info("Copy kode di bawah, lalu PASTE di Obsidian. Mermaid & Callout akan otomatis aktif.")
            
            # Code block agar user tinggal klik tombol copy
            st.code(final_content, language="markdown")
