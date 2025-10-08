"""
Analyze sample LPO and Quote documents to understand format
Extract structure, fields, and layout for HTML template creation
"""

import pdfplumber
import json
from pathlib import Path

def analyze_pdf(pdf_path, doc_type):
    """Extract text and analyze structure from PDF"""
    print(f"\n{'='*80}")
    print(f"Analyzing {doc_type}: {Path(pdf_path).name}")
    print(f"{'='*80}\n")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total Pages: {len(pdf.pages)}\n")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"--- PAGE {page_num} ---\n")
                
                # Extract text
                text = page.extract_text()
                print(text)
                print("\n")
                
                # Extract tables if any
                tables = page.extract_tables()
                if tables:
                    print(f"Found {len(tables)} table(s) on page {page_num}")
                    for i, table in enumerate(tables, 1):
                        print(f"\nTable {i}:")
                        for row in table[:5]:  # Show first 5 rows
                            print(row)
                        if len(table) > 5:
                            print(f"... ({len(table) - 5} more rows)")
                    print("\n")
                
                print(f"{'='*80}\n")
    
    except Exception as e:
        print(f"Error analyzing {pdf_path}: {e}\n")

def main():
    # Sample document paths
    base_path = Path("sample documents")
    
    # Analyze LPOs
    lpo_single = base_path / "sample lpo" / "sample single page.pdf"
    lpo_multi = base_path / "sample lpo" / "sample multi page.pdf"
    
    # Analyze Quote
    quote = base_path / "sample quote" / "115697 PKP -AL Nawras.pdf"
    
    # Analyze each document
    if lpo_single.exists():
        analyze_pdf(lpo_single, "LPO - Single Page")
    else:
        print(f"File not found: {lpo_single}")
    
    if lpo_multi.exists():
        analyze_pdf(lpo_multi, "LPO - Multi Page")
    else:
        print(f"File not found: {lpo_multi}")
    
    if quote.exists():
        analyze_pdf(quote, "Supplier Quote")
    else:
        print(f"File not found: {quote}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review extracted text above")
    print("2. Identify LPO template structure")
    print("3. Identify quote data fields")
    print("4. Create HTML template matching LPO format")
    print("5. Create GPT-4 prompt for quote parsing")

if __name__ == "__main__":
    main()
