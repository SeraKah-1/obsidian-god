import streamlit as st
import time
from modules.structure_manager import validate_inputs
from modules.generator import generate_note

# --- KONFIG HALAMAN ---
st.set_page_config(page_title="NeuroNote AI", page_icon="🧠", layout="wide")

# CSS Custom
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .stButton>button {background-color: #7c4dff; color: white; border-radius: 8px; height: 3em;}
    h1 {color: #7c4dff;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 NeuroNote")
    
    # LOGIKA BARU: Cek Secrets dulu
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Terdeteksi (Auto)")
    else:
        # Kalau tidak ada secrets, minta input manual
        api_key = st.text_input("API Key:", type="password", help="Masukkan Key manual karena secrets belum diset.")

    st.divider()
    model_choice = st.selectbox("Model:", ["gemini-2.5-flash", "gemini-1.5-flash"])
    st.info("Tips: Gunakan Gemini Web untuk menyusun struktur, lalu paste di sini.")

# --- UI UTAMA ---
st.title("Medical Note Generator")
st.caption("Human Structure x AI Content")

col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_input("Judul Topik:", placeholder="Cth: Diabetes Melitus Tipe 2")
    material = st.text_area("Materi Mentah (Opsional):", height=200)

with col2:
    structure = st.text_area("📋 Struktur Bab (Wajib):", height=275, 
                            placeholder="Paste Outline dari Gemini Web disini...\n1. Definisi\n2. Patofisiologi\n...")

btn = st.button("🚀 GENERATE CATATAN")

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
            st.write("🔒 Mengunci Struktur...")
            st.write("🧠 Mengarang Konten (NeuroNote Style)...")
            
            start = time.time()
            result = generate_note(api_key, model_choice, topic, structure, material)
            
            if result == "ERROR_QUOTA: 429":
                status.update(label="Gagal!", state="error")
                st.error("🚨 KUOTA HABIS (Error 429). Ganti model ke 1.5-flash di sidebar.")
            elif result.startswith("ERROR_SYSTEM"):
                status.update(label="Error!", state="error")
                st.error(result)
            else:
                status.update(label="Selesai!", state="complete", expanded=False)
                st.success(f"Selesai dalam {round(time.time()-start, 1)} detik!")
                
                # 3. Output
                st.subheader("Hasil:")
                st.markdown(result)
                st.download_button("💾 Download .md", result, file_name=f"{topic}.md")
