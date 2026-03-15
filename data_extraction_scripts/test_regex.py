import fitz
import re

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')
surah_pattern = re.compile(r'^(?:[0-9]+\s*-\s*)?([A-ZÇĞİÖŞÜÎÂÛ\'\-\’]+(?:\s+[A-ZÇĞİÖŞÜÎÂÛ\'\-\’]+)*\s*S[UÜÛ]RES[İÎ])$', re.IGNORECASE)

missed = set()
for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text()
    for line in text.split('\n'):
        line_clean = line.strip()
        if ("SURE" in line_clean.upper() or "SÛRE" in line_clean.upper()):
            # Find ANY line that looks like a title 
            if len(line_clean) < 60 and (line_clean.isupper() or line_clean.title() == line_clean) and " " in line_clean:
                 match = surah_pattern.match(line_clean)
                 if not match:
                     missed.add(line_clean)

with open('missed.txt', 'w', encoding='utf-8') as f:
    for m in sorted(list(missed)):
        f.write(f"{m}\n")
