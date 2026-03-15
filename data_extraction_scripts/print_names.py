import json

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

names = [s['name'] for s in data]
for i in range(0, len(names), 10):
    print(" | ".join(names[i:i+10]))
