import fitz
import re

def extract_hucurat():
    pdf_path = r"C:\Users\tonny\Desktop\esbabı nüzul.pdf"
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
        
    # Find indices
    match_start = re.search(r'49[ \-\.]+HUCUR[AÂ]T', text, re.IGNORECASE)
    match_end = re.search(r'50[ \-\.]+K[AÂ]F', text, re.IGNORECASE)
    
    if match_start and match_end:
        chunk = text[match_start.start():match_end.start()]
        with open("hucurat_dump.txt", "w", encoding="utf-8") as f:
            f.write(chunk)
        print("Dumped Hucurat to hucurat_dump.txt")
    else:
        print("Could not find start or end.", match_start, match_end)

if __name__ == "__main__":
    extract_hucurat()
