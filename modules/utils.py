# modules/utils.py

def clean_mermaid_syntax(text):
    """Memperbaiki sintaks Mermaid agar render sempurna di Obsidian"""
    if not text: return ""
    
    if "```mermaid" in text:
        parts = text.split("```mermaid")
        for i in range(1, len(parts), 2):
            # Ganti kurung () jadi [] karena () sering bikin crash di Mermaid
            parts[i] = parts[i].replace("(", "[").replace(")", "]")
            # Hapus tanda kutip tunggal/ganda yang mengganggu
            parts[i] = parts[i].replace("'", "").replace('"', "") 
        text = "```mermaid".join(parts)
    
    return text
