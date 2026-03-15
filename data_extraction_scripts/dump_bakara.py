import fitz

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')

start_page = -1
for i in range(10):  # Check first 10 pages for Bakara
    page = doc.load_page(i)
    text = page.get_text()
    if "BAKARA SURESİ" in text:
        start_page = i
        break

if start_page != -1:
    with open("bakara_start.txt", "w", encoding="utf-8") as f:
        for i in range(start_page, start_page+3):
            f.write(f"--- PAGE {i+1} ---\n")
            f.write(doc.load_page(i).get_text())
    print(f"Dumped Bakara start pages (from page {start_page+1})")
else:
    print("Bakara not found early")
