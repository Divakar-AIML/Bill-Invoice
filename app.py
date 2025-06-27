import streamlit as st
import os
import sys
import tempfile
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "exporter"))

from pdf_extractor import extract_lines_with_metadata
from table_builder import build_table_from_lines
from excel_writer import write_excel


# Page settings
st.set_page_config(page_title="Bill to Excel Converter", layout="wide")

st.title("🧾 Bill-to-Excel Converter")
st.markdown("Upload one or more invoice PDF files to extract items and generate a structured Excel file.")

uploaded_files = st.file_uploader("Upload Bill PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_df = []
    all_summary = []
    all_skipped = []
    all_mismatched = []

    with st.spinner("🔍 Processing uploaded PDF(s)..."):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            lines, metadata = extract_lines_with_metadata(tmp_path)
            df, skipped, mismatched = build_table_from_lines(lines, metadata)

            all_df.append(df)

            # Build summary for this bill
            if not df.empty:
                summary = df.groupby("Section")[["Total Price"]].sum().reset_index()
                summary["Invoice Number"] = metadata.get("invoice_number", "")
                summary["Quote Date"] = metadata.get("quote_date", "")
                summary["Sold To"] = metadata.get("sold_to", "")
                summary = summary[["Invoice Number", "Quote Date", "Sold To", "Section", "Total Price"]]
                all_summary.append(summary)

            for line in skipped:
                all_skipped.append(line)
            for mismatch in mismatched:
                all_mismatched.append(mismatch)
    

    final_df = pd.concat(all_df, ignore_index=True)
    final_summary = pd.concat(all_summary, ignore_index=True) if all_summary else None

    if "Ship To" in df.columns:
        df = df.drop(columns=["Ship To"])

    st.success("✅ Processing complete!")

    st.subheader("📦 Extracted Items Preview")
    st.dataframe(final_df)

    if final_summary is not None:
        st.subheader("🧾 Bill Summary")
        st.dataframe(final_summary)

    if all_skipped or all_mismatched:
        st.subheader("⚠️ Warnings")
        if all_skipped:
            st.markdown("**Skipped Lines:**")
            for l in all_skipped:
                st.code(l)
        if all_mismatched:
            st.markdown("**Mismatched Lines:**")
            for l, reason in all_mismatched:
                st.code(f"{l} --> {reason['Validation']}")

    # Generate Excel
    output_path = write_excel(final_df, final_summary, all_skipped, all_mismatched)

    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 Download Excel",
            data=f,
            file_name=os.path.basename(output_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
