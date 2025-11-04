import pdfplumber
import pandas as pd
import re
import unicodedata


def normalize_arabic(text: str) -> str:
    """Convert Arabic presentation forms back to standard Arabic Unicode.
    Uses a comprehensive mapping of presentation forms (U+FE70-U+FEFC) to 
    standard Arabic characters (U+0600-U+06FF).
    """
    if not text:
        return text
    
    # Comprehensive mapping of Arabic Presentation Forms-B to standard Arabic
    # This covers all common forms extracted from PDFs
    presentation_to_standard = {
        # Hamza and Alef forms
        '\uFE80': '\u0621', '\uFE81': '\u0622', '\uFE82': '\u0622',
        '\uFE83': '\u0623', '\uFE84': '\u0623', '\uFE85': '\u0624',
        '\uFE86': '\u0624', '\uFE87': '\u0625', '\uFE88': '\u0625',
        '\uFE8D': '\u0627', '\uFE8E': '\u0627',
        
        # Beh, Teh, Theh
        '\uFE8F': '\u0628', '\uFE90': '\u0628', '\uFE91': '\u0628', '\uFE92': '\u0628',
        '\uFE93': '\u0629', '\uFE94': '\u0629',
        '\uFE95': '\u062A', '\uFE96': '\u062A', '\uFE97': '\u062A', '\uFE98': '\u062A',
        '\uFE99': '\u062B', '\uFE9A': '\u062B', '\uFE9B': '\u062B', '\uFE9C': '\u062B',
        
        # Jeem, Hah, Khah
        '\uFE9D': '\u062C', '\uFE9E': '\u062C', '\uFE9F': '\u062C', '\uFEA0': '\u062C',
        '\uFEA1': '\u062D', '\uFEA2': '\u062D', '\uFEA3': '\u062D', '\uFEA4': '\u062D',
        '\uFEA5': '\u062E', '\uFEA6': '\u062E', '\uFEA7': '\u062E', '\uFEA8': '\u062E',
        
        # Dal, Thal, Reh, Zain
        '\uFEA9': '\u062F', '\uFEAA': '\u062F',
        '\uFEAB': '\u0630', '\uFEAC': '\u0630',
        '\uFEAD': '\u0631', '\uFEAE': '\u0631',
        '\uFEAF': '\u0632', '\uFEB0': '\u0632',
        
        # Seen, Sheen, Sad, Dad
        '\uFEB1': '\u0633', '\uFEB2': '\u0633', '\uFEB3': '\u0633', '\uFEB4': '\u0633',
        '\uFEB5': '\u0634', '\uFEB6': '\u0634', '\uFEB7': '\u0634', '\uFEB8': '\u0634',
        '\uFEB9': '\u0635', '\uFEBA': '\u0635', '\uFEBB': '\u0635', '\uFEBC': '\u0635',
        '\uFEBD': '\u0636', '\uFEBE': '\u0636', '\uFEBF': '\u0636', '\uFEC0': '\u0636',
        
        # Tah, Zah, Ain, Ghain
        '\uFEC1': '\u0637', '\uFEC2': '\u0637', '\uFEC3': '\u0637', '\uFEC4': '\u0637',
        '\uFEC5': '\u0638', '\uFEC6': '\u0638', '\uFEC7': '\u0638', '\uFEC8': '\u0638',
        '\uFEC9': '\u0639', '\uFECA': '\u0639', '\uFECB': '\u0639', '\uFECC': '\u0639',
        '\uFECD': '\u063A', '\uFECE': '\u063A', '\uFECF': '\u063A', '\uFED0': '\u063A',
        
        # Feh, Qaf, Kaf, Lam
        '\uFED1': '\u0641', '\uFED2': '\u0641', '\uFED3': '\u0641', '\uFED4': '\u0641',
        '\uFED5': '\u0642', '\uFED6': '\u0642', '\uFED7': '\u0642', '\uFED8': '\u0642',
        '\uFED9': '\u0643', '\uFEDA': '\u0643', '\uFEDB': '\u0643', '\uFEDC': '\u0643',
        '\uFEDD': '\u0644', '\uFEDE': '\u0644', '\uFEDF': '\u0644', '\uFEE0': '\u0644',
        
        # Meem, Noon, Heh, Waw
        '\uFEE1': '\u0645', '\uFEE2': '\u0645', '\uFEE3': '\u0645', '\uFEE4': '\u0645',
        '\uFEE5': '\u0646', '\uFEE6': '\u0646', '\uFEE7': '\u0646', '\uFEE8': '\u0646',
        '\uFEE9': '\u0647', '\uFEEA': '\u0647', '\uFEEB': '\u0647', '\uFEEC': '\u0647',
        '\uFEED': '\u0648', '\uFEEE': '\u0648',
        
        # Alef Maksura, Yeh
        '\uFEEF': '\u0649', '\uFEF0': '\u0649',
        '\uFEF1': '\u064A', '\uFEF2': '\u064A', '\uFEF3': '\u064A', '\uFEF4': '\u064A',
        
        # Lam-Alef ligatures
        '\uFEF5': '\u0644\u0622', '\uFEF6': '\u0644\u0622',
        '\uFEF7': '\u0644\u0623', '\uFEF8': '\u0644\u0623',
        '\uFEF9': '\u0644\u0625', '\uFEFA': '\u0644\u0625',
        '\uFEFB': '\u0644\u0627', '\uFEFC': '\u0644\u0627',
        
        # Yeh with Hamza
        '\uFE89': '\u0626', '\uFE8A': '\u0626', '\uFE8B': '\u0626', '\uFE8C': '\u0626',
        
        # Tatweel (kashida) - remove it
        '\u0640': '',
    }
    
    return ''.join(presentation_to_standard.get(c, c) for c in text)


