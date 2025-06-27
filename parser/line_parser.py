# parser/line_parser.py

import re

def parse_product_line(line_text, section):
    """
    Extracts fields from a single product line.
    Returns a dictionary with structured data or None if it fails.
    """

    # Regex pattern: Qty (Code) (Description) UnitPrice TotalPrice
    pattern = r"^(\d+)\s+([A-Z0-9 ]{5,})\s+(.*?)\s+([\d]+\.\d{2})\s+([\d]+\.\d{2})$"
    match = re.match(pattern, line_text)

    if not match:
        return None  # Line doesn't match, we’ll log it later

    quantity = int(match.group(1))
    product_code = match.group(2).strip()
    description = match.group(3).strip()
    unit_price = float(match.group(4))
    total_price = float(match.group(5))

    packet_qty_match = re.search(r'\((\d{1,4})\)$', description)
    packet_qty = int(packet_qty_match.group(1)) if packet_qty_match else None

    result = {
        "Section": section or "Unknown",
        "Quantity": quantity,
        "Product Code": product_code,
        "Description": description,
        "Packet Quantity": packet_qty,
        "Unit Price": unit_price,
        "Total Price": total_price,
        "Unit Price Per Item": round(unit_price / packet_qty, 2) if packet_qty else None
    }
    return result
