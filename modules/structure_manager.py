def validate_inputs(topic, structure):
    """
    Fungsi Validasi Input.
    Mencegah request kosong dikirim ke API (Hemat Kuota & Waktu).
    
    Args:
        topic (str): Judul topik dari user.
        structure (str): Kerangka bab dari user.
        
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    
    # 1. Cek Topik
    if not topic or not topic.strip():
        return False, "Judul Topik tidak boleh kosong!"
        
    # 2. Cek Struktur
    if not structure or not structure.strip():
        return False, "Struktur Bab wajib diisi! Copy outline dari Gemini/ChatGPT dulu."
        
    # 3. Cek Panjang Struktur (Biar gak cuma nulis "bab 1" doang)
    if len(structure) < 15:
        return False, "Struktur terlalu pendek. Berikan kerangka yang jelas (min. 15 karakter)."
        
    # Kalau lolos semua
    return True, ""
