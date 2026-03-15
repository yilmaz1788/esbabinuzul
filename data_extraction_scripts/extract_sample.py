import fitz

pdf_path = r"C:\Users\tonny\Desktop\esbabı nüzul.pdf"
doc = fitz.open(pdf_path)

with open("sample.txt", "w", encoding="utf-8") as f:
    for i in range(min(15, len(doc))):
        page = doc.load_page(i)
        f.write(f"--- PAGE {i+1} ---\n")
        f.write(page.get_text())
        f.write("\n\n")
