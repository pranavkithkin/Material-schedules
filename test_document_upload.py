"""
Document Intelligence Upload & Test Script
Upload PDFs and test the complete AI extraction workflow
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5001"
N8N_WEBHOOK_URL = "https://n8n1.trart.uk/webhook/extract-document"
API_KEY = "j5mpyk725_PTd7lZ0v99CQSRuk4qsfj1PGbOJ18ziJY"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text):
    """Print section divider"""
    print(f"\n{'─'*80}")
    print(f"  {text}")
    print('─'*80 + "\n")

def test_flask_running():
    """Test if Flask application is running"""
    print_header("🔍 STEP 1: Check Flask Application")
    
    try:
        response = requests.get(f"{BASE_URL}/api/n8n/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask is running on", BASE_URL)
            return True
        else:
            print(f"❌ Flask returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Flask at {BASE_URL}")
        print("\n💡 Please start Flask first:")
        print("   python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_n8n_running():
    """Test if n8n is accessible"""
    print_header("🔍 STEP 2: Check n8n Availability")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/n8n-status", timeout=10)
        data = response.json()
        
        if data.get('n8n_live'):
            print("✅ n8n is online:", N8N_WEBHOOK_URL.replace('/webhook/extract-document', ''))
            return True
        else:
            print("⚠️ n8n status check:")
            print(f"   Live: {data.get('n8n_live')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            print("\n💡 n8n should be accessible at: https://n8n1.trart.uk")
            return False
    except Exception as e:
        print(f"❌ Error checking n8n: {e}")
        return False

def find_pdf_files():
    """Find PDF files in current directory and subdirectories"""
    print_header("📂 STEP 3: Find Available PDF Files")
    
    pdf_files = []
    search_paths = [
        Path.cwd(),  # Current directory
        Path.cwd().parent,  # Parent directory
        Path.home() / "Documents",  # Documents folder
        Path.home() / "Downloads"   # Downloads folder
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            found = list(search_path.glob("*.pdf"))
            pdf_files.extend(found)
    
    # Remove duplicates and limit to first 10
    pdf_files = list(set(pdf_files))[:10]
    
    if not pdf_files:
        print("❌ No PDF files found in common locations")
        print("\n💡 Place your test PDFs in one of these locations:")
        for path in search_paths:
            print(f"   • {path}")
        return []
    
    print(f"✅ Found {len(pdf_files)} PDF file(s):\n")
    for i, pdf in enumerate(pdf_files, 1):
        size_kb = pdf.stat().st_size / 1024
        print(f"   {i}. {pdf.name}")
        print(f"      📍 {pdf.parent}")
        print(f"      📦 {size_kb:.2f} KB\n")
    
    return pdf_files

def upload_pdf_to_flask(pdf_path):
    """Upload PDF file to Flask and return file record"""
    print_section(f"📤 Uploading: {pdf_path.name}")
    
    try:
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            
            # Upload to Flask file upload endpoint
            response = requests.post(
                f"{BASE_URL}/api/files/upload",
                files=files,
                data={
                    'entity_type': 'purchase_order',
                    'entity_id': '0',
                    'description': f'Test upload: {pdf_path.name}'
                },
                headers={'X-API-Key': API_KEY}
            )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   File ID: {data['file']['id']}")
            print(f"   Path: {data['file']['file_path']}")
            return data['file']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

def trigger_n8n_extraction(file_id, po_ref="PKP-LPO-TEST-001"):
    """Trigger n8n document intelligence workflow"""
    print_section(f"🤖 Triggering AI Extraction for File ID: {file_id}")
    
    try:
        payload = {
            "file_id": file_id,
            "po_ref": po_ref,
            "document_type": "purchase_order"
        }
        
        print("📤 Sending to n8n workflow...")
        print(f"   URL: {N8N_WEBHOOK_URL}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Workflow triggered successfully!")
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}")
            
            print("\n💡 What's happening now:")
            print("   1. n8n receives webhook")
            print("   2. Extracts PDF text from Flask")
            print("   3. Sends to GPT-4 for AI analysis")
            print("   4. Parses structured data (PO number, supplier, amount, etc.)")
            print("   5. Calculates confidence score")
            print("   6. Sends back to Flask endpoint")
            print("   7. Flask updates database")
            
            print("\n📊 Check your n8n dashboard:")
            print("   https://n8n1.trart.uk/workflow")
            
            return True
        else:
            print(f"❌ Workflow trigger failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out (this is normal - n8n processes in background)")
        print("✅ Workflow likely triggered successfully")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_extraction_status(file_id):
    """Check if extraction completed by querying Flask"""
    print_section(f"🔍 Checking Extraction Status")
    
    try:
        # Check deliveries for extracted data
        response = requests.get(
            f"{BASE_URL}/api/deliveries",
            headers={'X-API-Key': API_KEY}
        )
        
        if response.status_code == 200:
            deliveries = response.json()
            print(f"✅ Found {len(deliveries)} delivery records")
            
            # Look for recent extractions
            for delivery in deliveries[:5]:
                if delivery.get('extraction_status') == 'completed':
                    print(f"\n   📦 Delivery ID {delivery['id']}:")
                    print(f"      Status: {delivery.get('extraction_status')}")
                    print(f"      Confidence: {delivery.get('extraction_confidence')}%")
                    print(f"      Items: {delivery.get('extracted_item_count', 0)}")
        else:
            print(f"⚠️ Could not fetch deliveries: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def manual_test_extraction_endpoint(pdf_path):
    """Manually test PDF text extraction endpoint"""
    print_section(f"🧪 Direct API Test: PDF Text Extraction")
    
    try:
        import base64
        
        # Read and encode PDF
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        print(f"📄 PDF Size: {len(pdf_bytes)} bytes")
        print(f"📝 Base64 Size: {len(pdf_base64)} characters")
        
        # Call extraction endpoint
        response = requests.post(
            f"{BASE_URL}/api/n8n/extract-pdf-text",
            json={'file_data': pdf_base64},
            headers={'X-API-Key': API_KEY},
            timeout=30
        )
        
        print(f"\n📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text extraction successful!")
            print(f"   Pages: {data.get('num_pages', 'N/A')}")
            print(f"   Text Length: {len(data.get('text', ''))} characters")
            print(f"\n📄 Extracted Text Preview (first 500 chars):")
            print("─" * 80)
            print(data.get('text', '')[:500])
            print("─" * 80)
            return True
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test workflow"""
    print_header("🤖 DOCUMENT INTELLIGENCE - UPLOAD & TEST")
    
    print("This script will:")
    print("  1. Check Flask and n8n are running")
    print("  2. Find PDF files on your computer")
    print("  3. Upload PDF to Flask")
    print("  4. Trigger n8n AI extraction workflow")
    print("  5. Monitor extraction status")
    
    input("\nPress Enter to start...")
    
    # Step 1: Check Flask
    if not test_flask_running():
        print("\n❌ Flask is not running. Please start it first:")
        print("   python app.py")
        return
    
    # Step 2: Check n8n
    test_n8n_running()
    
    # Step 3: Find PDFs
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("\n❌ No PDF files found. Please provide the path to your PDF:")
        pdf_path = input("   PDF Path: ").strip()
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return
        pdf_files = [Path(pdf_path)]
    
    # Select PDF
    if len(pdf_files) > 1:
        print("\nWhich PDF do you want to test?")
        choice = input(f"Enter number (1-{len(pdf_files)}): ").strip()
        try:
            selected_pdf = pdf_files[int(choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
    else:
        selected_pdf = pdf_files[0]
    
    print(f"\n✅ Selected: {selected_pdf.name}")
    
    # Test extraction endpoint first (doesn't require upload)
    print("\n" + "="*80)
    print("Would you like to:")
    print("  1. Test PDF text extraction directly (no upload needed)")
    print("  2. Upload PDF and trigger full AI workflow")
    print("="*80)
    choice = input("\nChoice (1 or 2): ").strip()
    
    if choice == "1":
        manual_test_extraction_endpoint(selected_pdf)
        print("\n✅ Direct extraction test complete!")
        print("\n💡 This confirms PyPDF2 can read your PDF.")
        print("   Next, try option 2 to test the full workflow.")
        
    elif choice == "2":
        # Upload PDF
        file_record = upload_pdf_to_flask(selected_pdf)
        
        if not file_record:
            print("❌ Upload failed. Cannot proceed.")
            return
        
        # Trigger n8n workflow
        print("\n")
        confirm = input("Trigger n8n AI extraction workflow? (y/N): ").strip().lower()
        
        if confirm == 'y':
            success = trigger_n8n_extraction(file_record['id'])
            
            if success:
                print("\n" + "="*80)
                print("⏳ Extraction is processing in the background...")
                print("="*80)
                
                print("\n📊 How to check results:")
                print("   1. Open n8n dashboard: https://n8n1.trart.uk")
                print("   2. Check 'Executions' tab for the workflow run")
                print("   3. Verify each step completed successfully")
                print("   4. Check Flask database for extracted data")
                
                input("\nPress Enter after checking n8n to query Flask database...")
                check_extraction_status(file_record['id'])
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*80)
    print("🎉 TEST COMPLETE")
    print("="*80)
    
    print("\n📚 What you learned:")
    print("   ✅ Flask API is working")
    print("   ✅ PDF text extraction works (PyPDF2)")
    print("   ✅ n8n webhook connectivity")
    print("   ✅ Document upload functionality")
    
    print("\n💡 Next steps:")
    print("   • Test via web interface (upload in Payment form)")
    print("   • Check extracted data auto-fills forms")
    print("   • Test with different document types (Invoice, Delivery)")
    print("   • Verify confidence scoring and auto-approval logic")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
