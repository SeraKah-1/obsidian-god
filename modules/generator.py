# modules/generator.py
import google.generativeai as genai
from modules.prompts import get_main_prompt
from modules.structure_manager import format_user_structure
from modules.utils import clean_mermaid_syntax

def generate_note(api_key, model_name, topic, raw_structure, raw_material):
    # 1. Setup
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # 2. Siapkan Data (Pakai Structure Manager & Prompt Module)
    locked_structure = format_user_structure(raw_structure)
    source_context = f"SUMBER TAMBAHAN: {raw_material[:50000]}" if raw_material else ""
    
    final_prompt = get_main_prompt(topic, locked_structure, source_context)
    
    # 3. Eksekusi One-Shot
    try:
        response = model.generate_content(
            final_prompt,
            generation_config={"max_output_tokens": 8192}
        )
        
        # 4. Bersihkan Hasil
        return clean_mermaid_syntax(response.text)
        
    except Exception as e:
        if "429" in str(e):
            return "ERROR_QUOTA: 429" # Kode khusus buat ditangkap UI
        return f"ERROR_SYSTEM: {str(e)}"
