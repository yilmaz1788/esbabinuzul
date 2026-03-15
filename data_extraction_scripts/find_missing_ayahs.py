import fitz
import re

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')

potential_ayahs = []
for i in range(15, 30): # Scan early pages like Baqarah
    page = doc.load_page(i)
    text = page.get_text()
    for line in text.split('\n'):
        line_clean = line.strip()
        if not line_clean:
             continue
        # Look for things that start with a number but fail our current regex
        if re.match(r'^\d+', line_clean) and not re.match(r'^(\d+(?:-\d+)?)\.\s+(.*)', line_clean):
            # Exclude obvious non-ayah things like standalone numbers (page numbers)
            if len(line_clean) > 5 and not "SURESİ" in line_clean.upper() and not "SÛRESİ" in line_clean.upper():
                potential_ayahs.append(f"Page {i+1}: '{line_clean}'")

for p in potential_ayahs[:30]:
    print(p)
