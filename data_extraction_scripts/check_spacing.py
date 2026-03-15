import fitz

doc = fitz.open(r'C:\Users\tonny\Desktop\esbabı nüzul.pdf')

for i in range(10, 15):
    page = doc.load_page(i)
    text = page.get_text()
    for line in text.split('\n'):
        clean = line.strip()
        if not clean:
            print("EMPTY")
        elif clean == '\xa0':
            print("NBSP")
        else:
            print(clean)
