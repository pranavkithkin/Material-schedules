"""
Test script to verify LPO creation and PDF generation
Creates a sample LPO manually and generates PDF
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from services.lpo_service import LPOService
from services.lpo_pdf_generator import LPOPDFGenerator
from datetime import date

def test_lpo_creation():
    """Test creating an LPO and generating PDF"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("TESTING LPO CREATION & PDF GENERATION")
        print("=" * 60)
        
        # Sample LPO data - Steel supplier with MAKE column
        lpo_data = {
            'supplier_name': 'ABC Steel Trading LLC',
            'supplier_trn': '100123456700003',
            'supplier_address': 'Industrial Area 3, Sharjah, UAE',
            'supplier_tel': '+971-6-1234567',
            'supplier_fax': '+971-6-1234568',
            'contact_person': 'Mohammed Ahmed',
            'contact_number': '+971-50-1234567',
            
            'project_name': 'Villa Construction - Al Barsha',
            'project_location': 'Al Barsha, Dubai',
            
            'quotation_ref': 'QT-2025-001',
            'quotation_date': date(2025, 10, 5),
            
            # Dynamic column structure - Steel supplier has MAKE column
            'column_structure': ['MAKE', 'CODE', 'DESCRIPTION', 'UNIT', 'QTY', 'UNIT PRICE', '5%'],
            
            'items': [
                {
                    'number': 1,
                    'make': 'Tata Steel',
                    'code': 'TMT-16',
                    'description': 'TMT Steel Bar 16mm',
                    'unit': 'Ton',
                    'quantity': 5.0,
                    'unit_price': 2800.00,
                    'vat_amount': 700.00,
                    'total_amount': 14700.00
                },
                {
                    'number': 2,
                    'make': 'Jindal',
                    'code': 'TMT-20',
                    'description': 'TMT Steel Bar 20mm',
                    'unit': 'Ton',
                    'quantity': 3.0,
                    'unit_price': 2850.00,
                    'vat_amount': 427.50,
                    'total_amount': 8977.50
                },
                {
                    'number': 3,
                    'make': 'Local',
                    'code': 'MESH-6',
                    'description': 'Welded Wire Mesh 6mm',
                    'unit': 'Sqm',
                    'quantity': 100.0,
                    'unit_price': 25.00,
                    'vat_amount': 125.00,
                    'total_amount': 2625.00
                }
            ],
            
            'notes': 'Delivery within 7 days. Payment terms: 30 days from delivery.',
            'terms': 'All materials should be as per approved specifications.'
        }
        
        try:
            # Step 1: Create LPO
            print("\n1. Creating LPO...")
            lpo = LPOService.create_lpo(lpo_data)
            print(f"   ✓ LPO Created: {lpo.lpo_number}")
            print(f"   - Supplier: {lpo.supplier_name}")
            print(f"   - Project: {lpo.project_name}")
            print(f"   - Items: {lpo.item_count}")
            print(f"   - Subtotal: AED {lpo.subtotal:,.2f}")
            print(f"   - VAT (5%): AED {lpo.vat_amount:,.2f}")
            print(f"   - Total: AED {lpo.total_amount:,.2f}")
            print(f"   - Status: {lpo.status}")
            
            # Step 2: Generate PDF
            print("\n2. Generating PDF...")
            pdf_path = f"uploads/lpos/{lpo.lpo_number.replace('/', '_')}.pdf"
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            pdf_file = LPOPDFGenerator.generate_pdf(lpo, pdf_path)
            print(f"   ✓ PDF Generated: {pdf_file}")
            print(f"   - File size: {os.path.getsize(pdf_file):,} bytes")
            
            # Step 3: Update status to issued
            print("\n3. Issuing LPO...")
            updated_lpo = LPOService.change_status(lpo.id, 'issued', performed_by='System Test', notes='LPO issued to supplier')
            print(f"   ✓ Status updated: {updated_lpo.status}")
            print(f"   - Issued at: {updated_lpo.issued_at}")
            
            # Step 4: Retrieve and display
            print("\n4. Retrieving LPO...")
            retrieved_lpo = LPOService.get_lpo(lpo.id)
            print(f"   ✓ Retrieved: {retrieved_lpo.lpo_number}")
            print(f"   - Column structure: {retrieved_lpo.column_structure}")
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED!")
            print("=" * 60)
            print(f"\nLPO Number: {lpo.lpo_number}")
            print(f"PDF Location: {pdf_file}")
            print(f"\nNext steps:")
            print(f"1. Open the PDF to verify formatting")
            print(f"2. Test with different column structures (electrical, services)")
            print(f"3. Integrate with quote upload for Phase 5B")
            
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_lpo_creation()
    sys.exit(0 if success else 1)
