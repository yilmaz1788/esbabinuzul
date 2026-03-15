import fitz  # PyMuPDF
import json
import re

def parse_pdf(pdf_path, output_json="data.json"):
    doc = fitz.open(pdf_path)
    
    surahs = []
    current_surah = None
    current_ayahs_block = None
    current_reasons = [] # lines of reasons
    
    # regex patterns
    # Matches "1- FATİHA SURESİ" or "FATİHA SURESİ"
    # Added hyphen, apostrophe for names like "ÂL-İ", "EN'ÂM"
    # Added Û to SÛRESİ, parentheses for "MELÂÎKE (FÂTIR)", and optional trailing dot.
    surah_pattern = re.compile(r'^(?:[0-9]+\s*-\s*)?([A-ZÇĞİÖŞÜÎÂÛ\'\-\’\(\)]+(?:\s+[A-ZÇĞİÖŞÜÎÂÛ\'\-\’\(\)]+)*\s*S[UÜÛ]RES[İÎ])\.?$', re.IGNORECASE)
    
    # Matches "1-4. Elif. Lam. Mîm..." or "2. Ayet..."
    ayah_pattern = re.compile(r'^(\d+(?:-\d+)?)\.\s+(.*)')
    
    reason_start_pattern = re.compile(r'^Ayetlerin n[üu]zul sebebi ile ilgili.*', re.IGNORECASE)
    reason_start_pattern_alt = re.compile(r'^Ayetin n[üu]zul sebebi ile ilgili.*', re.IGNORECASE)
    reason_start_pattern_2 = re.compile(r'^Bu s[uü]renin n[üu]z[uü]lu hakk[ıi]nda.*', re.IGNORECASE)
    
    state = "SCANNING"  # SCANNING, IN_SURAH_INTRO, IN_AYAH_TEXT, IN_REASON
    empty_line_before = True
    pending_ayahs = []  # To hold back-to-back ayahs that share the next reason
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        lines = text.split('\n')
        
        for line in lines:
            raw_line = line
            line = line.strip()
            
            # Keep track of structural empty lines, they signify transitions to new Ayahs
            if not line or line == '\xa0':
                empty_line_before = True
                if state == "IN_REASON":
                    current_reasons.append("") # Preserve newlines in narrations
                continue
                
            # Skip page headers/footers if any
            if line.startswith("--- PAGE") or line.isdigit() or len(line) < 3:
                # Sometimes page numbers are standalone digits, skip them
                if line.isdigit(): continue
            
            # 1. Check for Surah Name
            surah_match = surah_pattern.match(line)
                 
            if surah_match:
                surah_name = surah_match.group(1)
                empty_line_before = False
                if current_surah:
                    # Save previous block if exists
                    if current_ayahs_block:
                        reason_text = "\n".join(current_reasons)
                        for pa in pending_ayahs:
                            pa["reason"] += reason_text
                            current_surah["ayahs"].append(pa)
                        pending_ayahs = []
                    surahs.append(current_surah)
                
                # We matched a new Surah
                current_surah = {
                    "name": surah_name if type(surah_match) == bool else surah_match.group(1),
                    "intro": "",
                    "ayahs": []
                }
                state = "IN_SURAH_INTRO"
                current_ayahs_block = None
                current_reasons = []
                continue
            
            # Check for reason start
            if reason_start_pattern.match(line) or reason_start_pattern_alt.match(line) or reason_start_pattern_2.match(line):
                state = "IN_REASON"
                empty_line_before = False
                continue
            
            # Check for Ayah start
            ayah_match = ayah_pattern.match(line)
            # A true Ayah is usually preceded by an empty line in the PDF structure.
            # Bullet point items inside IN_REASON are not preceded by an empty line in the same way.
            # So if we are currently IN_REASON, require an empty line to snap back to IN_AYAH_TEXT.
            is_valid_ayah = False
            if ayah_match:
                if state != "IN_REASON":
                    is_valid_ayah = True
                else:
                    # In reason state. If it matches a true ayah start and not a bullet list
                    rest = ayah_match.group(2)
                    # Check if it looks like a list item (e.g. "1. a- " or short names like "1. Mukâtil")
                    if not re.match(r'^[a-z]\s*-', rest, re.IGNORECASE) and not line.startswith("1. Mukâtil") and not line.startswith("1. a-") and not line.startswith("2. a-") and not re.match(r'^\d+\.\s+a-', line):
                        # For Hucurat and others, consecutive ayahs listed in reasons DO NOT always have empty lines.
                        # We will assume if it matches ayah_pattern and it's not a known list format, it's an ayah.
                        # List items in PDF usually have short text or specific formats.
                        # Real ayahs usually start with a quote `"` or are long.
                        # "1. "Ebû Mansur..." is a list item.
                        # We can check if `empty_line_before` is true, or if it doesn't look like a narrator list item.
                        # To be safe, if it matches, and not a short list/narrator start:
                        is_valid_ayah = True
            
            if is_valid_ayah:
                # If we are starting a NEW sequence of ayahs (because we just finished a reason),
                # save the PREVIOUS sequence and their shared reasons.
                if state == "IN_REASON" and current_ayahs_block:
                    reason_text = "\n".join(current_reasons)
                    for pa in pending_ayahs:
                        pa["reason"] += reason_text
                        current_surah["ayahs"].append(pa)
                    pending_ayahs = []
                    current_reasons = []
                
                current_ayahs_block = {
                    "ayah_number": ayah_match.group(1),
                    "ayah_text": ayah_match.group(2) + " ",
                    "reason": ""
                }
                pending_ayahs.append(current_ayahs_block)
                state = "IN_AYAH_TEXT"
                empty_line_before = False
                continue
            
            # Append text based on state
            if state == "IN_SURAH_INTRO" and current_surah:
                current_surah["intro"] += line + " "
            elif state == "IN_AYAH_TEXT" and current_ayahs_block:
                current_ayahs_block["ayah_text"] += line + " "
            elif state == "IN_REASON" and current_ayahs_block:
                current_reasons.append(line)
            elif state == "IN_REASON" and current_surah and not current_ayahs_block:
                # Reason for the whole Surah
                current_surah["intro"] += line + " "
                
            empty_line_before = False

    # Save the last Surah
    if current_surah:
        if current_ayahs_block:
             reason_text = "\n".join(current_reasons)
             for pa in pending_ayahs:
                 pa["reason"] += reason_text
                 current_surah["ayahs"].append(pa)
        surahs.append(current_surah)
        
    # Deduplicate Surahs and Ayahs
    merged_surahs = {}
    for surah in surahs:
        name = surah["name"]
        if name not in merged_surahs:
            merged_surahs[name] = {"name": name, "intro": surah["intro"], "ayahs": []}
        else:
            merged_surahs[name]["intro"] += "\n\n" + surah["intro"]
            
        # Add ayahs
        for ayah in surah["ayahs"]:
            merged_surahs[name]["ayahs"].append(ayah)
            
    final_surahs = list(merged_surahs.values())
    
    for surah in final_surahs:
        merged_ayahs = {}
        for ayah in surah["ayahs"]:
            ayah_num = ayah["ayah_number"]
            # Fix duplicate spacing from the empty newline preservation
            merged_reason = ayah["reason"].replace("\n\n\n", "\n\n").strip()
            ayah["reason"] = merged_reason
            
            if ayah_num not in merged_ayahs:
                merged_ayahs[ayah_num] = ayah
            else:
                # Same Ayah found, merge reasons
                if merged_reason:
                    if merged_ayahs[ayah_num]["reason"]:
                        merged_ayahs[ayah_num]["reason"] += "\n\n" + merged_reason
                    else:
                        merged_ayahs[ayah_num]["reason"] = merged_reason
                        
        
        # Sort Ayahs by their starting numerical value
        # e.g., "1-3" -> 1, "61" -> 61
        def sort_key(a):
            num_str = a["ayah_number"].split("-")[0]
            try:
                return int(num_str)
            except:
                return 9999
        
        surah["ayahs"] = sorted(list(merged_ayahs.values()), key=sort_key)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_surahs, f, ensure_ascii=False, indent=2)
        
    print(f"Parsed {len(final_surahs)} Surahs (Deduplicated). Saved to {output_json}")

if __name__ == "__main__":
    parse_pdf(r"C:\Users\tonny\Desktop\esbabı nüzul.pdf")
