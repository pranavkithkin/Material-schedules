#!/usr/bin/env python3
"""
Simple test script to trigger n8n document extraction workflow
Tests with the uploaded SAB_6001_49-2025_DB.pdf file
"""

import requests
import json

# Configuration
N8N_WEBHOOK_URL = "https://n8n1.trart.uk/webhook-test/extract-delivery"
FILE_ID = 1  # The uploaded DB PDF file
DELIVERY_ID = 1  # Test delivery ID (can be any number for now)
PO_REF = "SAB_6001_49-2025"  # From the filename

def test_n8n_extraction():
    """
    Trigger n8n workflow to extract data from the uploaded DB PDF
    """
    
    payload = {
        "delivery_id": DELIVERY_ID,
        "file_id": FILE_ID,
        "file_path": "2025/10/20251005_025738_SAB_6001_49-2025_DB.pdf",
        "po_ref": PO_REF
    }
    
    print("=" * 60)
    print("Testing n8n Document Extraction Workflow")
    print("=" * 60)
    print(f"\n📄 File: SAB_6001_49-2025_DB.pdf")
    print(f"🆔 File ID: {FILE_ID}")
    print(f"📦 PO Reference: {PO_REF}")
    print(f"🔗 Webhook URL: {N8N_WEBHOOK_URL}")
    print(f"\n📤 Sending request to n8n...")
    
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📨 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Workflow triggered successfully!")
            print("\n📋 Next Steps:")
            print("1. Check your n8n dashboard for execution details")
            print("2. Go to: https://n8n1.trart.uk/workflows")
            print("3. Look for the 'Document Intelligence' workflow execution")
            print("4. Verify that Flask received the API call")
            
        else:
            print(f"\n⚠️  Warning: Received status code {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (this is normal for async workflows)")
        print("Check n8n dashboard for execution status")
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Check if n8n is running and accessible")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_n8n_extraction()
