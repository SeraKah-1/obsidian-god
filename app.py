import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="NeuroNote Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM (OBSIDIAN VIBES) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextArea textarea {
        background-color: #1a1c24;
        color: #e6e6e6;
        border: 1px solid #4a4a4a;
    }
    .stButton>button {
        width: 100%;
        background-color: #7c4dff;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .stButton>button:hover {
        background-color: #651fff;
    }
    .stSuccess {
        background-color: #1b5e20;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: API KEY & SETTINGS ---
with st.sidebar:
    st.title("🧠 NeuroNote")
    st.markdown("Engine Medis Berbasis Struktur Kognitif.")
    
    st.divider()
    
    # Input API Key
    api_key = st.text_input("🔑 Google AI API Key:", type="password", help="Ambil di aistudio.google.com")
    
    # Pilihan Model (Jaga-jaga kalau 2.5 limit)
    model_choice = st.selectbox(
        "Pilih Model:",
        ["gemini-2.5-flash", "gemini-1.5-flash"],
        index=0,
        help="Gunakan 2.5 Flash untuk kualitas terbaik. Gunakan 1.5 jika kuota 2.5 habis (Limit 20/hari)."
    )
    
    st.info("""
    **Cara Pakai:**
    1. Buka Gems **'NeuroNote Architect'**.
    2. Minta struktur topik (misal: "Struktur Stroke Iskemik").
    3. Copy struktur ke kolom di kanan.
    4. Klik Generate.
    """)

# --- FUNGSI LOGIC ---
def clean_mermaid_syntax(text):
    if not text: return ""
    # Membersihkan syntax mermaid agar tidak error di Obsidian
    if "```mermaid" in text:
        parts = text.split("```mermaid")
        for i in range(1, len(parts), 2):
            parts[i] = parts[i].replace("(", "[").replace(")", "]") # Ganti kurung () jadi []
            parts[i] = parts[i].replace("'", "").replace('"', "") 
        text = "```mermaid".join(parts)
    return text

def generate_medical_note(api_key, model_name, topic, structure, raw_material):
    # Konfigurasi
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Siapkan Sumber
    source = f"MATERI REFERENSI TAMBAHAN: {raw_material[:50000]}" if raw_material else "SUMBER: Knowledge Base Medis Akademik (Internasional)."

    # --- PROMPT 'KULI CERDAS' ---
    final_prompt = f"""
    # ROLE: Medical Content Writer & Auditor (Obsidian Expert)
    TOPIK: {topic}
    {source}

    # INSTRUKSI UTAMA:
    Anda adalah penulis medis yang patuh pada struktur. 
    Tugas Anda:
    1. Tulis konten SANGAT DETAIL & MENDALAM berdasarkan **STRUKTUR** di bawah ini.
    2. JANGAN mengubah urutan bab yang sudah saya tentukan.
    3. **WAJIB:** Di akhir tulisan, buatlah **Checklist Quality Control**.

    # STRUKTUR YANG HARUS DIIKUTI (HARGA MATI):
    {structure}

    # ATURAN VISUAL & FORMAT (Obsidian Style):
    - **Visual:** Gunakan `> [!grid]` untuk placeholder gambar anatomi/klinis.
    - **Proses:** WAJIB Diagram Mermaid `graph TD` untuk Patofisiologi/Alur Kerja.
    - **Klinis:** Tabel banding untuk Diagnosis Banding.
    - **Highlight:** Gunakan Callout `> [!tip]`, `> [!note]`, `> [!danger]`.

    # AUDIT CHECKLIST (WAJIB ADA DI AKHIR):
    Buat bagian: `## ✅ Quality Control Checklist`
    Isinya adalah daftar item penting yang ada di catatan ini.
    Format:
    - [x] Struktur Lengkap sesuai Request
    - [x] Diagram Mermaid (Mekanisme/Alur)
    - [x] Tabel Komparasi
    - [ ] Validasi User (User harus baca ulang)
    *(Centang [x] jika Anda merasa sudah menyertakannya)*

    # OUTPUT:
    Markdown lengkap. Mulai dengan `# {topic}`.
    """

    try:
        # Generate One-Shot (Sekali Tembak)
        response = model.generate_content(
            final_prompt,
            generation_config={"max_output_tokens": 8192} 
        )
        return clean_mermaid_syntax(response.text)
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "⚠️ **QUOTA LIMIT REACHED (429)**\n\nKuota harian model ini habis. Silakan ganti ke **gemini-1.5-flash** di sidebar sebelah kiri."
        else:
            return f"❌ Error: {error_msg}"

# --- UI UTAMA ---
st.title("🩺 Medical Note Generator")
st.caption("Human-in-the-Loop Workflow: Anda tentukan Struktur, AI isi Dagingnya.")

# Layout Input
col1, col2 = st.columns([1, 1])

with col1:
    topic_input = st.text_input("Judul Topik:", placeholder="Contoh: Gagal Jantung Kongestif")
    raw_material_input = st.text_area("Materi Mentah (Opsional):", height=150, placeholder="Paste teks PDF/Kuliah di sini jika ada...")

with col2:
    structure_input = st.text_area("📋 Struktur Bab (Wajib):", height=240, placeholder="Paste Struktur dari Gemini Gems di sini...\n\n1. Definisi\n2. Patofisiologi (Mermaid)\n3. Tatalaksana\n...")

# Tombol Eksekusi
generate_btn = st.button("🚀 GENERATE CATATAN (ONE-SHOT)")

# --- OUTPUT AREA ---
if generate_btn:
    if not api_key:
        st.error("⚠️ Masukkan API Key dulu di Sidebar!")
    elif not topic_input or not structure_input:
        st.warning("⚠️ Judul Topik dan Struktur wajib diisi!")
    else:
        with st.status("Sedang menulis catatan medis lengkap...", expanded=True) as status:
            st.write("🔄 Menghubungkan ke Brain...")
            st.write(f"📝 Mengikuti struktur yang diberikan...")
            
            # Panggil Fungsi Generate
            start_time = time.time()
            result_md = generate_medical_note(api_key, model_choice, topic_input, structure_input, raw_material_input)
            end_time = time.time()
            
            # Cek Error
            if result_md.startswith("❌") or result_md.startswith("⚠️"):
                status.update(label="Gagal!", state="error")
                st.error(result_md)
            else:
                status.update(label=f"Selesai! ({round(end_time - start_time, 2)} detik)", state="complete", expanded=False)
                
                # Tampilkan Hasil
                st.divider()
                st.subheader(f"📄 Hasil: {topic_input}")
                
                # Tab Preview & Raw Code
                tab_preview, tab_code = st.tabs(["👁️ Preview", "💻 Kode Markdown"])
                
                with tab_preview:
                    st.markdown(result_md)
                
                with tab_code:
                    st.code(result_md, language="markdown")
                
                # Tombol Download
                st.download_button(
                    label="💾 Download .md (Obsidian Ready)",
                    data=result_md,
                    file_name=f"{topic_input.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
