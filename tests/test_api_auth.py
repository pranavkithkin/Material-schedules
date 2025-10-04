"""
API Authentication Testing Script
Tests all n8n webhook endpoints with and without authentication
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "your-api-key-here"  # Replace with your actual API key from .env

# Test data
TEST_AI_SUGGESTION = {
    "material_id": 1,
    "source": "email",
    "suggestion_type": "purchase_order",
    "extracted_data": {
        "po_number": "PO-TEST-001",
        "supplier": "Test Supplier Co.",
        "amount": 25000.00,
        "currency": "AED"
    },
    "confidence_score": 85.5,
    "ai_reasoning": "Test extraction from email attachment",
    "metadata": {
        "email_from": "test@example.com",
        "email_subject": "Test PO",
        "file_name": "test_po.pdf"
    }
}

TEST_CONVERSATION = {
    "conversation_id": "conv-test-123",
    "user_message": "When is the cement delivery?",
    "ai_response": "Testing conversation storage",
    "context": {
        "material_id": 1,
        "query_type": "delivery_status"
    }
}

TEST_CLARIFICATION = {
    "suggestion_id": 1,
    "clarifications": {
        "supplier_email": "test@supplier.com",
        "delivery_date": "2025-10-15"
    },
    "ready_to_create": True
}


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(endpoint, status_code, response_data):
    """Print test result"""
    status_symbol = "✅" if 200 <= status_code < 300 else "❌"
    print(f"\n{status_symbol} {endpoint}")
    print(f"   Status: {status_code}")
    print(f"   Response: {json.dumps(response_data, indent=2)}")


def test_without_auth(endpoint, method='GET', data=None):
    """Test endpoint without authentication (should fail)"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


def test_with_auth(endpoint, method='GET', data=None):
    """Test endpoint with authentication (should succeed)"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, json=data, headers=headers)
        
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


def main():
    print_header("API AUTHENTICATION TEST SUITE")
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}..." if len(API_KEY) > 20 else f"API Key: {API_KEY}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health Check (No auth required)
    print_header("Test 1: Health Check (No Auth Required)")
    status, data = test_without_auth("/api/n8n/health")
    print_result("GET /api/n8n/health", status, data)
    
    # Test 2: Protected endpoints without auth (should fail with 401)
    print_header("Test 2: Protected Endpoints WITHOUT Authentication (Should Fail)")
    
    endpoints = [
        ("/api/n8n/ai-suggestion", "POST", TEST_AI_SUGGESTION),
        ("/api/n8n/conversation", "POST", TEST_CONVERSATION),
        ("/api/n8n/clarification", "POST", TEST_CLARIFICATION),
        ("/api/n8n/pending-reviews", "GET", None),
        ("/api/n8n/stats", "GET", None),
    ]
    
    for endpoint, method, data in endpoints:
        status, response = test_without_auth(endpoint, method, data)
        print_result(f"{method} {endpoint}", status, response)
        if status != 401:
            print("   ⚠️  WARNING: Expected 401 Unauthorized!")
    
    # Test 3: Protected endpoints with valid auth (should succeed)
    print_header("Test 3: Protected Endpoints WITH Authentication (Should Succeed)")
    
    for endpoint, method, data in endpoints:
        status, response = test_with_auth(endpoint, method, data)
        print_result(f"{method} {endpoint}", status, response)
        if not (200 <= status < 300):
            print("   ⚠️  WARNING: Expected 2xx Success!")
    
    # Test 4: Invalid API Key (should fail with 403)
    print_header("Test 4: Invalid API Key (Should Fail with 403)")
    
    url = f"{BASE_URL}/api/n8n/stats"
    headers = {"X-API-Key": "invalid-key-12345"}
    
    try:
        response = requests.get(url, headers=headers)
        status = response.status_code
        data = response.json()
    except Exception as e:
        status = None
        data = {"error": str(e)}
    
    print_result("GET /api/n8n/stats", status, data)
    if status != 403:
        print("   ⚠️  WARNING: Expected 403 Forbidden!")
    
    # Summary
    print_header("TEST SUMMARY")
    print("\n✅ Authentication system is working if:")
    print("   1. Health check works without auth (200)")
    print("   2. Protected endpoints fail without auth (401)")
    print("   3. Protected endpoints succeed with valid auth (200-201)")
    print("   4. Protected endpoints fail with invalid auth (403)")
    print("\n📝 Next Steps:")
    print("   1. Update API_KEY in this script with your .env value")
    print("   2. Ensure Flask is running: python app.py")
    print("   3. Run this test script: python test_api_auth.py")
    print()


if __name__ == "__main__":
    print("\n" + "🔐 API AUTHENTICATION TESTING" + "\n")
    
    # Check if API key is set
    if API_KEY == "your-api-key-here":
        print("⚠️  WARNING: API_KEY not set!")
        print("\nPlease update the API_KEY variable in this script.")
        print("Get your API key from:")
        print("  1. Run: python generate_api_key.py")
        print("  2. Copy the generated key to .env file")
        print("  3. Update API_KEY in this script")
        print()
        exit(1)
    
    main()