def fix_arabic_line(line: str) -> str:
    """pdfplumber extracts Arabic text in reversed order with presentation forms.
    We need to reverse the entire line to get correct order, then normalize."""
    if not line or not any('\u0600' <= c <= '\u06FF' or '\uFE70' <= c <= '\uFEFF' for c in line):
        return line
    
    # Reverse the line and normalize presentation forms to standard Arabic
    reversed_line = line[::-1]
    normalized = normalize_arabic(reversed_line)
    return normalized


# === 1️⃣ Load PDF ===
# Fixed absolute path provided by user
pdf_path = r"C:\Users\user\Desktop\data analysis orientation\orientation_book.pdf"

data = []
current_category = None
current_university = None
current_faculty = None

# === 2️⃣ Open the PDF ===
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split("\n")

        for line in lines:
            # Extract scores BEFORE reversing (they're at the start of the reversed line)
            original_line = line
            scores = re.findall(r"\d+\.\d+", original_line)
            
            # Fix Arabic text direction (pdfplumber extracts it reversed)
            line = fix_arabic_line(line)
            
            # Detect category (like آداب, رياضيات, علوم...)
            # Check if it's a short line without numbers that matches category patterns
            if (not re.search(r'\d', original_line) and 
                len(original_line.strip()) < 20 and
                any(word in original_line for word in ["ﺏﺍﺩﺁ", "ﻡﻮﻠﻋ", "ﺕﺎﻴﺿﺎﻳﺭ", "ﺩﺎﺼﺘﻗﺍ", "ﺎﻴﺟﻮﻟﻮﻨﻜﺗ", "ﻥﻮﻨﻓ"])):
                current_category = line.strip()  # Store the reversed (readable) version
                continue

            # Detect University (جامعة ...)
            if "ﺔﻌﻣﺎﺟ" in original_line and not re.search(r'\d{2,}', original_line):
                current_university = line.strip()  # Store the reversed (readable) version
                continue

            # Detect faculty/institute (e.g. كلية, معهد, مدرسة)
            if (any(keyword in original_line for keyword in ["ﺔﻴﻠﻛ", "ﺪﻬﻌﻣ", "ﺔﺳﺭﺪﻣ", "ﺔﺳﺭﺪﻤﻟﺍ", "ﺔﻴﻠﻜﻟﺍ", "ﺪﻬﻌﻤﻟﺍ"]) and 
                not re.search(r'\d{2,}', original_line)):
                current_faculty = line.strip()  # Store the reversed (readable) version
                continue

            # Use scores extracted before reversal
            if scores:
                program = re.sub(r"\d+(\.\d+)?", "", line).strip()
                # Try to get scores for 2022, 2023, 2024
                s2022 = scores[0] if len(scores) > 0 else None
                s2023 = scores[1] if len(scores) > 1 else None
                s2024 = scores[2] if len(scores) > 2 else None
                data.append([
                    current_category,
                    current_university,
                    current_faculty,
                    program,
                    s2022, s2023, s2024
                ])

# === 3️⃣ Create DataFrame ===
columns = ["Category", "University", "Faculty", "Program", "2022", "2023", "2024"]
df = pd.DataFrame(data, columns=columns)

# === 4️⃣ Clean duplicates / empty lines ===
df = df.dropna(subset=["Program"]).drop_duplicates()

# === 5️⃣ Save to CSV & Excel ===
df.to_csv("university_scores.csv", index=False, encoding="utf-8-sig")
df.to_excel("university_scores.xlsx", index=False)

print("✅ Extraction complete! Files saved as 'university_scores.csv' and 'university_scores.xlsx'.")
