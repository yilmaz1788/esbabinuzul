import json

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

rad = [s for s in data if "RA" in s["name"].upper() and "D" in s["name"].upper()][0]

for a in rad['ayahs']:
    num = int(a['ayah_number'].split('-')[0])
    if num <= 14:
        print(f"[{a['ayah_number']}] Reason lengths: {len(a['reason'])}")
