"""
Test script for Phase 5A Core LPO System
Tests manual LPO creation with different column structures
"""
import requests
import json
from datetime import date

# Base URL
BASE_URL = 'http://localhost:5001'

def test_generate_lpo_number():
    """Test LPO number generation"""
    print("\n1. Testing LPO Number Generation...")
    response = requests.get(f'{BASE_URL}/api/lpo/generate-number')
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Generated LPO Number: {data['lpo_number']}")
        return True
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

def test_create_lpo_steel_supplier():
    """Test creating LPO for steel supplier (full columns)"""
    print("\n2. Testing LPO Creation - Steel Supplier (MAKE, CODE, DESCRIPTION)...")
    
    lpo_data = {
        "project_name": "Al Barsha Villa Project",
        "project_location": "Al Barsha, Dubai",
        "consultant": "ABC Engineering Consultants",
        "supplier_name": "Steel Trading LLC",
        "supplier_address": "Industrial Area 1, Sharjah",
        "supplier_trn": "100123456700003",
        "supplier_tel": "+971 6 1234567",
        "supplier_fax": "+971 6 1234568",
        "contact_person": "Ahmed Ali",
        "contact_number": "+971 50 1234567",
        "quotation_ref": "ST/Q/2025/001",
        "quotation_date": "2025-10-05",
        "column_structure": ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
        "items": [
            {
                "make": "Tata Steel",
                "code": "TMT16",
                "description": "TMT Bar 16mm Grade 60",
                "unit": "Ton",
                "quantity": 5,
                "rate": 2850.00
            },
            {
                "make": "Tata Steel",
                "code": "TMT12",
                "description": "TMT Bar 12mm Grade 60",
                "unit": "Ton",
                "quantity": 3,
                "rate": 2900.00
            },
            {
                "make": "Emirates Steel",
                "code": "MESH150",
                "description": "Wire Mesh 150mm x 150mm",
                "unit": "Roll",
                "quantity": 10,
                "rate": 125.00
            }
        ],
        "payment_terms": "30 days from delivery",
        "delivery_terms": "Deliver to site within 7 working days",
        "warranty_terms": "As per manufacturer warranty",
        "notes": "All materials must have test certificates"
    }
    
    response = requests.post(
        f'{BASE_URL}/api/lpo/create',
        json=lpo_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        data = response.json()
        lpo_id = data['lpo']['id']
        lpo_number = data['lpo']['lpo_number']
        print(f"   ✓ LPO Created: {lpo_number} (ID: {lpo_id})")
        print(f"   ✓ Items: {data['lpo']['item_count']}")
        print(f"   ✓ Subtotal: AED {data['lpo']['subtotal']:.2f}")
        print(f"   ✓ VAT (5%): AED {data['lpo']['vat_amount']:.2f}")
        print(f"   ✓ Grand Total: AED {data['lpo']['grand_total']:.2f}")
        return lpo_id
    else:
        print(f"   ✗ Failed: {response.text}")
        return None

def test_create_lpo_electrical_supplier():
    """Test creating LPO for electrical supplier (no MAKE column)"""
    print("\n3. Testing LPO Creation - Electrical Supplier (CODE, DESCRIPTION only)...")
    
    lpo_data = {
        "project_name": "Marina Heights Tower",
        "project_location": "Dubai Marina",
        "supplier_name": "Electrical Supplies Co",
        "supplier_address": "Deira, Dubai",
        "supplier_trn": "100987654300001",
        "supplier_tel": "+971 4 2345678",
        "contact_person": "Mohammed Hassan",
        "contact_number": "+971 50 9876543",
        "quotation_ref": "ESC/2025/045",
        "quotation_date": "2025-10-06",
        "column_structure": ["CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
        "items": [
            {
                "code": "CAB-2.5",
                "description": "2.5mm² Cable 100m Roll",
                "unit": "Roll",
                "quantity": 15,
                "rate": 85.00
            },
            {
                "code": "CAB-4.0",
                "description": "4.0mm² Cable 100m Roll",
                "unit": "Roll",
                "quantity": 8,
                "rate": 120.00
            },
            {
                "code": "MCB-16A",
                "description": "MCB 16A Single Pole",
                "unit": "Nos",
                "quantity": 50,
                "rate": 12.50
            }
        ],
        "payment_terms": "Cash on delivery",
        "delivery_terms": "Immediate delivery"
    }
    
    response = requests.post(
        f'{BASE_URL}/api/lpo/create',
        json=lpo_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        data = response.json()
        lpo_id = data['lpo']['id']
        lpo_number = data['lpo']['lpo_number']
        print(f"   ✓ LPO Created: {lpo_number} (ID: {lpo_id})")
        print(f"   ✓ Column Structure: {data['lpo']['column_structure']}")
        print(f"   ✓ Grand Total: AED {data['lpo']['grand_total']:.2f}")
        return lpo_id
    else:
        print(f"   ✗ Failed: {response.text}")
        return None

def test_create_lpo_service_provider():
    """Test creating LPO for service provider (minimal columns)"""
    print("\n4. Testing LPO Creation - Service Provider (DESCRIPTION only)...")
    
    lpo_data = {
        "project_name": "JBR Beach Residence",
        "supplier_name": "Professional Labor Services",
        "supplier_address": "Jebel Ali, Dubai",
        "supplier_trn": "100555666700002",
        "quotation_ref": "PLS/LAB/2025/12",
        "column_structure": ["DESCRIPTION", "UNIT", "QTY", "RATE"],
        "items": [
            {
                "description": "Skilled Electrician - 8 hours/day",
                "unit": "Day",
                "quantity": 10,
                "rate": 450.00
            },
            {
                "description": "Helper - 8 hours/day",
                "unit": "Day",
                "quantity": 10,
                "rate": 250.00
            }
        ],
        "payment_terms": "Weekly payment",
        "delivery_terms": "Workers to report at site 7 AM"
    }
    
    response = requests.post(
        f'{BASE_URL}/api/lpo/create',
        json=lpo_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        data = response.json()
        lpo_id = data['lpo']['id']
        lpo_number = data['lpo']['lpo_number']
        print(f"   ✓ LPO Created: {lpo_number} (ID: {lpo_id})")
        print(f"   ✓ Column Structure: {data['lpo']['column_structure']}")
        print(f"   ✓ Grand Total: AED {data['lpo']['grand_total']:.2f}")
        return lpo_id
    else:
        print(f"   ✗ Failed: {response.text}")
        return None

def test_get_lpo(lpo_id):
    """Test retrieving LPO by ID"""
    print(f"\n5. Testing LPO Retrieval (ID: {lpo_id})...")
    
    response = requests.get(f'{BASE_URL}/api/lpo/{lpo_id}')
    
    if response.status_code == 200:
        data = response.json()
        lpo = data['lpo']
        print(f"   ✓ Retrieved LPO: {lpo['lpo_number']}")
        print(f"   ✓ Supplier: {lpo['supplier_name']}")
        print(f"   ✓ Status: {lpo['status']}")
        return True
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

def test_list_lpos():
    """Test listing all LPOs"""
    print("\n6. Testing LPO List...")
    
    response = requests.get(f'{BASE_URL}/api/lpo/list')
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Total LPOs: {data['pagination']['total']}")
        print(f"   ✓ LPOs on page 1:")
        for lpo in data['lpos']:
            print(f"      - {lpo['lpo_number']}: {lpo['supplier_name']} (AED {lpo['grand_total']:.2f})")
        return True
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

def test_change_status(lpo_id):
    """Test changing LPO status"""
    print(f"\n7. Testing Status Change (ID: {lpo_id})...")
    
    response = requests.patch(
        f'{BASE_URL}/api/lpo/{lpo_id}/status',
        json={"status": "issued", "notes": "LPO issued to supplier via email"},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Status changed to: {data['lpo']['status']}")
        return True
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

def test_pdf_generation(lpo_id):
    """Test PDF generation"""
    print(f"\n8. Testing PDF Generation (ID: {lpo_id})...")
    
    response = requests.get(f'{BASE_URL}/api/lpo/{lpo_id}/pdf')
    
    if response.status_code == 200:
        # Save PDF
        filename = f'test_lpo_{lpo_id}.pdf'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✓ PDF generated and saved: {filename}")
        print(f"   ✓ File size: {len(response.content)} bytes")
        return True
    else:
        print(f"   ✗ Failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 5A: CORE LPO SYSTEM TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Generate LPO number
    results.append(test_generate_lpo_number())
    
    # Test 2: Create LPO - Steel supplier
    steel_lpo_id = test_create_lpo_steel_supplier()
    results.append(steel_lpo_id is not None)
    
    # Test 3: Create LPO - Electrical supplier
    electrical_lpo_id = test_create_lpo_electrical_supplier()
    results.append(electrical_lpo_id is not None)
    
    # Test 4: Create LPO - Service provider
    service_lpo_id = test_create_lpo_service_provider()
    results.append(service_lpo_id is not None)
    
    # Test 5: Get LPO by ID
    if steel_lpo_id:
        results.append(test_get_lpo(steel_lpo_id))
    
    # Test 6: List all LPOs
    results.append(test_list_lpos())
    
    # Test 7: Change status
    if steel_lpo_id:
        results.append(test_change_status(steel_lpo_id))
    
    # Test 8: Generate PDF
    if steel_lpo_id:
        results.append(test_pdf_generation(steel_lpo_id))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED! Phase 5A Core System is working!")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")

if __name__ == '__main__':
    main()
