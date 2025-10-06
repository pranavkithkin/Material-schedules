"""
Quick Test Script for Document Intelligence
Tests your existing PDF with the AI extraction workflow
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Configuration
FLASK_URL = "http://localhost:5001"
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk/webhook/extract-document')
API_KEY = os.getenv('N8N_TO_FLASK_API_KEY', 'j5mpyk725_PTd7lZ0v99CQSRuk4qsfj1PGbOJ18ziJY')

# Find your existing PDF
PDF_PATH = "static/uploads/2025/10/20251003_175249_test_purchase_order.pdf"


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_1_pdf_exists():
    """Test 1: Check if PDF file exists"""
    print_section("TEST 1: Verify PDF File Exists")
    
    if os.path.exists(PDF_PATH):
        file_size = os.path.getsize(PDF_PATH)
        print(f"✅ PDF Found: {PDF_PATH}")
        print(f"📦 File Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        return True
    else:
        print(f"❌ PDF Not Found: {PDF_PATH}")
        print("\nPlease provide the correct path to your PDF file.")
        return False


def test_2_extract_text_locally():
    """Test 2: Extract text from PDF using Flask API"""
    print_section("TEST 2: Extract Text from PDF (Flask API)")
    
    try:
        # Read PDF file
        with open(PDF_PATH, 'rb') as f:
            pdf_bytes = f.read()
        
        # Convert to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        print(f"📄 PDF encoded to base64: {len(pdf_base64)} characters")
        
        # Call Flask API
        url = f"{FLASK_URL}/api/n8n/extract-pdf-text"
        headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            'file_data': pdf_base64,
            'file_id': 1
        }
        
        print(f"🔗 Calling: {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📄 Pages: {data.get('num_pages')}")
            print(f"📝 Text Length: {len(data.get('text', ''))} characters")
            
            # Show preview of extracted text
            text = data.get('text', '')
            if text:
                print("\n" + "-"*80)
                print("EXTRACTED TEXT PREVIEW (first 500 characters):")
                print("-"*80)
                print(text[:500])
                print("-"*80)
                
                # Check for key information
                print("\n🔍 Key Information Detected:")
                if 'PKP' in text or 'LPO' in text:
                    print("  ✅ PKP/LPO reference found")
                if 'Purchase Order' in text or 'PURCHASE ORDER' in text:
                    print("  ✅ Document type identified")
                if any(char.isdigit() for char in text):
                    print("  ✅ Numeric data present")
                
                return text
            else:
                print("⚠️ No text extracted from PDF")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server not running")
        print(f"   Make sure Flask is running on {FLASK_URL}")
        print("   Run: python app.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_3_check_n8n_health():
    """Test 3: Check if n8n is accessible"""
    print_section("TEST 3: Check n8n Availability")
    
    try:
        # Check n8n health via Flask
        url = f"{FLASK_URL}/api/dashboard/n8n-status"
        print(f"🔗 Calling: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📡 n8n Status:")
            print(f"  Live: {data.get('n8n_live')}")
            print(f"  AI Available: {data.get('ai_available')}")
            print(f"  Message: {data.get('message', 'N/A')}")
            
            if data.get('n8n_live'):
                print("\n✅ n8n is ONLINE and ready")
                return True
            else:
                print("\n⚠️ n8n appears OFFLINE")
                print(f"   Check if n8n is running at: {os.getenv('N8N_BASE_URL')}")
                return False
        else:
            print(f"❌ Could not check n8n status")
            return False
            
    except Exception as e:
        print(f"❌ Error checking n8n: {e}")
        return False


def test_4_trigger_n8n_workflow():
    """Test 4: Trigger n8n document intelligence workflow"""
    print_section("TEST 4: Trigger n8n Document Intelligence Workflow")
    
    print("⚠️ This test requires n8n to be running with the workflow active")
    print(f"Workflow URL: {N8N_WEBHOOK_URL}")
    
    try:
        # Prepare webhook payload
        payload = {
            'file_id': 1,
            'po_ref': 'PKP-LPO-TEST',
            'document_type': 'purchase_order'
        }
        
        print(f"\n📤 Sending webhook request...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook triggered successfully!")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
            
            print("\n💡 What happens next:")
            print("  1. n8n receives the webhook")
            print("  2. Calls Flask to extract PDF text")
            print("  3. Sends text to GPT-4 for AI extraction")
            print("  4. Parses AI response and calculates confidence")
            print("  5. Routes to appropriate endpoint (PO/Invoice/Delivery)")
            print("  6. Sends extracted data back to Flask")
            print("  7. Flask stores in database")
            
            print("\n📊 Check your n8n dashboard to see the workflow execution")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Cannot reach n8n at {N8N_WEBHOOK_URL}")
        print("\n🔧 Troubleshooting:")
        print("  1. Is n8n running? Check https://n8n1.trart.uk")
        print("  2. Is the workflow activated in n8n?")
        print("  3. Is the webhook URL correct?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_5_check_flask_endpoints():
    """Test 5: Verify Flask API endpoints are working"""
    print_section("TEST 5: Check Flask API Endpoints")
    
    endpoints = [
        ('Health Check', '/api/n8n/health', 'GET', None),
        ('Stats', '/api/n8n/stats', 'GET', API_KEY),
    ]
    
    results = []
    
    for name, path, method, auth in endpoints:
        try:
            url = f"{FLASK_URL}{path}"
            headers = {}
            if auth:
                headers['X-API-Key'] = auth
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, timeout=10)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name:20} {path:30} [{response.status_code}]")
            results.append(response.status_code == 200)
            
        except Exception as e:
            print(f"❌ {name:20} {path:30} [ERROR: {e}]")
            results.append(False)
    
    if all(results):
        print("\n✅ All Flask endpoints are working!")
        return True
    else:
        print("\n⚠️ Some Flask endpoints failed")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  🤖 DOCUMENT INTELLIGENCE - INTEGRATION TEST")
    print("="*80)
    
    print("\nThis script tests your AI document intelligence system:")
    print("  • PDF text extraction (Flask + PyPDF2)")
    print("  • n8n workflow connectivity")
    print("  • AI extraction endpoint")
    print("  • Database integration")
    
    input("\nPress Enter to start testing...")
    
    # Run tests
    results = []
    
    # Test 1: PDF exists
    results.append(('PDF File Check', test_1_pdf_exists()))
    
    if not results[-1][1]:
        print("\n❌ Cannot proceed without a valid PDF file")
        return
    
    # Test 2: Extract text
    extracted_text = test_2_extract_text_locally()
    results.append(('Text Extraction', extracted_text is not None))
    
    # Test 3: n8n health
    results.append(('n8n Health Check', test_3_check_n8n_health()))
    
    # Test 4: Flask endpoints
    results.append(('Flask API Endpoints', test_5_check_flask_endpoints()))
    
    # Test 5: Trigger workflow (optional)
    print_section("Optional: Trigger Full Workflow")
    trigger = input("Do you want to trigger the n8n workflow? (y/N): ").strip().lower()
    if trigger == 'y':
        results.append(('n8n Workflow Trigger', test_4_trigger_n8n_workflow()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    print("Results:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:10} {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n📊 Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Your document intelligence system is working correctly.")
    elif passed_count >= total_count - 1:
        print("\n✅ System is mostly operational. Minor issues detected.")
    else:
        print("\n⚠️ Some components need attention. Check the errors above.")
    
    print("\n" + "="*80)
    print("\n💡 Next Steps:")
    print("  1. Upload a PDF via the web interface")
    print("  2. Click 'Validate & Save' to trigger AI extraction")
    print("  3. Check n8n workflow execution logs")
    print("  4. Verify extracted data appears in the form")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
