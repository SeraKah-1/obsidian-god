import re

def clean_and_quote_content(content):
    """
    Fungsi Pembantu:
    Membersihkan konten di dalam tag dan menambahkan tanda '>' di setiap baris.
    
    Fitur Utama:
    - Menangani baris kosong (empty lines) agar kotak Callout tidak "putus".
    - Di Obsidian, jika ada baris kosong tanpa tanda '>', callout dianggap selesai.
      Fungsi ini mencegah hal itu terjadi.
    """
    # Hapus whitespace berlebih di awal/akhir blok konten, lalu pisah per baris
    lines = content.strip().split('\n')
    
    processed_lines = []
    for line in lines:
        # Jika baris kosong, tetap beri tanda '>' (tanpa spasi) agar visual kotak nyambung
        if line.strip() == "":
            processed_lines.append(">") 
        else:
            # Jika ada isinya, tambahkan '> ' di depan
            processed_lines.append(f"> {line}")
            
    return "\n".join(processed_lines)

def convert_tags_to_obsidian(text):
    """
    Fungsi Utama:
    Mencari RAW TAGS (<<<...>>>) dan mengubahnya menjadi Obsidian Callout Syntax.
    """
    
    # KAMUS TAG (Bisa Anda tambah sendiri nanti)
    # Format: 'NAMA_TAG': ('Tipe_Callout_Obsidian', 'Ikon')
    tag_map = {
        'DEEP':   ('note', '👁️'),      # Biru (Deep Dive / Analisis)
        'CLINIC': ('tip', '💊'),       # Hijau (Klinis / Tips)
        'ALERT':  ('warning', '⚠️'),   # Merah (Red Flags) - Opsional
        'INFO':   ('info', 'ℹ️')       # Abu-abu (Info tambahan) - Opsional
    }

    processed_text = text

    for tag_name, (obsidian_type, icon) in tag_map.items():
        # --- PENJELASAN REGEX ---
        # 1. <<<TAG_START>>>   : Cari pembuka tag
        # 2. \s* : Toleransi spasi (jika AI tidak sengaja nambah spasi)
        # 3. (.*?)             : GROUP 1 -> Ambil Judul (Baris pertama)
        # 4. \n                : Wajib ada enter setelah judul
        # 5. (.*?)             : GROUP 2 -> Ambil Isi Konten (sampai penutup)
        # 6. <<<TAG_END>>>     : Cari penutup tag
        # Flags re.DOTALL      : Agar tanda titik (.) bisa membaca baris baru (\n)
        
        pattern = f"<<<{tag_name}_START>>>\s*(.*?)\n(.*?)<<<{tag_name}_END>>>"
        
        def replacement_func(match):
            try:
                # Ambil data dari capture group regex
                title = match.group(1).strip()
                raw_body = match.group(2)
                
                # Format body agar masuk ke dalam blockquote
                formatted_body = clean_and_quote_content(raw_body)
                
                # Rakit string akhir Obsidian Callout
                # Tanda [-] artinya default collapsed (tertutup) biar rapi
                return f"> [!{obsidian_type}]- {icon} **{title}**\n{formatted_body}"
            except Exception:
                # Safety net: Kalau parsing gagal, kembalikan teks asli (jangan crash)
                return match.group(0)

        # Eksekusi penggantian teks
        processed_text = re.sub(pattern, replacement_func, processed_text, flags=re.DOTALL)

    return processed_text
