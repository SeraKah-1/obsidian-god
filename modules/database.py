# modules/database.py
import streamlit as st
from supabase import create_client, Client
import re

# 1. Setup Koneksi ke Supabase
# Kita bungkus pakai @st.cache_resource supaya koneksi gak dibuka-tutup terus tiap user klik (biar cepat)
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["URL"]
        key = st.secrets["supabase"]["KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Gagal connect ke Database: {e}")
        return None

supabase: Client = init_supabase()

# 2. Helper: Bersihkan Teks (Slugify)
# Ubah "Gagal Jantung (HF)!!" jadi "gagal-jantung-hf" biar pencarian konsisten
def create_slug(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text) # Hapus simbol aneh
    text = re.sub(r'[\s_-]+', '-', text) # Ganti spasi jadi strip
    return text

# 3. Fungsi Cek Gudang (Fetch)
def fetch_note_from_db(topic_input):
    if not supabase: return None
    
    slug = create_slug(topic_input)
    
    try:
        # Query: Cari di tabel 'medical_notes' yang slug-nya cocok
        response = supabase.table("medical_notes") \
            .select("*") \
            .eq("topic_slug", slug) \
            .execute()
        
        # Jika ada datanya
        if response.data and len(response.data) > 0:
            # Update View Count (Nambah 1 yang lihat) - Opsional, bisa dihapus kalau lemot
            current_views = response.data[0]['view_count'] or 0
            supabase.table("medical_notes") \
                .update({"view_count": current_views + 1}) \
                .eq("id", response.data[0]['id']) \
                .execute()
            
            return response.data[0] # Kembalikan data lengkap
            
        return None # Gak nemu
    except Exception as e:
        print(f"Error fetching: {e}") # Print di terminal aja biar user gak panik
        return None

# 4. Fungsi Simpan Barang Baru (Save)
def save_note_to_db(topic_input, content_md):
    if not supabase: return
    
    slug = create_slug(topic_input)
    
    data = {
        "topic_input": topic_input,
        "topic_slug": slug,
        "content_md": content_md,
        "source_type": "AI_GENERATED"
    }
    
    try:
        supabase.table("medical_notes").insert(data).execute()
        print(f"✅ Berhasil simpan topik: {slug}")
    except Exception as e:
        st.warning(f"Gagal menyimpan ke database: {e}")
