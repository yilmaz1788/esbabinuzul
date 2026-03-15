import fitz

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')

start_page = -1
for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text()
    if "RA’D SURESİ" in text or "RAD SURESİ" in text:
        start_page = i
        break

if start_page != -1:
    print(f"Found Rad Suresi at page {start_page+1}")
    with open("rad_dump.txt", "w", encoding="utf-8") as f:
        for i in range(start_page, start_page+4):
            f.write(f"--- PAGE {i+1} ---\n")
            f.write(doc.load_page(i).get_text())
else:
    print("Rad Suresi not found")
