import json

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

baqarah = [s for s in data if "BAKARA" in s["name"].upper()][0]

ayah_nums = set()
for a in baqarah["ayahs"]:
    # Ayah numbers can be ranges like "1-4"
    parts = a["ayah_number"].split("-")
    if len(parts) == 1:
        ayah_nums.add(int(parts[0]))
    else:
        for i in range(int(parts[0]), int(parts[1])+1):
            ayah_nums.add(i)

missing = []
for i in range(1, 287): # Baqarah has 286 ayahs
    if i not in ayah_nums:
        missing.append(i)

print(f"Skipped Ayahs in Bakara: {missing[:50]}")
