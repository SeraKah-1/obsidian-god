import google.generativeai as genai
from modules.prompts import get_strict_prompt
from modules.formatter import convert_tags_to_obsidian

def generate_note(api_key, model_choice, topic, structure, material=""):
    """
    Fungsi Orkestrator Utama:
    1. Mengkonfigurasi API Google.
    2. Menyusun Prompt (Gabungan Persona + Struktur User).
    3. Mengirim Request ke AI.
    4. Membersihkan/Format Output untuk Obsidian.
    """
    try:
        # 1. Konfigurasi API
        genai.configure(api_key=api_key)
        
        # 2. Setup Model & Parameter
        # Temperature 0.4: Cukup rendah agar dia patuh struktur, 
        # tapi tidak 0.0 agar dia masih bisa membuat analogi (Active Prediction).
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 20000, # Token maksimal (cukup untuk bab panjang)
        }
        
        # Pastikan nama model valid
        # Jika user pilih 2.0 di UI, kirim string yang benar ke API
        target_model = model_choice 
        
        model = genai.GenerativeModel(
            model_name=target_model,
            generation_config=generation_config
        )
        
        # 3. Ambil Prompt "Strict Structure"
        # Ini memanggil fungsi dari modules/prompts.py yang baru saja kita buat
        final_prompt = get_strict_prompt(topic, structure, material)
        
        # 4. Eksekusi Generate (The Waiting Game)
        response = model.generate_content(final_prompt)
        
        # Cek apakah respons diblokir safety settings (jarang terjadi di medis, tapi jaga-jaga)
        if not response.parts:
            return "ERROR_SYSTEM: Respons kosong (Mungkin terblokir filter safety Google)."
            
        raw_text = response.text
        
        # 5. Post-Processing (The Magic Step)
        # Mengubah tag <<<DEEP>>> menjadi Callout Obsidian
        final_md = convert_tags_to_obsidian(raw_text)
        
        return final_md

    except Exception as e:
        # Tangani Error
        error_msg = str(e)
        
        # Deteksi Error Kuota Habis (Paling sering terjadi)
        if "429" in error_msg:
            return "ERROR_QUOTA: 429 Resource Exhausted"
        
        # Deteksi API Key Salah
        elif "API_KEY_INVALID" in error_msg or "400" in error_msg:
            return "ERROR_SYSTEM: API Key Salah atau Tidak Valid."
            
        # Error Lainnya
        else:
            return f"ERROR_SYSTEM: {error_msg}"
