import fitz
import re

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')

print("Searching for titles...")
titles = []
for i in range(200):  # Check first 200 pages
    page = doc.load_page(i)
    text = page.get_text()
    for line in text.split('\n'):
        # Check if line contains SURE or SÛRE, and is mostly uppercase
        line_clean = line.strip()
        if ("SURE" in line_clean.upper() or "SÛRE" in line_clean.upper()):
            # If line is short and uppercase
            if len(line_clean) < 60 and line_clean.isupper() or line_clean.title() == line_clean:
                 print(f"Page {i+1}: '{line_clean}'")

