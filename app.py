import streamlit as st
import google.generativeai as genai
from modules import prompts
from modules import database as db

# 1. Konfigurasi Halaman & API
st.set_page_config(page_title="MedWiki Crowdsourced", page_icon="🧬", layout="wide")

try:
    genai.configure(api_key=st.secrets["general"]["GOOGLE_API_KEY"])
except Exception as e:
    st.error("⚠️ Lupa masukin API Key Google di secrets.toml ya?")

# 2. Fungsi Utama: Generate Materi Baru (The Chef)
def generate_new_material(topic):
    # Struktur standar (bisa dikembangkan nanti)
    structure = """
    1. Definisi & Patofisiologi
    2. Etiologi & Faktor Risiko
    3. Manifestasi Klinis (Tanda & Gejala)
    4. Diagnosis & Pemeriksaan Penunjang
    5. Tatalaksana & Farmakologi
    """
    
    # Ambil prompt rahasia "Trojan Horse"
    final_prompt = prompts.get_main_prompt(topic, structure, "General Medical Knowledge")
    
    # Panggil Gemini
    model = genai.GenerativeModel('gemini-1.5-flash') # Pakai Flash biar cepat & murah
    with st.spinner(f"🧠 Sedang meracik materi '{topic}' dari nol... (Sabar ya)"):
        response = model.generate_content(final_prompt)
        return response.text

# 3. UI Frontend
st.title("🧬 Medical Knowledge Base")
st.caption("Crowdsourced by AI, Saved for Humanity.")

# Input User
col1, col2 = st.columns([3, 1])
with col1:
    topic_input = st.text_input("Mau belajar apa hari ini?", placeholder="Contoh: Gagal Jantung Kongestif")
with col2:
    # Opsi buat kalau user merasa data di database jelek/salah
    force_regen = st.checkbox("Paksa Generate Ulang", help="Centang ini kalau mau ignore database dan minta AI bikin baru.")

# Tombol Aksi
if st.button("Pelajari Sekarang 🚀", type="primary"):
    if not topic_input:
        st.warning("Isi topiknya dulu dong, Dok.")
    else:
        content_to_display = None
        source_label = ""
        
        # --- LOGIKA "CEK DATABASE DULU" ---
        
        # 1. Cek DB jika user TIDAK mencentang "Paksa Generate"
        if not force_regen:
            db_data = db.fetch_note_from_db(topic_input)
            
            if db_data:
                # KASUS A: Barang ada di Gudang
                content_to_display = db_data['content_md']
                source_label = "⚡ Diambil dari Database (Hemat Token!)"
                st.toast("Materi ditemukan di database! Loading instan.", icon="⚡")
        
        # 2. Jika tidak ketemu di DB ATAU User maksa generate ulang
        if not content_to_display:
            try:
                # KASUS B: Barang kosong, panggil AI
                generated_text = generate_new_material(topic_input)
                
                if generated_text:
                    content_to_display = generated_text
                    source_label = "🧠 Baru saja digenerate oleh AI"
                    
                    # Simpan ke Database buat user berikutnya!
                    db.save_note_to_db(topic_input, generated_text)
                    st.toast("Materi baru berhasil disimpan ke Supabase!", icon="💾")
            except Exception as e:
                st.error(f"Yah error waktu generate: {e}")

        # --- TAMPILAN HASIL ---
        
        if content_to_display:
            st.divider()
            st.info(f"Sumber: {source_label}")
            
            # Render Markdown Cantik
            st.markdown(content_to_display)
            
            st.divider()
            
            # --- FITUR OBSIDIAN (COPY PASTE) ---
            st.subheader("📂 Simpan ke Obsidian")
            st.write("Klik ikon **Copy** di pojok kanan kotak bawah ini, lalu Paste di Obsidianmu.")
            
            # Tampilkan raw markdown di dalam code block biar tombol copy muncul otomatis
            st.code(content_to_display, language="markdown")
