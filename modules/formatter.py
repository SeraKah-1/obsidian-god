import re

def convert_tags_to_obsidian(text):
    """
    Mengubah RAW TAGS dari AI (<<<DEEP_START>>>) menjadi format Obsidian Callout
    yang valid (> [!note]) tanpa rusak.
    """
    
    # 1. Konversi DEEP DIVE (Blue Note)
    # Pola: <<<DEEP_START>>> Judul \n Isi <<<DEEP_END>>>
    pattern_deep = r"<<<DEEP_START>>>\s*(.*?)\n(.*?)<<<DEEP_END>>>"
    
    def replace_deep(match):
        title = match.group(1).strip()
        content = match.group(2)
        # Tambahkan "> " di setiap baris agar masuk ke dalam callout
        processed_lines = [f"> {line}" for line in content.split('\n')]
        formatted_content = "\n".join(processed_lines)
        return f"> [!note]- 👁️ **{title}**\n{formatted_content}"

    # Flag DOTALL penting agar regex bisa membaca baris baru (\n) sebagai satu kesatuan
    text = re.sub(pattern_deep, replace_deep, text, flags=re.DOTALL)

    # 2. Konversi CLINIC (Green Tip)
    # Pola: <<<CLINIC_START>>> Judul \n Isi <<<CLINIC_END>>>
    pattern_clinic = r"<<<CLINIC_START>>>\s*(.*?)\n(.*?)<<<CLINIC_END>>>"
    
    def replace_clinic(match):
        title = match.group(1).strip()
        content = match.group(2)
        processed_lines = [f"> {line}" for line in content.split('\n')]
        formatted_content = "\n".join(processed_lines)
        return f"> [!tip]- 💊 **{title}**\n{formatted_content}"

    text = re.sub(pattern_clinic, replace_clinic, text, flags=re.DOTALL)
    
    return text
