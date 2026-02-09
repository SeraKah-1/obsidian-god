import re

def fix_mermaid_syntax(markdown_text):
    """
    Fungsi ini memperbaiki output Mermaid yang rusak dari AI.
    Target perbaikan:
    1. Menghapus prefix list (.. , - , *) di depan node.
    2. Membungkus isi label node dengan tanda kutip ("") agar karakter aneh aman.
    """
    
    # POLA 1: Menemukan blok mermaid di dalam teks markdown
    # (Mencari teks di antara ```mermaid dan ```)
    mermaid_block_pattern = re.compile(r"```mermaid(.*?)```", re.DOTALL)
    
    def process_block(match):
        raw_content = match.group(1)
        lines = raw_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Bersihkan spasi kiri kanan
            line = line.strip()
            if not line: continue # Skip baris kosong
            
            # --- LANGKAH A: HAPUS PREFIX SAMPAH (.. B[ -> B[ ) ---
            # Regex: Cari karakter titik/strip/bintang di AWAL baris
            # Jika ketemu, ganti dengan string kosong ""
            line = re.sub(r'^[\.\-\*\s]+(?=\w)', '', line)

            # --- LANGKAH B: BUNGKUS DENGAN TANDA KUTIP ("...") ---
            # Kita cari pola: ID[Isi Apapun]
            # Syarat: Ada '[' DAN ada ']' di baris itu
            if '[' in line and line.endswith(']'):
                try:
                    # 1. Pisahkan ID (sebelum '[') dan ISI (setelah '[')
                    # split('[', 1) artinya potong pada kurung siku PERTAMA saja
                    parts = line.split('[', 1)
                    
                    if len(parts) == 2:
                        node_id = parts[0].strip() # Misal: "B"
                        
                        # Ambil isinya, buang ']' terakhir
                        # rsplit(']', 1) artinya potong dari KANAN
                        raw_content = parts[1].rsplit(']', 1)[0] # Misal: "Zona (Glomerulosa)"
                        
                        # 2. Cek apakah sudah ada kutip? Kalau belum, tambahkan.
                        if not (raw_content.startswith('"') and raw_content.endswith('"')):
                            # Hati-hati: Kalau di dalam teks ada kutip ", ganti jadi ' biar gak error
                            safe_content = raw_content.replace('"', "'")
                            
                            # RAKIT ULANG: ID + [" + Isi + "]
                            line = f'{node_id}["{safe_content}"]'
                except Exception:
                    # Kalau error parsing, biarkan baris apa adanya (fail-safe)
                    pass
            
            # Perbaikan Panah (Optional, kadang AI nulis "- >")
            line = line.replace("- >", "->").replace("-- >", "-->")
            
            fixed_lines.append(line)
            
        return "```mermaid\n" + "\n".join(fixed_lines) + "\n```"

    # JALANKAN PROSES:
    # Cari semua blok mermaid, lalu jalankan fungsi 'process_block' padanya
    return mermaid_block_pattern.sub(process_block, markdown_text)
