# modules/structure_manager.py

def format_user_structure(raw_structure_text):
    """
    Mengambil teks struktur mentah dari user dan membungkusnya 
    dengan instruksi ketat agar AI patuh.
    """
    if not raw_structure_text:
        return ""

    # Kita bungkus dengan tag XML-style semu agar AI fokus
    formatted = f"""
    <LOCKED_STRUCTURE_PROTOCOL>
    PERINGATAN KERAS KEPADA AI:
    Ini adalah KERANGKA YANG TIDAK BOLEH DIUBAH.
    Anda dilarang keras menambah Bab baru atau menghilangkan Bab yang ada.
    Ikuti urutan ini poin demi poin:
    
    {raw_structure_text}
    
    </LOCKED_STRUCTURE_PROTOCOL>
    """
    return formatted

def validate_inputs(topic, structure):
    """Cek apakah input user kosong"""
    if not topic or len(topic) < 3:
        return False, "⚠️ Judul topik terlalu pendek!"
    if not structure or len(structure) < 10:
        return False, "⚠️ Struktur belum diisi dengan benar!"
    return True, ""
