import sys
try:
    import fitz 
except ImportError:
    print("fitz not installed")
    sys.exit(1)

pdf_path = r"C:\Users\tonny\Desktop\esbabı nüzul.pdf"
doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")
for i in range(min(5, len(doc))):
    page = doc.load_page(i)
    text = page.get_text()
    print(f"--- Page {i+1} ---")
    print(text)
    print("-------------------")
