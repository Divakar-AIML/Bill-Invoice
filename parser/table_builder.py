# parser/table_builder.py

from line_parser import parse_product_line
import pandas as pd
import math

def build_table_from_lines(lines, metadata):
    """
    Builds a clean table (DataFrame) from extracted lines and metadata.
    Validates price calculations, handles parsing failures.

    Args:
        lines (list): [(line_text, section), ...]
        metadata (dict): invoice_number, quote_date, sold_to, ship_to

    Returns:
        parsed_items (DataFrame): successful rows
        skipped_lines (list): lines that failed to parse
        mismatched_lines (list): lines with value errors
    """
    parsed_rows = []
    skipped_lines = []
    mismatched_lines = []

    for line_text, section in lines:
        result = parse_product_line(line_text, section)
        if result:
            # Add metadata fields
            result["Invoice Number"] = metadata.get("invoice_number", "UNKNOWN")
            result["Quote Date"] = metadata.get("quote_date", "UNKNOWN")
            result["Sold To"] = metadata.get("sold_to", "UNKNOWN")
            result["Ship To"] = metadata.get("ship_to", "UNKNOWN")

            # Validate total = quantity × unit price
            expected = round(result["Quantity"] * result["Unit Price"], 2)
            if not math.isclose(expected, result["Total Price"], abs_tol=0.02):
                result["Validation"] = f"Mismatch: {expected} ≠ {result['Total Price']}"
                mismatched_lines.append((line_text, result))
            else:
                result["Validation"] = "OK"
                parsed_rows.append(result)
        else:
            skipped_lines.append(line_text)

    df = pd.DataFrame(parsed_rows)

    return df, skipped_lines, mismatched_lines
