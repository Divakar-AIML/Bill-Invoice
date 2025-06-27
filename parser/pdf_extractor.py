import pdfplumber
import re

def extract_lines_with_metadata(pdf_path):
    all_lines = []
    current_section = None
    metadata = {
        'invoice_number': None,
        'quote_date': None,
        'sold_to': None,
        'ship_to': None
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.splitlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if not metadata['invoice_number']:
                    match = re.search(r'(\d{5,})\s+\d+\s+of\s+\d+', line)
                    if match:
                        metadata['invoice_number'] = match.group(1)

                if not metadata['quote_date']:
                    match = re.search(r"QUOTE\s+(\d{1,2}/\d{1,2}/\d{4})", line)
                    if match:
                        metadata['quote_date'] = match.group(1)

                if not metadata['sold_to']:
                    match = re.search(r"SOLD\s+(.*?)\s+SHIP", line)
                    if match:
                        metadata['sold_to'] = match.group(1).strip()

                if not metadata['ship_to']:
                    match = re.search(r"SHIP\s+(.*?)\s+(Lake Zurich|IL)", line)
                    if match:
                        metadata['ship_to'] = match.group(1).strip()

                section_match = re.search(r'(Frozen|Grocery|Refrigerated|Mix Misc)\s*-+', line)
                if section_match:
                    current_section = section_match.group(1)
                    continue

                if any(skip in line for skip in [
                    "QUOTE", "CONTINUED ON NEXT PAGE", "NO Refunds", "Write Invoice"
                ]):
                    continue

                all_lines.append((line, current_section))

    return all_lines, metadata
