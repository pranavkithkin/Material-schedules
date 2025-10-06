"""
Test validation agent with current model attributes
"""
import pytest
from app import create_app
from models import db
from services.data_processing_agent import DataProcessingAgent


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestValidationAgentMaterials:
    """Test validation agent for Materials (submittal)"""
    
    def test_valid_material_data(self, app):
        """Test validation passes with valid material data"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            data = {
                'material_type': 'PVC Conduits & Accessories',
                'description': '20mm PVC conduit pipes',
                'approval_status': 'Pending',
                'submittal_ref': 'SUB-PVC-001',
                'specification_ref': 'SPEC-001',
                'revision_number': 0
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            
            assert result['is_valid'] == True
            assert len(result['errors']) == 0
            print("✅ Valid material data validation passed")
    
    def test_missing_material_type(self, app):
        """Test validation fails when material_type is missing"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            data = {
                'description': '20mm PVC conduit pipes',
                'approval_status': 'Pending'
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            
            assert result['is_valid'] == False
            assert len(result['errors']) > 0
            assert any('material type' in err.lower() for err in result['errors'])
            print("✅ Missing material_type validation passed")
    
    def test_missing_approval_status(self, app):
        """Test validation fails when approval_status is missing"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            data = {
                'material_type': 'PVC Conduits & Accessories',
                'description': '20mm PVC conduit pipes'
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            
            assert result['is_valid'] == False
            assert len(result['errors']) > 0
            assert any('approval status' in err.lower() for err in result['errors'])
            print("✅ Missing approval_status validation passed")
    
    def test_invalid_approval_status(self, app):
        """Test validation fails with invalid approval status"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            data = {
                'material_type': 'PVC Conduits & Accessories',
                'description': '20mm PVC conduit pipes',
                'approval_status': 'InvalidStatus'
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            
            assert result['is_valid'] == False
            assert len(result['errors']) > 0
            print("✅ Invalid approval_status validation passed")
    
    def test_valid_approval_statuses(self, app):
        """Test all valid approval statuses"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            valid_statuses = [
                'Pending',
                'Under Review', 
                'Approved',
                'Approved as Noted',
                'Revise & Resubmit'
            ]
            
            for status in valid_statuses:
                data = {
                    'material_type': 'PVC Conduits & Accessories',
                    'approval_status': status
                }
                
                result = agent.process_data('submittal', data, check_duplicates=False)
                assert result['is_valid'] == True, f"Status '{status}' should be valid"
            
            print(f"✅ All {len(valid_statuses)} valid approval statuses passed")
    
    def test_revision_validation(self, app):
        """Test revision number validation"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            # Valid revision
            data = {
                'material_type': 'PVC Conduits & Accessories',
                'approval_status': 'Pending',
                'revision_number': 1,
                'previous_submittal_id': 123
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            assert result['is_valid'] == True
            
            # Revision without previous submittal (warning but valid)
            data['previous_submittal_id'] = None
            result = agent.process_data('submittal', data, check_duplicates=False)
            assert result['is_valid'] == True
            assert len(result['warnings']) > 0
            
            # Negative revision number (error)
            data['revision_number'] = -1
            result = agent.process_data('submittal', data, check_duplicates=False)
            assert result['is_valid'] == False
            
            print("✅ Revision number validation passed")
    
    def test_approval_date_validation(self, app):
        """Test approval date validation"""
        with app.app_context():
            agent = DataProcessingAgent(None)
            
            # Valid date
            data = {
                'material_type': 'PVC Conduits & Accessories',
                'approval_status': 'Approved',
                'approval_date': '2025-08-08'
            }
            
            result = agent.process_data('submittal', data, check_duplicates=False)
            assert result['is_valid'] == True
            print("✅ Approval date validation passed")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
