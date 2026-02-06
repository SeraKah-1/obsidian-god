import re

def clean_and_quote_content(content):
    """
    Helper function: Membersihkan konten dan menambahkan '> ' di setiap baris.
    Menjaga agar blockquote tidak putus di tengah jalan.
    """
    # Hapus whitespace berlebih di awal/akhir blok konten
    lines = content.strip().split('\n')
    
    processed_lines = []
    for line in lines:
        # Jika baris kosong, tetap beri tanda '>' agar kotak tidak putus visualnya
        if line.strip() == "":
            processed_lines.append(">") 
        else:
            # Tambahkan '> ' di depan teks
            processed_lines.append(f"> {line}")
            
    return "\n".join(processed_lines)

def convert_tags_to_obsidian(text):
    """
    Mengubah RAW TAGS dari AI menjadi format Obsidian Callout yang valid.
    Menangani berbagai jenis tag secara dinamis.
    """
    
    # DAFTAR TAG YANG DIDUKUNG
    # Format: 'TAG_NAME': ('Obsidian_Type', 'Icon', 'Color_Hex_Optional')
    tag_map = {
        'DEEP':   ('note', '👁️'),      # Biru (Deep Dive)
        'CLINIC': ('tip', '💊'),       # Hijau (Klinis/Tips)
        'WARN':   ('warning', '⚠️'),   # Merah (Peringatan/Red Flags) - Opsional kalau mau tambah
    }

    processed_text = text

    for tag_name, (obsidian_type, icon) in tag_map.items():
        # Regex Penjelasan:
        # 1. <<<TAG_START>>>   -> Cari tag pembuka
        # 2. \s* -> Toleransi spasi/newline setelah tag
        # 3. (.*?)             -> GROUP 1: Judul (Ambil baris pertama)
        # 4. \n                -> Wajib ada enter setelah judul
        # 5. (.*?)             -> GROUP 2: Isi Konten (Ambil sampai tag penutup)
        # 6. <<<TAG_END>>>     -> Cari tag penutup
        pattern = f"<<<{tag_name}_START>>>\s*(.*?)\n(.*?)<<<{tag_name}_END>>>"
        
        def replacement_func(match):
            try:
                # Ambil data dari capture group
                title = match.group(1).strip()
                raw_body = match.group(2)
                
                # Proses body agar indentasinya rapi
                formatted_body = clean_and_quote_content(raw_body)
                
                # Rakit string akhir Obsidian Callout
                # [-] artinya collapsible (bisa dilipat), default tertutup biar rapi
                return f"> [!{obsidian_type}]- {icon} **{title}**\n{formatted_body}"
            except Exception as e:
                # Fallback: Kalau error parsing, kembalikan teks asli biar gak crash
                return match.group(0)

        # Eksekusi Regex
        processed_text = re.sub(pattern, replacement_func, processed_text, flags=re.DOTALL)

    return processed_text
