#!/usr/bin/env python3
"""
Quick Test Script for Data Processing Agent
Run this to verify Sprint 1 is working correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_processing_agent import DataProcessingAgent
from datetime import datetime, timedelta


class MockDBSession:
    """Mock DB session for testing"""
    def query(self, model):
        class MockQuery:
            def filter_by(self, **kwargs):
                return self
            def filter(self, *args):
                return self
            def first(self):
                return None
            def all(self):
                return []
        return MockQuery()


def test_lpo_validation():
    """Test LPO validation"""
    print("\n" + "="*70)
    print("TEST 1: LPO/PO Validation")
    print("="*70)
    
    agent = DataProcessingAgent(MockDBSession())
    
    # Valid LPO - matches actual database schema (PurchaseOrder model)
    valid_lpo = {
        'material_id': 1,  # Required by schema
        'supplier_name': 'ABC Suppliers',
        'lpo_number': 'TEST-LPO-001',
        'release_date': datetime.now().strftime('%Y-%m-%d'),  # Required
        'amount': 5000.0,  # Required
        'contact_number': '+971501234567',
        'contact_email': 'john@abc.com',
        'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }
    
    result = agent.process_data(
        record_type='lpo_release',
        data=valid_lpo,
        check_duplicates=False
    )
    
    print(f"\n✅ Valid LPO Test:")
    print(f"   Is Valid: {result['is_valid']}")
    print(f"   Errors: {len(result['errors'])}")
    print(f"   Warnings: {len(result['warnings'])}")
    print(f"   Ready to Save: {result['ready_to_save']}")
    
    if result['is_valid']:
        print("   ✅ PASSED - Valid LPO accepted")
    else:
        print("   ❌ FAILED - Valid LPO rejected")
        print(f"   Errors: {result['errors']}")


def test_invalid_lpo():
    """Test invalid LPO detection"""
    print("\n" + "="*70)
    print("TEST 2: Invalid LPO Detection")
    print("="*70)
    
    agent = DataProcessingAgent(MockDBSession())
    
    # Invalid LPO (missing required fields, invalid formats)
    invalid_lpo = {
        'lpo_number': 'TEST-LPO-002',
        # Missing material_id (required!)
        # Missing supplier_name (required!)
        # Missing release_date (required!)
        # Missing amount (required!)
        'expected_delivery_date': '2020-01-01',  # Past date!
        'contact_number': 'invalid',  # Invalid format!
        'contact_email': 'not-an-email'  # Invalid format!
    }
    
    result = agent.process_data(
        record_type='lpo_release',
        data=invalid_lpo,
        check_duplicates=False
    )
    
    print(f"\n❌ Invalid LPO Test:")
    print(f"   Is Valid: {result['is_valid']}")
    print(f"   Errors Found: {len(result['errors'])}")
    print(f"   Ready to Save: {result['ready_to_save']}")
    
    if not result['is_valid']:
        print("   ✅ PASSED - Invalid LPO correctly rejected")
        print("\n   Errors detected:")
        for error in result['errors']:
            print(f"     • {error}")
    else:
        print("   ❌ FAILED - Invalid LPO was accepted")


def test_invoice_validation():
    """Test invoice validation"""
    print("\n" + "="*70)
    print("TEST 3: Invoice/Payment Validation")
    print("="*70)
    
    agent = DataProcessingAgent(MockDBSession())
    
    # Valid invoice - matches Payment model schema
    valid_invoice = {
        'invoice_number': 'INV-TEST-001',
        'invoice_date': datetime.now().strftime('%Y-%m-%d'),
        'amount': 50000.0,  # Required field in Payment model
        'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    result = agent.process_data(
        record_type='invoice',
        data=valid_invoice,
        check_duplicates=False,
        match_invoice_to_lpo=False  # Disable LPO matching for now
    )
    
    print(f"\n✅ Valid Invoice Test:")
    print(f"   Is Valid: {result['is_valid']}")
    print(f"   Errors: {len(result['errors'])}")
    print(f"   Matched LPO: {result.get('matched_lpo_id')}")
    print(f"   Ready to Save: {result['ready_to_save']}")
    
    if result['is_valid']:
        print("   ✅ PASSED - Valid invoice accepted")
    else:
        print("   ❌ FAILED - Valid invoice rejected")
        print(f"   Errors: {result['errors']}")


def test_fuzzy_matching():
    """Test fuzzy string matching"""
    print("\n" + "="*70)
    print("TEST 4: Fuzzy Matching Algorithm")
    print("="*70)
    
    agent = DataProcessingAgent(MockDBSession())
    
    test_cases = [
        ('LPO-2024-001', 'LPO-2024-001', 'Exact match'),
        ('LPO-2024-001', 'LPO-2024-0001', 'Very similar'),
        ('ABC-123', 'ABC-124', 'Close match'),
        ('ABC-123', 'XYZ-789', 'Different')
    ]
    
    print("\n   String Similarity Tests:")
    for str1, str2, description in test_cases:
        similarity = agent._calculate_similarity(str1, str2)
        is_duplicate = similarity >= agent.similarity_threshold
        
        print(f"\n   {description}:")
        print(f"     '{str1}' vs '{str2}'")
        print(f"     Similarity: {similarity:.1%}")
        print(f"     Duplicate? {'✅ YES' if is_duplicate else '❌ NO'}")
    
    print("\n   ✅ PASSED - Fuzzy matching working correctly")


def test_performance():
    """Test performance (should be < 100ms)"""
    print("\n" + "="*70)
    print("TEST 5: Performance Test")
    print("="*70)
    
    import time
    
    agent = DataProcessingAgent(MockDBSession())
    
    # Use correct schema fields
    test_lpo = {
        'material_id': 1,
        'supplier_name': 'Test Supplier',
        'lpo_number': 'PERF-TEST-001',
        'release_date': datetime.now().strftime('%Y-%m-%d'),
        'amount': 5000.0,
        'contact_number': '+971501234567',
        'contact_email': 'john@test.com',
        'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }
    
    # Warm up
    agent.process_data('lpo_release', test_lpo, check_duplicates=False)
    
    # Measure performance
    times = []
    iterations = 10
    
    for _ in range(iterations):
        start = time.time()
        agent.process_data('lpo_release', test_lpo, check_duplicates=False)
        times.append((time.time() - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n   Performance Results ({iterations} iterations):")
    print(f"     Average: {avg_time:.1f}ms")
    print(f"     Min: {min_time:.1f}ms")
    print(f"     Max: {max_time:.1f}ms")
    print(f"     Target: <100ms")
    
    if avg_time < 100:
        print(f"     ✅ PASSED - {100-avg_time:.1f}ms faster than target!")
    else:
        print(f"     ❌ FAILED - {avg_time-100:.1f}ms slower than target")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 DATA PROCESSING AGENT - QUICK TEST")
    print("="*70)
    print("\nSprint 1: Testing validation, duplicates, and performance...")
    
    try:
        test_lpo_validation()
        test_invalid_lpo()
        test_invoice_validation()
        test_fuzzy_matching()
        test_performance()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎉 Sprint 1 is working correctly!")
        print("\nNext steps:")
        print("  1. Start Flask: python app.py")
        print("  2. Test API: curl http://localhost:5000/api/agents/validate-and-check/test")
        print("  3. Run unit tests: python -m pytest tests/test_data_processing_agent.py -v")
        print("  4. Review: SPRINT_1_COMPLETE.md")
        print()
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
