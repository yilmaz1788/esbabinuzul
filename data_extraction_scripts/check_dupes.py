import json
from collections import Counter

def check():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    names = [s['name'] for s in data]
    print("Duplicate Surahs:", [k for k,v in Counter(names).items() if v > 1])
    
    ayahs = [f"{s['name']} - {a['ayah_number']}" for s in data for a in s['ayahs']]
    print("Duplicate Ayahs:", [k for k,v in Counter(ayahs).items() if v > 1])

if __name__ == "__main__":
    check()
