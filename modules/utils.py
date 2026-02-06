# modules/utils.py
import re

def clean_mermaid_syntax(text):
    """Membersihkan sintaks Mermaid dan elemen Markdown yang rusak."""
    if not text: return ""
    
    # 1. Fix Mermaid
    if "```mermaid" in text:
        parts = text.split("```mermaid")
        for i in range(1, len(parts), 2):
            parts[i] = parts[i].replace("(", "[").replace(")", "]")
            parts[i] = parts[i].replace("'", "").replace('"', "") 
        text = "```mermaid".join(parts)
        
    # 2. Fix Table "Infinite Dash" Bug (PENTING!)
    # Mengganti garis pemisah tabel yang > 3 strip menjadi 3 strip saja.
    # Contoh: | :----------------------- |  JADI  | :--- |
    text = re.sub(r'-{4,}', '---', text)
    
    return text
