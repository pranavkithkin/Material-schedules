"""
Test Document Intelligence Integration
Tests the complete flow: PDF upload → n8n extraction → data storage
"""

import pytest
import os
import json
import base64
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Test configuration
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk/webhook')
API_KEY = os.getenv('N8N_TO_FLASK_API_KEY', 'j5mpyk725_PTd7lZ0v99CQSRuk4qsfj1PGbOJ18ziJY')


def create_sample_lpo_pdf():
    """Create a sample LPO/Purchase Order PDF for testing"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # PKP LPO Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "PKP ENGINEERING CONSULTANTS")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 80, "LOCAL PURCHASE ORDER")
    
    # LPO Number (at the top - critical for PKP format detection)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 110, "LPO No: PKP-LPO-6001-2025-51")
    
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 130, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Supplier Details
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 160, "To:")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 180, "M/s ABC Sanitary Wares Trading LLC")
    c.drawString(100, height - 195, "Dubai, UAE")
    c.drawString(100, height - 210, "Phone: +971-4-1234567")
    c.drawString(100, height - 225, "Email: sales@abcsanitary.ae")
    
    # Material Details
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 260, "Material Type: Sanitary Wares")
    
    # Items Table
    y_position = height - 300
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Item")
    c.drawString(300, y_position, "Qty")
    c.drawString(380, y_position, "Unit")
    c.drawString(450, y_position, "Unit Price")
    c.drawString(530, y_position, "Amount")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Item 1
    y_position -= 25
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position, "Basin Mixer - Model BM-300")
    c.drawString(300, y_position, "15")
    c.drawString(380, y_position, "pcs")
    c.drawString(450, y_position, "AED 250.00")
    c.drawString(530, y_position, "AED 3,750.00")
    
    # Item 2
    y_position -= 20
    c.drawString(100, y_position, "Shower Mixer - Model SM-500")
    c.drawString(300, y_position, "20")
    c.drawString(380, y_position, "pcs")
    c.drawString(450, y_position, "AED 320.00")
    c.drawString(530, y_position, "AED 6,400.00")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Total
    y_position -= 25
    c.setFont("Helvetica-Bold", 10)
    c.drawString(450, y_position, "Total Amount:")
    c.drawString(530, y_position, "AED 10,150.00")
    
    # Terms
    y_position -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Payment Terms:")
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position - 15, "50% Advance, 50% on Delivery")
    
    y_position -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Delivery Terms:")
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position - 15, "Delivery within 15 days")
    c.drawString(100, y_position - 30, "Expected Delivery: 2025-10-21")
    
    # Footer
    c.setFont("Helvetica-Italic", 8)
    c.drawString(100, 50, "This is a computer-generated document. No signature required.")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def create_sample_invoice_pdf():
    """Create a sample Invoice PDF for testing"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Invoice Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "ABC SANITARY WARES TRADING LLC")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 80, "TAX INVOICE")
    
    # Invoice Details
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 110, "Invoice No: INV-2025-1523")
    c.drawString(100, height - 130, "Invoice Date: 2025-10-06")
    c.drawString(100, height - 150, "PO Reference: PKP-LPO-6001-2025-51")
    c.drawString(100, height - 170, "Due Date: 2025-11-05")
    
    # Bill To
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 210, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 230, "PKP Engineering Consultants")
    c.drawString(100, height - 245, "Dubai, UAE")
    
    # Items
    y_position = height - 290
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Description")
    c.drawString(350, y_position, "Qty")
    c.drawString(420, y_position, "Unit Price")
    c.drawString(520, y_position, "Amount")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Item 1
    y_position -= 25
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position, "Basin Mixer - Model BM-300")
    c.drawString(350, y_position, "15 pcs")
    c.drawString(420, y_position, "AED 250.00")
    c.drawString(520, y_position, "AED 3,750.00")
    
    # Item 2
    y_position -= 20
    c.drawString(100, y_position, "Shower Mixer - Model SM-500")
    c.drawString(350, y_position, "20 pcs")
    c.drawString(420, y_position, "AED 320.00")
    c.drawString(520, y_position, "AED 6,400.00")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Totals
    y_position -= 30
    c.setFont("Helvetica", 10)
    c.drawString(420, y_position, "Subtotal:")
    c.drawString(520, y_position, "AED 10,150.00")
    
    y_position -= 20
    c.drawString(420, y_position, "VAT (5%):")
    c.drawString(520, y_position, "AED 507.50")
    
    y_position -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(420, y_position, "Total Amount:")
    c.drawString(520, y_position, "AED 10,657.50")
    
    # Payment Terms
    y_position -= 50
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Payment Terms: 30 days from invoice date")
    
    y_position -= 20
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position, "Payment Type: Advance Payment (50%)")
    c.drawString(100, y_position - 15, "Amount Paid: AED 5,328.75")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def create_sample_delivery_note_pdf():
    """Create a sample Delivery Note PDF for testing"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "ABC SANITARY WARES TRADING LLC")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 80, "DELIVERY NOTE")
    
    # Delivery Details
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 110, "Delivery Order No: DO-2025-0823")
    c.drawString(100, height - 130, "Delivery Date: 2025-10-06")
    c.drawString(100, height - 150, "PO Reference: PKP-LPO-6001-2025-51")
    
    # Tracking Info
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 180, "Tracking Number: TRK-UAE-2025-99887")
    c.drawString(100, height - 195, "Carrier: Emirates Fast Logistics")
    
    # Delivery Location
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 230, "Delivered To:")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 250, "PKP Engineering Consultants")
    c.drawString(100, height - 265, "Project Site - Al Barsha, Dubai")
    c.drawString(100, height - 280, "Received By: Ahmed Hassan")
    
    # Items Delivered
    y_position = height - 320
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Item Description")
    c.drawString(350, y_position, "Ordered")
    c.drawString(430, y_position, "Delivered")
    c.drawString(520, y_position, "Status")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Item 1
    y_position -= 25
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position, "Basin Mixer - Model BM-300")
    c.drawString(350, y_position, "15 pcs")
    c.drawString(430, y_position, "15 pcs")
    c.drawString(520, y_position, "✓ Complete")
    
    # Item 2
    y_position -= 20
    c.drawString(100, y_position, "Shower Mixer - Model SM-500")
    c.drawString(350, y_position, "20 pcs")
    c.drawString(430, y_position, "20 pcs")
    c.drawString(520, y_position, "✓ Complete")
    
    c.line(100, y_position - 5, 580, y_position - 5)
    
    # Notes
    y_position -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y_position, "Notes:")
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position - 15, "All items inspected and accepted in good condition")
    c.drawString(100, y_position - 30, "No damages or defects found")
    
    # Signature
    y_position -= 70
    c.setFont("Helvetica", 9)
    c.drawString(100, y_position, "Receiver Signature: _______________________")
    c.drawString(350, y_position, "Date: 2025-10-06")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


class TestDocumentIntelligence:
    """Test suite for Document Intelligence AI Agent"""
    
    def test_pdf_text_extraction_lpo(self, client):
        """Test 1: Extract text from LPO PDF"""
        print("\n" + "="*80)
        print("TEST 1: PDF Text Extraction - Purchase Order")
        print("="*80)
        
        # Create sample LPO PDF
        pdf_bytes = create_sample_lpo_pdf()
        
        # Convert to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Call extraction endpoint
        response = client.post(
            '/api/n8n/extract-pdf-text',
            json={'file_data': pdf_base64},
            headers={'X-API-Key': API_KEY}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200
        
        data = response.get_json()
        print(f"✅ Success: {data['success']}")
        print(f"📄 Pages: {data['num_pages']}")
        print(f"📝 Text Length: {len(data['text'])} characters")
        print(f"\nExtracted Text Preview (first 300 chars):")
        print("-" * 80)
        print(data['text'][:300])
        print("-" * 80)
        
        # Verify key content is extracted
        assert 'PKP-LPO-6001-2025-51' in data['text']
        assert 'ABC Sanitary' in data['text']
        assert '10,150' in data['text'] or '10150' in data['text']
        
        print("✅ TEST PASSED: PDF text extraction working correctly")
        return data['text']
    
    def test_pdf_text_extraction_invoice(self, client):
        """Test 2: Extract text from Invoice PDF"""
        print("\n" + "="*80)
        print("TEST 2: PDF Text Extraction - Invoice")
        print("="*80)
        
        pdf_bytes = create_sample_invoice_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = client.post(
            '/api/n8n/extract-pdf-text',
            json={'file_data': pdf_base64},
            headers={'X-API-Key': API_KEY}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200
        
        data = response.get_json()
        print(f"✅ Success: {data['success']}")
        print(f"📝 Text Preview:")
        print("-" * 80)
        print(data['text'][:300])
        print("-" * 80)
        
        assert 'INV-2025-1523' in data['text']
        assert 'PKP-LPO-6001-2025-51' in data['text']
        
        print("✅ TEST PASSED: Invoice text extraction working")
        return data['text']
    
    def test_pdf_text_extraction_delivery(self, client):
        """Test 3: Extract text from Delivery Note PDF"""
        print("\n" + "="*80)
        print("TEST 3: PDF Text Extraction - Delivery Note")
        print("="*80)
        
        pdf_bytes = create_sample_delivery_note_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        response = client.post(
            '/api/n8n/extract-pdf-text',
            json={'file_data': pdf_base64},
            headers={'X-API-Key': API_KEY}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200
        
        data = response.get_json()
        print(f"✅ Success: {data['success']}")
        print(f"📝 Text Preview:")
        print("-" * 80)
        print(data['text'][:300])
        print("-" * 80)
        
        assert 'DO-2025-0823' in data['text']
        assert 'TRK-UAE-2025-99887' in data['text']
        
        print("✅ TEST PASSED: Delivery note extraction working")
        return data['text']
    
    def test_api_authentication(self, client):
        """Test 4: API Key Authentication"""
        print("\n" + "="*80)
        print("TEST 4: API Authentication")
        print("="*80)
        
        # Test without API key
        response = client.post('/api/n8n/extract-pdf-text', json={})
        print(f"\n❌ Without API Key: Status {response.status_code}")
        assert response.status_code == 401
        
        # Test with wrong API key
        response = client.post(
            '/api/n8n/extract-pdf-text',
            json={},
            headers={'X-API-Key': 'wrong-key'}
        )
        print(f"❌ Wrong API Key: Status {response.status_code}")
        assert response.status_code == 401
        
        # Test with correct API key
        response = client.get(
            '/api/n8n/health',
            headers={'X-API-Key': API_KEY}
        )
        print(f"✅ Correct API Key: Status {response.status_code}")
        assert response.status_code == 200
        
        print("✅ TEST PASSED: Authentication working correctly")
    
    def test_health_check(self, client):
        """Test 5: n8n Health Check"""
        print("\n" + "="*80)
        print("TEST 5: Health Check Endpoint")
        print("="*80)
        
        response = client.get('/api/n8n/health')
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200
        
        data = response.get_json()
        print(f"📊 Service: {data['service']}")
        print(f"✅ Status: {data['status']}")
        print(f"🕐 Timestamp: {data['timestamp']}")
        
        assert data['status'] == 'healthy'
        
        print("✅ TEST PASSED: Health check working")
    
    def test_delivery_extraction_endpoint(self, client):
        """Test 6: Delivery Extraction Endpoint"""
        print("\n" + "="*80)
        print("TEST 6: Delivery Extraction Endpoint")
        print("="*80)
        
        from models.purchase_order import PurchaseOrder
        from models.delivery import Delivery
        from models import db
        
        # Create test PO and Delivery
        po = PurchaseOrder(
            material_id=1,
            po_ref='PKP-LPO-6001-2025-51',
            po_date=datetime(2025, 10, 6),
            supplier_name='ABC Sanitary Wares',
            total_amount=10150.00,
            currency='AED',
            po_status='Released',
            created_by='Test'
        )
        db.session.add(po)
        db.session.flush()
        
        delivery = Delivery(
            po_id=po.id,
            expected_delivery_date=datetime(2025, 10, 21),
            delivery_status='Pending',
            created_by='Test'
        )
        db.session.add(delivery)
        db.session.commit()
        
        # Simulate n8n sending extracted data
        extraction_data = {
            'delivery_id': delivery.id,
            'file_id': 1,
            'extraction_status': 'completed',
            'extraction_confidence': 92.5,
            'extracted_data': {
                'delivery_order_number': 'DO-2025-0823',
                'delivery_date': '2025-10-06',
                'tracking_number': 'TRK-UAE-2025-99887',
                'carrier': 'Emirates Fast Logistics',
                'supplier': 'ABC Sanitary Wares Trading LLC',
                'delivery_location': 'Project Site - Al Barsha, Dubai',
                'received_by': 'Ahmed Hassan',
                'items': [
                    {
                        'item_description': 'Basin Mixer - Model BM-300',
                        'quantity': 15,
                        'unit': 'pcs',
                        'delivered': True
                    },
                    {
                        'item_description': 'Shower Mixer - Model SM-500',
                        'quantity': 20,
                        'unit': 'pcs',
                        'delivered': True
                    }
                ],
                'total_items': 2,
                'notes': 'All items inspected and accepted in good condition'
            }
        }
        
        response = client.post(
            '/api/n8n/delivery-extraction',
            json=extraction_data,
            headers={'X-API-Key': API_KEY}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        assert response.status_code == 200
        
        data = response.get_json()
        print(f"✅ Success: {data['success']}")
        print(f"📦 Delivery ID: {data['delivery_id']}")
        print(f"📊 Confidence: {data['extraction_confidence']}%")
        print(f"📝 Items Extracted: {data['extracted_item_count']}")
        print(f"📈 Delivery %: {data['delivery_percentage']}%")
        print(f"✅ Status: {data['delivery_status']}")
        
        # Verify database update
        updated_delivery = Delivery.query.get(delivery.id)
        assert updated_delivery.extraction_status == 'completed'
        assert updated_delivery.extraction_confidence == 92.5
        assert updated_delivery.extracted_item_count == 2
        assert updated_delivery.delivery_percentage == 100.0
        assert updated_delivery.delivery_status == 'Delivered'
        
        print("✅ TEST PASSED: Delivery extraction and auto-update working")
        
        # Cleanup
        db.session.delete(delivery)
        db.session.delete(po)
        db.session.commit()


def test_save_sample_pdfs():
    """Generate and save sample PDFs for manual testing"""
    print("\n" + "="*80)
    print("GENERATING SAMPLE PDFs FOR MANUAL TESTING")
    print("="*80)
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'test_samples')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate PDFs
    pdfs = {
        'sample_lpo.pdf': create_sample_lpo_pdf(),
        'sample_invoice.pdf': create_sample_invoice_pdf(),
        'sample_delivery_note.pdf': create_sample_delivery_note_pdf()
    }
    
    for filename, pdf_bytes in pdfs.items():
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        print(f"✅ Created: {filepath}")
    
    print(f"\n📁 Sample PDFs saved to: {upload_dir}")
    print("\nYou can use these PDFs to test:")
    print("1. Upload via the web interface")
    print("2. Test n8n workflow manually")
    print("3. Verify AI extraction accuracy")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DOCUMENT INTELLIGENCE TEST SUITE")
    print("="*80)
    print("\nThis test suite validates:")
    print("1. ✅ PDF text extraction (PyPDF2)")
    print("2. ✅ API authentication (API key)")
    print("3. ✅ Health check endpoint")
    print("4. ✅ Delivery extraction endpoint")
    print("5. ✅ Auto-calculation of delivery percentages")
    print("6. ✅ Status auto-update based on completion")
    print("\nRun with: pytest tests/test_document_intelligence.py -v -s")
    print("="*80 + "\n")
    
    # Generate sample PDFs
    test_save_sample_pdfs()
