#!/usr/bin/env python3
"""
System Testing Script - Material Delivery Dashboard
Tests all features and endpoints to verify system is working
"""

import sys
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from datetime import datetime

BASE_URL = "http://localhost:5001"
API_KEY = "j5mpyk725_PTd7lZ0v99CQSRuk4qsfj1PGbOJ18ziJY"  # From your API_SECURITY_GUIDE.md

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def test_endpoint(name, url, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    try:
        full_url = f"{BASE_URL}{url}"
        
        if headers is None:
            headers = {}
        
        if method == "POST" and data:
            headers['Content-Type'] = 'application/json'
            req = Request(full_url, 
                         data=json.dumps(data).encode('utf-8'),
                         headers=headers,
                         method=method)
        else:
            req = Request(full_url, headers=headers, method=method)
        
        response = urlopen(req, timeout=5)
        status_code = response.getcode()
        
        if status_code == 200:
            print_success(f"{name}: Status {status_code}")
            try:
                result = json.loads(response.read().decode('utf-8'))
                return True, result
            except:
                return True, None
        else:
            print_warning(f"{name}: Status {status_code}")
            return False, None
            
    except HTTPError as e:
        print_error(f"{name}: HTTP Error {e.code}")
        return False, None
    except URLError as e:
        print_error(f"{name}: Connection Error - {e.reason}")
        return False, None
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False, None

def main():
    print_header("MATERIAL DELIVERY DASHBOARD - SYSTEM TEST")
    print_info(f"Testing Flask app at: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Basic Connectivity
    print_header("TEST 1: Basic Connectivity")
    success, _ = test_endpoint("Dashboard Home", "/")
    results['total'] += 1
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print_error("Flask app is not running or not accessible!")
        print_info("Make sure Flask is running: python app.py")
        sys.exit(1)
    
    # Test 2: Web Pages
    print_header("TEST 2: Web Pages")
    pages = [
        ("Materials Page", "/materials"),
        ("Purchase Orders Page", "/purchase_orders"),
        ("Payments Page", "/payments"),
        ("Deliveries Page", "/deliveries"),
        ("AI Suggestions Page", "/ai_suggestions"),
    ]
    
    for name, url in pages:
        success, _ = test_endpoint(name, url)
        results['total'] += 1
        if success:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 3: API Endpoints (Read)
    print_header("TEST 3: API Endpoints - Read Operations")
    api_endpoints = [
        ("Materials API", "/api/materials"),
        ("Purchase Orders API", "/api/purchase_orders"),
        ("Payments API", "/api/payments"),
        ("Deliveries API", "/api/deliveries"),
        ("AI Suggestions API", "/api/ai_suggestions"),
        ("Dashboard Stats API", "/api/dashboard/stats"),
        ("Dashboard Analytics API", "/api/dashboard/analytics"),
    ]
    
    for name, url in api_endpoints:
        success, data = test_endpoint(name, url)
        results['total'] += 1
        if success:
            results['passed'] += 1
            if data:
                if isinstance(data, list):
                    print_info(f"  → Returned {len(data)} items")
                elif isinstance(data, dict):
                    print_info(f"  → Returned {len(data)} fields")
        else:
            results['failed'] += 1
    
    # Test 4: n8n Webhook Endpoints
    print_header("TEST 4: n8n Webhook Endpoints (with API Key)")
    n8n_headers = {"X-API-Key": API_KEY}
    
    n8n_endpoints = [
        ("n8n Health Check", "/api/n8n/health", "GET", None),
        ("n8n Stats", "/api/n8n/stats", "GET", None),
        ("n8n Pending Reviews", "/api/n8n/pending-reviews", "GET", None),
    ]
    
    for name, url, method, data in n8n_endpoints:
        success, response = test_endpoint(name, url, method, data, n8n_headers)
        results['total'] += 1
        if success:
            results['passed'] += 1
            if response:
                print_info(f"  → Response: {json.dumps(response, indent=2)[:100]}...")
        else:
            results['failed'] += 1
    
    # Test 5: Agent Endpoints
    print_header("TEST 5: Agent Endpoints")
    agent_endpoints = [
        ("Agent Status", "/api/agents/status"),
    ]
    
    for name, url in agent_endpoints:
        success, data = test_endpoint(name, url)
        results['total'] += 1
        if success:
            results['passed'] += 1
            if data:
                print_info(f"  → {json.dumps(data, indent=2)[:150]}...")
        else:
            results['failed'] += 1
    
    # Test 6: Database Check
    print_header("TEST 6: Database Verification")
    success, stats = test_endpoint("Database Stats", "/api/dashboard/stats")
    results['total'] += 1
    
    if success and stats:
        results['passed'] += 1
        print_success("Database is accessible!")
        print_info(f"  → Materials: {stats.get('materials_count', 0)}")
        print_info(f"  → Purchase Orders: {stats.get('purchase_orders_count', 0)}")
        print_info(f"  → Payments: {stats.get('payments_count', 0)}")
        print_info(f"  → Deliveries: {stats.get('deliveries_count', 0)}")
        print_info(f"  → AI Suggestions: {stats.get('ai_suggestions_count', 0)}")
        
        if stats.get('materials_count', 0) == 0:
            print_warning("Database appears empty! Consider running:")
            print_info("  python init_db.py --with-samples")
    else:
        results['failed'] += 1
        print_error("Could not retrieve database stats")
    
    # Final Summary
    print_header("TEST SUMMARY")
    print(f"\n{Colors.BOLD}Total Tests: {results['total']}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! System is fully operational!{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed. Check failed items above.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Multiple issues detected. Please review errors above.{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return success_rate == 100

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user.{Colors.END}\n")
        sys.exit(1)
