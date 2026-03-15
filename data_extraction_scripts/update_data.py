import json
import re
import os

def main():
    quran_path = os.path.join(os.path.dirname(__file__), '..', 'quran.json')
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data.json')
    
    with open(quran_path, 'r', encoding='utf-8') as f:
        quran_data = json.load(f).get('quran', [])
    
    quran_lookup = {}
    for item in quran_data:
        c = int(item['chapter'])
        v = int(item['verse'])
        quran_lookup[(c, v)] = item['text']

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for surah_idx, surah in enumerate(data):
        chapter = surah_idx + 1
        for ayah in surah.get('ayahs', []):
            ayah_num_str = str(ayah.get('ayah_number', ''))
            
            # Extract numbers
            parts = re.findall(r'\d+', ayah_num_str)
            if not parts:
                continue
            
            verses_to_fetch = []
            if '-' in ayah_num_str and len(parts) >= 2:
                start = int(parts[0])
                end = int(parts[-1])
                verses_to_fetch = list(range(start, end + 1))
            elif ',' in ayah_num_str or ' ve ' in ayah_num_str:
                verses_to_fetch = [int(p) for p in parts]
            else:
                verses_to_fetch = [int(parts[0])]

            new_texts = []
            for v in verses_to_fetch:
                if (chapter, v) in quran_lookup:
                    new_texts.append(quran_lookup[(chapter, v)])
            
            if new_texts:
                # Combine parts with space if multiple
                ayah['ayah_text'] = " ".join(new_texts)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully updated data.json with texts from quran.json")

if __name__ == '__main__':
    main()
