import re

def fix_mermaid_syntax(markdown_text):
    """
    Fungsi ini mencari blok ```mermaid ... ``` dan memperbaiki sintaks error umum
    seperti titik di depan node (.. B[...]), spasi di ID, dll.
    """
    
    # Pola untuk menemukan blok mermaid
    mermaid_pattern = re.compile(r"```mermaid(.*?)```", re.DOTALL)
    
    def repair_block(match):
        content = match.group(1)
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Hapus whitespace di awal/akhir
            clean_line = line.strip()
            
            if not clean_line:
                continue
                
            # --- PERBAIKAN 1: Hapus Titik/List di Depan Node ---
            # Kasus user: ".. B[Zona...]" -> menjadi "B[Zona...]"
            # Regex: Menghapus karakter non-alphanumeric di awal baris jika diikuti ID node
            clean_line = re.sub(r'^[\.\-\*\s]+([A-Za-z0-9_]+\[)', r'\1', clean_line)
            
            # --- PERBAIKAN 2: Perbaiki Panah Rusak ---
            # Kadang AI nulis "-->" jadi "-- >" atau "- ->"
            clean_line = clean_line.replace("- >", "->")
            clean_line = clean_line.replace("-- >", "-->")
            clean_line = clean_line.replace("== >", "==>")
            
            # --- PERBAIKAN 3: Spasi di dalam ID Node ---
            # Error: A B[Label] -> Rusak karena ada spasi antara A dan B
            # Kita cari pola "ID[Label]" dan pastikan ID gak ada spasi aneh
            # (Ini agak tricky, jadi kita fokus ke perbaikan tanda kurung dan panah dulu)

            # --- PERBAIKAN 4: Tanda Kurung dalam Label ---
            # Mermaid bingung kalau ada () di dalam [] tanpa kutip.
            # Contoh: A[Makan (Nasi)] -> Aman
            # Contoh: A[Makan [Nasi]] -> Error
            # Solusi: Ganti [ di dalam label jadi (
            
            if '[' in clean_line and ']' in clean_line:
                # Pisahkan ID dan Label: ID[Label Isi]
                parts = clean_line.split('[', 1) 
                if len(parts) == 2:
                    node_id = parts[0]
                    label_content = parts[1].rsplit(']', 1)[0]
                    rest = parts[1].rsplit(']', 1)[1] if len(parts[1].rsplit(']', 1)) > 1 else ""
                    
                    # Bersihkan label content dari karakter perusak
                    label_content = label_content.replace('[', '(').replace(']', ')')
                    label_content = label_content.replace('"', "'") # Ganti kutip dua jadi satu biar aman
                    
                    clean_line = f"{node_id}[{label_content}]{rest}"

            fixed_lines.append(clean_line)
            
        return "```mermaid\n" + "\n".join(fixed_lines) + "\n```"

    # Jalankan penggantian di seluruh teks
    fixed_text = mermaid_pattern.sub(repair_block, markdown_text)
    return fixed_text
