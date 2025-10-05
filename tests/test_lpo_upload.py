#!/usr/bin/env python3
"""
Real-time LPO Upload Test
Upload a Purchase Order PDF and monitor n8n extraction
"""
import requests
import json
import time
import sys
import os

# Configuration
FLASK_URL = "http://localhost:5001"
API_KEY = "j5mpyk725_PTd7lZ0v99CQSRuk4qsfj1PGbOJ18ziJY"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_existing_pos():
    """Check if we have any Purchase Orders to attach the document to"""
    print_header("STEP 1: Checking Existing Purchase Orders")
    
    try:
        response = requests.get(f"{FLASK_URL}/api/purchase_orders")
        response.raise_for_status()
        pos = response.json()
        
        print_info(f"Found {len(pos)} existing Purchase Orders")
        if len(pos) > 0:
            for po in pos[:5]:
                print(f"  • PO #{po['id']}: {po['po_ref']} - {po.get('supplier_name', 'N/A')}")
        
        return pos
    except Exception as e:
        print_error(f"Failed to fetch POs: {e}")
        return []

def create_test_po():
    """Create a NEW test Purchase Order for the LPO upload"""
    print_header("STEP 2: Creating NEW Purchase Order for LPO")
    
    po_data = {
        "material_id": 1,
        "po_ref": f"LPO-TEST-{int(time.time())}",  # Unique PO ref
        "supplier_name": "Pending AI Extraction",  # Will be updated by AI
        "total_amount": 0,  # Will be filled by AI extraction
        "currency": "AED",
        "po_status": "Draft"
    }
    
    try:
        response = requests.post(
            f"{FLASK_URL}/api/purchase_orders",
        )
        response.raise_for_status()
        po = response.json()
        
        print_success(f"Created test PO: {po['purchase_order']['po_ref']} (ID: {po['purchase_order']['id']})")
        return po['purchase_order']['id']
    except Exception as e:
        print_error(f"Failed to create PO: {e}")
        return None

def upload_lpo(po_id, pdf_path):
    """Upload LPO PDF and trigger n8n workflow"""
    print_header("STEP 3: Uploading LPO Document")
    
    print_info(f"Uploading: {pdf_path}")
    print_info(f"Target PO ID: {po_id}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            data = {'uploaded_by': 'Test Script'}
            
            response = requests.post(
                f"{FLASK_URL}/api/purchase-orders/{po_id}/upload-document",
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            print_success("Upload successful!")
            print_info(f"File ID: {result['file_id']}")
            print_info(f"Extraction Status: {result['extraction_status']}")
            print_info(f"n8n Triggered: {result.get('n8n_triggered', False)}")
            
            return result['file_id']
    except Exception as e:
        print_error(f"Upload failed: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def monitor_extraction(file_id, timeout=60):
    """Monitor the extraction process"""
    print_header("STEP 4: Monitoring AI Extraction")
    
    print_info("Waiting for n8n to process the document...")
    print_info("This may take 10-30 seconds depending on document size")
    
    start_time = time.time()
    dots = 0
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{FLASK_URL}/api/files/{file_id}")
            file_data = response.json()
            
            status = file_data['file']['processing_status']
            
            if status == 'completed':
                print("\n")
                print_success("Extraction completed!")
                return file_data['file']
            elif status == 'failed':
                print("\n")
                print_error("Extraction failed!")
                print_error(f"Error: {file_data['file'].get('error_message', 'Unknown error')}")
                return None
            else:
                dots = (dots + 1) % 4
                print(f"⏳ Status: {status} - processing{'.' * dots}   ", end='\r')
            
            time.sleep(2)
            
        except Exception as e:
            print_error(f"\nError checking status: {e}")
            time.sleep(2)
    
    print("\n")
    print_error(f"Timeout after {timeout} seconds")
    return None

def display_results(file_data, po_id):
    """Display extraction results"""
    print_header("STEP 5: Extraction Results")
    
    if not file_data:
        print_error("No extraction data available")
        return
    
    print_success(f"Processing Status: {file_data['processing_status']}")
    print_info(f"Extraction Confidence: {file_data.get('extraction_confidence', 0)}%")
    
    if file_data.get('extracted_data'):
        print("\n📄 Extracted Data:")
        extracted = file_data['extracted_data']
        if isinstance(extracted, str):
            try:
                extracted = json.loads(extracted)
            except:
                pass
        print(json.dumps(extracted, indent=2))
    
    print_header("STEP 6: Checking Updated Purchase Order")
    
    try:
        response = requests.get(f"{FLASK_URL}/api/purchase_orders/{po_id}")
        po = response.json()
        
        print_info("Purchase Order Details:")
        print(f"  PO Reference: {po.get('po_ref', 'N/A')}")
        print(f"  Supplier: {po.get('supplier_name', 'N/A')}")
        print(f"  Total Amount: {po.get('total_amount', 0)} {po.get('currency', 'AED')}")
        print(f"  PO Date: {po.get('po_date', 'N/A')}")
        print(f"  Expected Delivery: {po.get('expected_delivery_date', 'N/A')}")
        
        if po.get('items'):
            print(f"\n  📦 Items ({len(po['items'])}):")
            for idx, item in enumerate(po['items'][:5], 1):
                print(f"    {idx}. {item.get('description', 'N/A')} - Qty: {item.get('quantity', 0)}")
        
    except Exception as e:
        print_error(f"Could not fetch updated PO: {e}")

def main():
    print_header("�� LPO Upload & n8n Extraction Test")
    print_info("This script will:")
    print("  1. Check existing Purchase Orders")
    print("  2. Create a test PO (or use existing)")
    print("  3. Upload your LPO PDF")
    print("  4. Trigger n8n workflow")
    print("  5. Monitor extraction progress")
    print("  6. Display results\n")
    
    if len(sys.argv) < 2:
        print_error("Please provide the path to your LPO PDF file")
        print(f"\nUsage: python {sys.argv[0]} /path/to/lpo.pdf [po_id]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} ~/Downloads/company_lpo.pdf")
        print(f"  python {sys.argv[0]} ~/Downloads/company_lpo.pdf 1")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print_error(f"File not found: {pdf_path}")
        sys.exit(1)
    
    print_success(f"Found PDF: {os.path.basename(pdf_path)}")
    print_info(f"File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    
    # Check existing POs
    existing_pos = check_existing_pos()
    
    # Determine PO ID
    if len(sys.argv) >= 3:
        po_id = int(sys.argv[2])
        print_info(f"Using provided PO ID: {po_id}")
    elif existing_pos:
        po_id = existing_pos[0]['id']
        print_info(f"Using first existing PO ID: {po_id}")
    else:
        po_id = create_test_po()
        if not po_id:
            print_error("Failed to create test PO. Exiting.")
            sys.exit(1)
    
    # Upload PDF
    file_id = upload_lpo(po_id, pdf_path)
    if not file_id:
        print_error("Upload failed. Exiting.")
        sys.exit(1)
    
    # Monitor extraction
    file_data = monitor_extraction(file_id, timeout=90)
    
    # Display results
    display_results(file_data, po_id)
    
    print_header("✅ Test Complete!")
    
    if file_data and file_data.get('processing_status') == 'completed':
        print_success("Your LPO was successfully processed by n8n!")
        print_info(f"View the updated PO at: {FLASK_URL}/purchase_orders")
    else:
        print_error("Extraction did not complete successfully")
        print_info("Check n8n workflow logs at: https://n8n1.trart.uk")

if __name__ == "__main__":
    main()
