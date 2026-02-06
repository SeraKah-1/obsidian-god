import streamlit as st
import google.generativeai as genai
import json
import time
import re

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Medical Note AI",
    page_icon="🩺",
    layout="wide"
)

# --- CSS CUSTOM BIAR GANTENG ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #000;
        color: #fff;
        border-radius: 8px;
    }
    .stTextInput>div>div>input {
        border: 2px solid #000;
    }
</style>
""", unsafe_allow_html=True)

# --- SETUP API KEY (DARI SIDEBAR) ---
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key Terhubung!")
    else:
        st.warning("Masukkan API Key dulu.")

# --- ENGINE LOGIC (COPY DARI COLAB) ---
model_flash = genai.GenerativeModel('gemini-2.5-flash')

def clean_mermaid_syntax(text):
    if not text: return ""
    if "```mermaid" in text:
        parts = text.split("```mermaid")
        for i in range(1, len(parts), 2):
            parts[i] = parts[i].replace("(", "[").replace(")", "]").replace("'", "").replace('"', "") 
        text = "```mermaid".join(parts)
    return text

def generate_outline(topic, raw_material=None):
    source_context = f"MATERI: {raw_material[:15000]}" if raw_material else "SUMBER: Knowledge Base."
    prompt = f"""
    ROLE: Dosen Medis. TOPIC: {topic}.
    TUGAS: Buat Outline JSON (Maks 4 Bab).
    ATURAN:
    - JIKA PENYAKIT: ["1. Etiologi", "2. Patofisiologi", "3. Diagnosis", "4. Tatalaksana"]
    - JIKA ALAT/LAB: ["1. Prinsip Dasar", "2. Prosedur", "3. Interpretasi", "4. QC"]
    {source_context}
    OUTPUT: JSON Array String Only.
    """
    try:
        response = model_flash.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return ["1. Konsep Dasar", "2. Mekanisme", "3. Klinis", "4. Tatalaksana"]

def generate_chapter(topic, chapter, raw_material=None):
    source = f"MATERI: {raw_material[:25000]}" if raw_material else "SUMBER: Internal."
    prompt = f"""
    # ROLE: Medical Writer (Obsidian Style)
    TOPIK: {topic}
    BAB: {chapter}
    {source}
    INSTRUKSI:
    Tulis isi bab ini.
    - WAJIB: Gunakan `> [!grid]` untuk gambar.
    - WAJIB: Gunakan `> [!tip]` untuk klinis.
    - WAJIB: Mermaid `graph TD` jika ada proses.
    """
    try:
        time.sleep(2) # Anti-spam
        response = model_flash.generate_content(prompt)
        return clean_mermaid_syntax(response.text)
    except Exception as e:
        return f"> [!fail] Error: {e}"

# --- UI UTAMA ---
st.title("🩺 Hybrid Medical Engine")
st.markdown("Generate catatan medis Obsidian-ready dalam hitungan detik.")

# TABS
tab1, tab2, tab3 = st.tabs(["🔍 Judul Saja", "📂 Upload File", "📝 Custom Outline"])

final_md = ""
topic = ""

# --- TAB 1: JUDUL SAJA ---
with tab1:
    t1_input = st.text_input("Topik Medis:", placeholder="Misal: Gagal Jantung Kongestif")
    if st.button("🚀 Generate (Mode Cepat)") and api_key:
        topic = t1_input
        with st.status("Sedang bekerja...", expanded=True) as status:
            st.write("🏗️ Merancang Outline...")
            outline = generate_outline(topic)
            st.write(f"📋 Struktur: {outline}")
            
            full_content = f"# {topic}\n\n> [!abstract] AI Generated\n\n"
            progress_bar = st.progress(0)
            
            for i, chapter in enumerate(outline):
                st.write(f"✍️ Menulis: {chapter}...")
                content = generate_chapter(topic, chapter)
                full_content += f"\n\n## {chapter}\n\n{content}"
                progress_bar.progress((i + 1) / len(outline))
            
            final_md = full_content
            status.update(label="Selesai!", state="complete", expanded=False)

# --- TAB 2: UPLOAD FILE ---
with tab2:
    uploaded_file = st.file_uploader("Upload Materi (PDF/TXT)", type=['txt', 'md'])
    # Note: Utk PDF butuh library pypdf, utk simpel kita txt dulu atau copy text
    raw_text_input = st.text_area("Atau Paste Teks Materi Disini:", height=200)
    t2_topic = st.text_input("Judul Topik:", key="t2")
    
    if st.button("🚀 Generate (Mode Akurat)") and api_key and t2_topic:
        topic = t2_topic
        raw_mat = raw_text_input # Sederhana dulu
        
        with st.status("Menganalisis Materi...", expanded=True) as status:
            outline = generate_outline(topic, raw_mat)
            st.write(f"📋 Struktur: {outline}")
            full_content = f"# {topic}\n\n> [!abstract] Source: Upload\n\n"
            
            for chapter in outline:
                st.write(f"✍️ {chapter}...")
                content = generate_chapter(topic, chapter, raw_mat)
                full_content += f"\n\n## {chapter}\n\n{content}"
            
            final_md = full_content
            status.update(label="Done!", state="complete")

# --- OUTPUT AREA ---
if final_md:
    st.divider()
    st.subheader("🎉 Hasil Generate")
    st.markdown("Copy kode di bawah dan paste ke Obsidian:")
    st.code(final_md, language="markdown")
    
    # Tombol Download
    st.download_button(
        label="💾 Download .md File",
        data=final_md,
        file_name=f"{topic.replace(' ', '_')}.md",
        mime="text/markdown"
    )
