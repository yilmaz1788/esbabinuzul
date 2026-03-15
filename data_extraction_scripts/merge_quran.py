import json

def merge_quran():
    # Load parsed Esbab-ı Nüzul data
    with open("data.json", "r", encoding="utf-8") as f:
        esbab_data = json.load(f)
        
    # Load complete Quran data
    with open("quran.json", "r", encoding="utf-8") as f:
        quran_data = json.load(f)["quran"]
        
    # We need a mapping from Surah number to Surah name and Intro to preserve it
    # We will build a complete dataset structured similarly to data.json
    
    # Let's map esbab data by normalized name or index
    # Note: data.json has 114 surahs but names might be slightly different.
    # The order in data.json is 1 to 114. We can rely on index (0-based = chapter - 1)
    
    surahs = []
    
    # For robust matching, we assume esbab_data has exactly 114 surahs in order
    if len(esbab_data) != 114:
        print(f"Warning: esbab_data has {len(esbab_data)} surahs instead of 114. Attempting index mapping.")
        
    # Create the 114 Surahs
    for i in range(114):
        esbab_surah = esbab_data[i] if i < len(esbab_data) else None
        
        # We will use the name from Esbab data if available, else a generic name
        surah_name = esbab_surah["name"] if esbab_surah else f"Surah {i+1}"
        surah_intro = esbab_surah["intro"] if esbab_surah else ""
        
        surah_obj = {
            "name": surah_name,
            "intro": surah_intro,
            "ayahs": []
        }
        surahs.append(surah_obj)
        
    # Group Esbab ayahs by Surah and Ayah number for fast lookup
    # Because some ayahs are grouped like "1-3", we will parse those ranges
    esbab_lookup = {}
    for i, surah in enumerate(esbab_data):
        chapter = i + 1
        esbab_lookup[chapter] = {}
        for ayah in surah.get("ayahs", []):
            num_str = ayah["ayah_number"]
            reason = ayah.get("reason", "")
            
            # Parse ranges like "1-3" or "5"
            parts = num_str.split("-")
            if len(parts) == 1:
                try:
                    num = int(parts[0])
                    esbab_lookup[chapter][num] = reason
                except:
                    pass
            elif len(parts) == 2:
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                    for n in range(start, end + 1):
                        # Merge reasons if a range covers it
                        if n in esbab_lookup[chapter]:
                            esbab_lookup[chapter][n] += "\n\n" + reason
                        else:
                            esbab_lookup[chapter][n] = reason
                except:
                    pass

    # Now iterate over complete Quran ayahs and inject them
    for ayah in quran_data:
        chapter = int(ayah["chapter"])
        verse = int(ayah["verse"])
        text = ayah["text"]
        
        surah_idx = chapter - 1
        
        reason = ""
        if chapter in esbab_lookup and verse in esbab_lookup[chapter]:
            reason = esbab_lookup[chapter][verse].strip()
            
        surahs[surah_idx]["ayahs"].append({
            "ayah_number": str(verse),
            "ayah_text": text.strip(),
            "reason": reason
        })
        
    # Write the complete merged data
    with open("complete_data.json", "w", encoding="utf-8") as f:
        json.dump(surahs, f, ensure_ascii=False, indent=2)
        
    print("Merged full Quran with Esbab-ı Nüzul narrations. Saved to complete_data.json")

if __name__ == "__main__":
    merge_quran()
