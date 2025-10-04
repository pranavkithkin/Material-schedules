"""
Unit Tests for Data Processing Agent
Sprint 1 - Test Coverage for Validation, Duplicates, and Matching
"""
import unittest
from datetime import datetime, timedelta
from services.data_processing_agent import DataProcessingAgent


class MockDBSession:
    """Mock database session for testing without actual DB"""
    
    def __init__(self):
        self.mock_lpos = []
        self.mock_invoices = []
        self.mock_submittals = []
        self.mock_deliveries = []
    
    def query(self, model):
        """Mock query method"""
        return MockQuery(self, model)


class MockQuery:
    """Mock query builder"""
    
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.filters = []
    
    def filter_by(self, **kwargs):
        self.filters.append(kwargs)
        return self
    
    def filter(self, *args):
        return self
    
    def first(self):
        return None
    
    def all(self):
        return []


class TestDataProcessingAgent(unittest.TestCase):
    """Test cases for Data Processing Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_session = MockDBSession()
        self.agent = DataProcessingAgent(self.db_session)
    
    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================
    
    def test_validate_lpo_valid_data(self):
        """Test LPO validation with valid data"""
        valid_lpo = {
            'lpo_number': 'LPO-2024-001',
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'contact_person': 'John Doe',
            'contact_phone': '+971501234567',
            'contact_email': 'john@abc.com'
        }
        
        result = self.agent.process_data(
            record_type='lpo_release',
            data=valid_lpo,
            check_duplicates=False
        )
        
        self.assertTrue(result['is_valid'], f"Expected valid, got errors: {result['errors']}")
        self.assertEqual(len(result['errors']), 0)
        self.assertTrue(result['ready_to_save'])
    
    def test_validate_lpo_missing_required_fields(self):
        """Test LPO validation with missing required fields"""
        invalid_lpo = {
            'lpo_number': 'LPO-2024-001',
            # Missing material_name, quantity, etc.
        }
        
        result = self.agent.process_data(
            record_type='lpo_release',
            data=invalid_lpo,
            check_duplicates=False
        )
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertFalse(result['ready_to_save'])
    
    def test_validate_lpo_invalid_formats(self):
        """Test LPO validation with invalid data formats"""
        invalid_lpo = {
            'lpo_number': 'LPO-2024-001',
            'material_name': 'Cement',
            'quantity': -10,  # Negative quantity
            'unit': 'bags',
            'unit_rate': -50.0,  # Negative rate
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'expected_delivery_date': '2020-01-01',  # Past date
            'contact_person': 'John Doe',
            'contact_phone': 'invalid',  # Invalid phone
            'contact_email': 'not-an-email'  # Invalid email
        }
        
        result = self.agent.process_data(
            record_type='lpo_release',
            data=invalid_lpo,
            check_duplicates=False
        )
        
        self.assertFalse(result['is_valid'])
        # Should have errors for: negative values, past date, invalid phone, invalid email
        self.assertGreaterEqual(len(result['errors']), 4)
    
    def test_validate_lpo_amount_mismatch(self):
        """Test LPO validation catches amount calculation errors"""
        lpo_with_mismatch = {
            'lpo_number': 'LPO-2024-001',
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 6000.0,  # Wrong! Should be 100 * 50 = 5000
            'supplier_name': 'ABC Suppliers',
            'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'contact_person': 'John Doe',
            'contact_phone': '+971501234567',
            'contact_email': 'john@abc.com'
        }
        
        result = self.agent.process_data(
            record_type='lpo_release',
            data=lpo_with_mismatch,
            check_duplicates=False
        )
        
        self.assertFalse(result['is_valid'])
        self.assertTrue(
            any('amount mismatch' in err.lower() or 'calculation' in err.lower() 
                for err in result['errors'])
        )
    
    def test_validate_invoice_valid_data(self):
        """Test invoice validation with valid data"""
        valid_invoice = {
            'invoice_number': 'INV-2024-001',
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'payment_terms': 'Net 30',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        result = self.agent.process_data(
            record_type='invoice',
            data=valid_invoice,
            check_duplicates=False
        )
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_submittal_valid_data(self):
        """Test submittal validation with valid data"""
        valid_submittal = {
            'submittal_number': 'SUB-2024-001',
            'material_name': 'Cement',
            'supplier_name': 'ABC Suppliers',
            'submission_date': datetime.now().strftime('%Y-%m-%d'),
            'documents': ['datasheet.pdf', 'certificate.pdf']
        }
        
        result = self.agent.process_data(
            record_type='submittal',
            data=valid_submittal,
            check_duplicates=False
        )
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_delivery_valid_data(self):
        """Test delivery validation with valid data"""
        valid_delivery = {
            'delivery_note_number': 'DN-2024-001',
            'material_name': 'Cement',
            'quantity_delivered': 100,
            'unit': 'bags',
            'delivery_date': datetime.now().strftime('%Y-%m-%d'),
            'received_by': 'John Doe'
        }
        
        result = self.agent.process_data(
            record_type='delivery',
            data=valid_delivery,
            check_duplicates=False
        )
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    # ========================================================================
    # DUPLICATE DETECTION TESTS
    # ========================================================================
    
    def test_duplicate_detection_exact_match(self):
        """Test duplicate detection with exact LPO number match"""
        # This would require actual database mocking
        # For now, test the similarity calculation method
        
        similarity = self.agent._calculate_similarity('LPO-2024-001', 'LPO-2024-001')
        self.assertEqual(similarity, 1.0)
    
    def test_duplicate_detection_fuzzy_match(self):
        """Test duplicate detection with fuzzy matching"""
        # Similar but not identical LPO numbers
        similarity1 = self.agent._calculate_similarity('LPO-2024-001', 'LPO-2024-0001')
        self.assertGreater(similarity1, 0.85)  # Should be flagged as potential duplicate
        
        similarity2 = self.agent._calculate_similarity('LPO-2024-001', 'LPO-2025-999')
        self.assertLess(similarity2, 0.85)  # Should NOT be flagged as duplicate
    
    def test_duplicate_detection_different_strings(self):
        """Test duplicate detection correctly identifies non-duplicates"""
        similarity = self.agent._calculate_similarity('ABC-123', 'XYZ-789')
        self.assertLess(similarity, 0.5)
    
    # ========================================================================
    # INVOICE-LPO MATCHING TESTS
    # ========================================================================
    
    def test_invoice_lpo_matching_disabled_by_default(self):
        """Test that invoice-LPO matching is disabled by default"""
        invoice_data = {
            'invoice_number': 'INV-2024-001',
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'payment_terms': 'Net 30',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        result = self.agent.process_data(
            record_type='invoice',
            data=invoice_data,
            check_duplicates=False,
            match_invoice_to_lpo=False
        )
        
        self.assertIsNone(result.get('matched_lpo_id'))
        self.assertIsNone(result.get('confidence_score'))
    
    # ========================================================================
    # HELPER METHOD TESTS
    # ========================================================================
    
    def test_is_valid_date(self):
        """Test date validation helper"""
        # Valid dates
        self.assertTrue(self.agent._is_valid_date('2024-01-01'))
        self.assertTrue(self.agent._is_valid_date('2024-12-31'))
        
        # Invalid dates
        self.assertFalse(self.agent._is_valid_date('2024-13-01'))  # Invalid month
        self.assertFalse(self.agent._is_valid_date('2024-01-32'))  # Invalid day
        self.assertFalse(self.agent._is_valid_date('not-a-date'))
        self.assertFalse(self.agent._is_valid_date(None))
    
    def test_is_valid_email(self):
        """Test email validation helper"""
        # Valid emails
        self.assertTrue(self.agent._is_valid_email('test@example.com'))
        self.assertTrue(self.agent._is_valid_email('user.name@domain.co.uk'))
        
        # Invalid emails
        self.assertFalse(self.agent._is_valid_email('not-an-email'))
        self.assertFalse(self.agent._is_valid_email('@example.com'))
        self.assertFalse(self.agent._is_valid_email('test@'))
        self.assertFalse(self.agent._is_valid_email(None))
    
    def test_is_valid_phone(self):
        """Test phone validation helper"""
        # Valid UAE phone numbers
        self.assertTrue(self.agent._is_valid_phone('+971501234567'))
        self.assertTrue(self.agent._is_valid_phone('0501234567'))
        self.assertTrue(self.agent._is_valid_phone('+971-50-123-4567'))
        
        # Invalid phones
        self.assertFalse(self.agent._is_valid_phone('123'))  # Too short
        self.assertFalse(self.agent._is_valid_phone('abcdefghij'))
        self.assertFalse(self.agent._is_valid_phone(None))
    
    def test_is_positive_number(self):
        """Test positive number validation"""
        self.assertTrue(self.agent._is_positive_number(100))
        self.assertTrue(self.agent._is_positive_number(0.5))
        
        self.assertFalse(self.agent._is_positive_number(-100))
        self.assertFalse(self.agent._is_positive_number(0))
        self.assertFalse(self.agent._is_positive_number(None))
        self.assertFalse(self.agent._is_positive_number('not-a-number'))
    
    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================
    
    def test_full_processing_pipeline_lpo(self):
        """Test full processing pipeline for LPO"""
        lpo_data = {
            'lpo_number': 'LPO-2024-001',
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'expected_delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'contact_person': 'John Doe',
            'contact_phone': '+971501234567',
            'contact_email': 'john@abc.com'
        }
        
        result = self.agent.process_data(
            record_type='lpo_release',
            data=lpo_data,
            check_duplicates=True  # Enable all checks
        )
        
        # Should have all expected keys
        self.assertIn('is_valid', result)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        self.assertIn('duplicates', result)
        self.assertIn('ready_to_save', result)
        
        # Should be valid
        self.assertTrue(result['is_valid'])
        self.assertTrue(result['ready_to_save'])
    
    def test_full_processing_pipeline_invoice(self):
        """Test full processing pipeline for invoice with matching"""
        invoice_data = {
            'invoice_number': 'INV-2024-001',
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'material_name': 'Cement',
            'quantity': 100,
            'unit': 'bags',
            'unit_rate': 50.0,
            'total_amount': 5000.0,
            'supplier_name': 'ABC Suppliers',
            'payment_terms': 'Net 30',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        result = self.agent.process_data(
            record_type='invoice',
            data=invoice_data,
            check_duplicates=True,
            match_invoice_to_lpo=True  # Enable LPO matching
        )
        
        # Should have all expected keys
        self.assertIn('is_valid', result)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        self.assertIn('duplicates', result)
        self.assertIn('matched_lpo_id', result)
        self.assertIn('ready_to_save', result)


class TestDataValidationHelpers(unittest.TestCase):
    """Test helper functions separately"""
    
    def setUp(self):
        self.db_session = MockDBSession()
        self.agent = DataProcessingAgent(self.db_session)
    
    def test_date_validation_comprehensive(self):
        """Comprehensive date validation tests"""
        valid_dates = [
            '2024-01-01',
            '2024-06-15',
            '2024-12-31',
            '2025-02-28',
            '2024-02-29'  # Leap year
        ]
        
        for date in valid_dates:
            with self.subTest(date=date):
                self.assertTrue(self.agent._is_valid_date(date))
        
        invalid_dates = [
            '2024-00-01',  # Invalid month
            '2024-13-01',  # Invalid month
            '2024-01-00',  # Invalid day
            '2024-01-32',  # Invalid day
            '2023-02-29',  # Not a leap year
            'invalid',
            '01/01/2024',  # Wrong format
            ''
        ]
        
        for date in invalid_dates:
            with self.subTest(date=date):
                self.assertFalse(self.agent._is_valid_date(date))
    
    def test_email_validation_comprehensive(self):
        """Comprehensive email validation tests"""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user_name@example.co.uk',
            'test123@test-domain.com'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(self.agent._is_valid_email(email))
        
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'test@',
            'test..test@example.com',
            'test @example.com',  # Space
            '',
            None
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(self.agent._is_valid_email(email))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
