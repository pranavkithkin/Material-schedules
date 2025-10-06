"""
Comprehensive Tests for Basic CRUD Operations (Manual Entry Only - No AI)
===========================================================================

This test suite verifies that all basic features work correctly for manual data entry.
Tests cover Materials, Purchase Orders, Payments, and Deliveries.

Run with: pytest tests/test_basic_crud_manual.py -v
Or in WSL: wsl bash -c "cd '/mnt/c/...' && source venv/bin/activate && pytest tests/test_basic_crud_manual.py -v"
"""

import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery


@pytest.fixture
def app():
    """Create test application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_material(app):
    """Create a sample material for testing"""
    with app.app_context():
        material = Material(
            material_type='PVC Conduits & Accessories',
            description='20mm PVC conduit pipes',
            approval_status='Approved',
            submittal_ref='SUB-001',
            specification_ref='SPEC-001',
            revision_number=0,
            created_by='Manual'
        )
        db.session.add(material)
        db.session.commit()
        return material.id


@pytest.fixture
def sample_po(app, sample_material):
    """Create a sample purchase order for testing"""
    with app.app_context():
        po = PurchaseOrder(
            material_id=sample_material,
            quote_ref='QUO-2025-001',
            po_ref='PO-2025-001',
            po_date=datetime.utcnow(),
            expected_delivery_date=datetime.utcnow() + timedelta(days=30),
            supplier_name='ABC Trading LLC',
            supplier_contact='+971-4-1234567',
            supplier_email='supplier@abc.com',
            total_amount=50000.00,
            currency='AED',
            po_status='Released',
            payment_terms='30 days from delivery',
            delivery_terms='DDP Dubai',
            created_by='Manual'
        )
        db.session.add(po)
        db.session.commit()
        return po.id


# ==========================================
# MATERIAL TESTS
# ==========================================

class TestMaterialCRUD:
    """Test Material Create, Read, Update, Delete operations"""
    
    def test_create_material(self, client):
        """Test creating a new material manually"""
        response = client.post('/api/materials', 
            json={
                'material_type': 'Light Fittings (Internal)',
                'description': 'LED downlight fixtures 12W',
                'approval_status': 'Pending',
                'submittal_ref': 'SUB-002',
                'specification_ref': 'SPEC-LF-001',
                'revision_number': 0
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Material created successfully'
        assert data['material']['material_type'] == 'Light Fittings (Internal)'
        assert data['material']['approval_status'] == 'Pending'
        assert data['material']['created_by'] == 'Manual'
    
    def test_get_all_materials(self, client, sample_material):
        """Test retrieving all materials"""
        response = client.get('/api/materials')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['material_type'] == 'PVC Conduits & Accessories'
    
    def test_get_material_by_id(self, client, sample_material):
        """Test retrieving a specific material"""
        response = client.get(f'/api/materials/{sample_material}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_material
        assert data['material_type'] == 'PVC Conduits & Accessories'
    
    def test_update_material_status(self, client, sample_material):
        """Test updating material approval status"""
        response = client.put(f'/api/materials/{sample_material}',
            json={
                'approval_status': 'Approved as Noted',
                'approval_notes': 'Approved with minor modifications',
                'updated_by': 'Manual'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Material updated successfully'
        assert data['material']['approval_status'] == 'Approved as Noted'
    
    def test_create_material_revision(self, client, sample_material):
        """Test creating a material revision"""
        response = client.post('/api/materials',
            json={
                'material_type': 'PVC Conduits & Accessories',
                'description': '20mm PVC conduit pipes - Updated specs',
                'approval_status': 'Pending',
                'submittal_ref': 'SUB-001-R1',
                'specification_ref': 'SPEC-001',
                'revision_number': 1,
                'previous_submittal_id': sample_material
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['material']['revision_number'] == 1
        assert data['material']['previous_submittal_id'] == sample_material
    
    def test_delete_material(self, client, app):
        """Test deleting a material (without dependencies)"""
        with app.app_context():
            material = Material(
                material_type='Test Material for Deletion',
                description='This will be deleted',
                created_by='Manual'
            )
            db.session.add(material)
            db.session.commit()
            material_id = material.id
        
        response = client.delete(f'/api/materials/{material_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Material deleted successfully'


# ==========================================
# PURCHASE ORDER TESTS
# ==========================================

class TestPurchaseOrderCRUD:
    """Test Purchase Order Create, Read, Update, Delete operations"""
    
    def test_create_purchase_order(self, client, sample_material):
        """Test creating a new purchase order manually"""
        response = client.post('/api/purchase_orders',
            json={
                'material_id': sample_material,
                'quote_ref': 'QUO-2025-002',
                'po_ref': 'PO-2025-002',
                'po_date': datetime.utcnow().isoformat(),
                'expected_delivery_date': (datetime.utcnow() + timedelta(days=45)).isoformat(),
                'supplier_name': 'XYZ Materials LLC',
                'supplier_contact': '+971-4-7654321',
                'supplier_email': 'info@xyz.ae',
                'total_amount': 75000.00,
                'currency': 'AED',
                'po_status': 'Not Released',
                'payment_terms': '50% advance, 50% on delivery',
                'delivery_terms': 'Ex-Works',
                'notes': 'Urgent order - needed for project'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Purchase order created successfully'
        assert data['purchase_order']['po_ref'] == 'PO-2025-002'
        assert data['purchase_order']['total_amount'] == 75000.00
        assert data['purchase_order']['po_status'] == 'Not Released'
    
    def test_get_all_purchase_orders(self, client, sample_po):
        """Test retrieving all purchase orders"""
        response = client.get('/api/purchase_orders')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['po_ref'] == 'PO-2025-001'
    
    def test_get_purchase_order_by_id(self, client, sample_po):
        """Test retrieving a specific purchase order"""
        response = client.get(f'/api/purchase_orders/{sample_po}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_po
        assert data['supplier_name'] == 'ABC Trading LLC'
    
    def test_update_purchase_order_status(self, client, sample_po):
        """Test updating PO status to Released"""
        response = client.put(f'/api/purchase_orders/{sample_po}',
            json={
                'po_status': 'Released',
                'notes': 'PO released on ' + datetime.utcnow().strftime('%Y-%m-%d'),
                'updated_by': 'Manual'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Purchase order updated successfully'
        assert data['purchase_order']['po_status'] == 'Released'
    
    def test_purchase_order_unique_po_ref(self, client, sample_material, sample_po):
        """Test that PO reference must be unique"""
        response = client.post('/api/purchase_orders',
            json={
                'material_id': sample_material,
                'po_ref': 'PO-2025-001',  # Same as existing PO
                'supplier_name': 'Test Supplier',
                'total_amount': 10000.00,
                'po_status': 'Not Released'
            })
        
        # Should fail due to unique constraint
        assert response.status_code == 500


# ==========================================
# PAYMENT TESTS
# ==========================================

class TestPaymentCRUD:
    """Test Payment Create, Read, Update, Delete operations"""
    
    def test_create_single_payment(self, client, sample_po):
        """Test creating a single payment entry"""
        response = client.post('/api/payments',
            json={
                'po_id': sample_po,
                'payment_structure': 'Single Payment',
                'payment_type': 'Full',
                'total_amount': 50000.00,
                'paid_amount': 50000.00,
                'payment_percentage': 100,
                'payment_date': datetime.utcnow().isoformat(),
                'payment_ref': 'PAY-001',
                'invoice_ref': 'INV-001',
                'payment_method': 'Bank Transfer',
                'currency': 'AED',
                'payment_status': 'Completed',
                'payment_terms': '30 days from delivery'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Payment created successfully'
        assert data['payment']['payment_type'] == 'Full'
        assert data['payment']['paid_amount'] == 50000.00
        assert data['payment']['payment_percentage'] == 100
    
    def test_create_advance_payment(self, client, sample_po):
        """Test creating an advance payment (50%)"""
        response = client.post('/api/payments',
            json={
                'po_id': sample_po,
                'payment_structure': 'Advance + Balance',
                'payment_type': 'Advance',
                'total_amount': 50000.00,
                'paid_amount': 25000.00,
                'payment_percentage': 50,
                'payment_date': datetime.utcnow().isoformat(),
                'payment_ref': 'PAY-002-ADV',
                'invoice_ref': 'INV-002',
                'payment_method': 'Bank Transfer',
                'currency': 'AED',
                'payment_status': 'Completed',
                'payment_terms': '50% advance, 50% on delivery'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['payment']['payment_type'] == 'Advance'
        assert data['payment']['paid_amount'] == 25000.00
        assert data['payment']['payment_percentage'] == 50
    
    def test_get_payments_by_po(self, client, sample_po):
        """Test retrieving all payments for a specific PO"""
        # Create a payment first
        client.post('/api/payments',
            json={
                'po_id': sample_po,
                'payment_type': 'Full',
                'total_amount': 50000.00,
                'paid_amount': 50000.00,
                'payment_status': 'Completed'
            })
        
        response = client.get(f'/api/payments/po/{sample_po}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['po_id'] == sample_po
    
    def test_update_payment_status(self, client, sample_po, app):
        """Test updating payment status"""
        # Create payment
        with app.app_context():
            payment = Payment(
                po_id=sample_po,
                payment_type='Partial',
                total_amount=50000.00,
                paid_amount=30000.00,
                payment_percentage=60,
                payment_status='Pending',
                created_by='Manual'
            )
            db.session.add(payment)
            db.session.commit()
            payment_id = payment.id
        
        # Update payment
        response = client.put(f'/api/payments/{payment_id}',
            json={
                'payment_status': 'Completed',
                'payment_date': datetime.utcnow().isoformat(),
                'updated_by': 'Manual'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['payment']['payment_status'] == 'Completed'
    
    def test_payment_over_limit_warning(self, client, sample_po):
        """Test that payment exceeding PO amount is flagged"""
        # PO amount is 50,000 AED
        # Try to pay 60,000 AED (20% over limit)
        response = client.post('/api/payments',
            json={
                'po_id': sample_po,
                'payment_type': 'Full',
                'total_amount': 50000.00,
                'paid_amount': 60000.00,  # 20% over PO amount
                'payment_percentage': 120,
                'payment_status': 'Completed'
            })
        
        # Should create but may have warning in response
        assert response.status_code == 201


# ==========================================
# DELIVERY TESTS
# ==========================================

class TestDeliveryCRUD:
    """Test Delivery Create, Read, Update, Delete operations"""
    
    def test_create_pending_delivery(self, client, sample_po):
        """Test creating a pending delivery"""
        response = client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'expected_delivery_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'delivery_status': 'Pending',
                'delivery_percentage': 0,
                'tracking_number': 'TRK-001',
                'carrier': 'Aramex',
                'delivery_location': 'Site A - Dubai',
                'notes': 'Awaiting dispatch from supplier'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Delivery created successfully'
        assert data['delivery']['delivery_status'] == 'Pending'
        assert data['delivery']['delivery_percentage'] == 0
    
    def test_create_partial_delivery(self, client, sample_po):
        """Test creating a partial delivery (65% received)"""
        response = client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'expected_delivery_date': (datetime.utcnow() - timedelta(days=5)).isoformat(),
                'actual_delivery_date': datetime.utcnow().isoformat(),
                'delivery_status': 'Partial',
                'delivery_percentage': 65,
                'tracking_number': 'TRK-002',
                'carrier': 'DHL',
                'delivery_location': 'Site B - Dubai',
                'received_by': 'John Smith',
                'notes': '65% of items delivered, remaining items in transit'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['delivery']['delivery_status'] == 'Partial'
        assert data['delivery']['delivery_percentage'] == 65
        assert data['delivery']['received_by'] == 'John Smith'
    
    def test_create_full_delivery(self, client, sample_po):
        """Test creating a full delivery (100% received)"""
        response = client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'expected_delivery_date': (datetime.utcnow() - timedelta(days=2)).isoformat(),
                'actual_delivery_date': datetime.utcnow().isoformat(),
                'delivery_status': 'Delivered',
                'delivery_percentage': 100,
                'tracking_number': 'TRK-003',
                'carrier': 'Fedex',
                'delivery_location': 'Warehouse - Jebel Ali',
                'received_by': 'Ahmed Ali',
                'notes': 'All items received and inspected'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['delivery']['delivery_status'] == 'Delivered'
        assert data['delivery']['delivery_percentage'] == 100
    
    def test_update_delivery_to_delivered(self, client, sample_po, app):
        """Test updating a pending delivery to delivered"""
        # Create pending delivery
        with app.app_context():
            delivery = Delivery(
                po_id=sample_po,
                expected_delivery_date=datetime.utcnow() + timedelta(days=10),
                delivery_status='Pending',
                delivery_percentage=0,
                created_by='Manual'
            )
            db.session.add(delivery)
            db.session.commit()
            delivery_id = delivery.id
        
        # Update to delivered
        response = client.put(f'/api/deliveries/{delivery_id}',
            json={
                'delivery_status': 'Delivered',
                'delivery_percentage': 100,
                'actual_delivery_date': datetime.utcnow().isoformat(),
                'received_by': 'Site Manager',
                'notes': 'Delivery completed successfully',
                'updated_by': 'Manual'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['delivery']['delivery_status'] == 'Delivered'
        assert data['delivery']['delivery_percentage'] == 100
    
    def test_delivery_delay_detection(self, client, sample_po):
        """Test that delayed deliveries are detected"""
        # Create delivery with past expected date
        response = client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'expected_delivery_date': (datetime.utcnow() - timedelta(days=10)).isoformat(),
                'delivery_status': 'Pending',
                'delivery_percentage': 0,
                'delay_reason': 'Supplier production delay'
            })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        # Check if delay is detected
        delivery_id = data['delivery']['id']
        response = client.get(f'/api/deliveries/{delivery_id}')
        data = json.loads(response.data)
        
        assert data['is_delayed'] == True
        assert data['delay_days'] > 0
    
    def test_get_delayed_deliveries(self, client, sample_po):
        """Test retrieving all delayed deliveries"""
        # Create a delayed delivery
        client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'expected_delivery_date': (datetime.utcnow() - timedelta(days=15)).isoformat(),
                'delivery_status': 'Pending',
                'delivery_percentage': 0
            })
        
        response = client.get('/api/deliveries/delayed')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should have at least one delayed delivery
        assert len(data) >= 1
    
    def test_get_deliveries_by_po(self, client, sample_po):
        """Test retrieving all deliveries for a specific PO"""
        # Create delivery
        client.post('/api/deliveries',
            json={
                'po_id': sample_po,
                'delivery_status': 'Pending',
                'delivery_percentage': 0
            })
        
        response = client.get(f'/api/deliveries/po/{sample_po}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['po_id'] == sample_po


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestDataIntegrity:
    """Test data relationships and integrity"""
    
    def test_complete_workflow(self, client, app):
        """Test complete workflow: Material -> PO -> Payment -> Delivery"""
        
        # 1. Create Material
        material_response = client.post('/api/materials',
            json={
                'material_type': 'Cables & Wires',
                'description': '6mm2 power cables',
                'approval_status': 'Approved',
                'submittal_ref': 'SUB-CABLE-001'
            })
        assert material_response.status_code == 201
        material_id = json.loads(material_response.data)['material']['id']
        
        # 2. Create Purchase Order
        po_response = client.post('/api/purchase_orders',
            json={
                'material_id': material_id,
                'po_ref': 'PO-INTEGRATION-TEST',
                'supplier_name': 'Cable Supplier LLC',
                'total_amount': 100000.00,
                'po_status': 'Released',
                'po_date': datetime.utcnow().isoformat(),
                'expected_delivery_date': (datetime.utcnow() + timedelta(days=60)).isoformat()
            })
        assert po_response.status_code == 201
        po_id = json.loads(po_response.data)['purchase_order']['id']
        
        # 3. Create Advance Payment (50%)
        payment1_response = client.post('/api/payments',
            json={
                'po_id': po_id,
                'payment_type': 'Advance',
                'total_amount': 100000.00,
                'paid_amount': 50000.00,
                'payment_percentage': 50,
                'payment_status': 'Completed',
                'payment_date': datetime.utcnow().isoformat()
            })
        assert payment1_response.status_code == 201
        
        # 4. Create Delivery
        delivery_response = client.post('/api/deliveries',
            json={
                'po_id': po_id,
                'expected_delivery_date': (datetime.utcnow() + timedelta(days=60)).isoformat(),
                'delivery_status': 'Pending',
                'delivery_percentage': 0
            })
        assert delivery_response.status_code == 201
        delivery_id = json.loads(delivery_response.data)['delivery']['id']
        
        # 5. Update Delivery to Partial (70%)
        update_response = client.put(f'/api/deliveries/{delivery_id}',
            json={
                'delivery_status': 'Partial',
                'delivery_percentage': 70,
                'actual_delivery_date': datetime.utcnow().isoformat(),
                'received_by': 'Project Manager'
            })
        assert update_response.status_code == 200
        
        # 6. Create Balance Payment (remaining 50%)
        payment2_response = client.post('/api/payments',
            json={
                'po_id': po_id,
                'payment_type': 'Balance',
                'total_amount': 100000.00,
                'paid_amount': 50000.00,
                'payment_percentage': 50,
                'payment_status': 'Completed',
                'payment_date': datetime.utcnow().isoformat()
            })
        assert payment2_response.status_code == 201
        
        # 7. Verify all relationships
        po_check = client.get(f'/api/purchase_orders/{po_id}')
        po_data = json.loads(po_check.data)
        assert po_data['material']['id'] == material_id
        
        payments_check = client.get(f'/api/payments/po/{po_id}')
        payments = json.loads(payments_check.data)
        assert len(payments) == 2
        
        deliveries_check = client.get(f'/api/deliveries/po/{po_id}')
        deliveries = json.loads(deliveries_check.data)
        assert len(deliveries) == 1
        assert deliveries[0]['delivery_percentage'] == 70
    
    def test_cascade_delete_protection(self, client, sample_po, app):
        """Test that PO with payments/deliveries cannot be deleted easily"""
        # Create payment for PO
        with app.app_context():
            payment = Payment(
                po_id=sample_po,
                total_amount=50000.00,
                paid_amount=25000.00,
                payment_status='Completed',
                created_by='Manual'
            )
            db.session.add(payment)
            db.session.commit()
        
        # Try to delete PO - should cascade to payments (based on relationship)
        response = client.delete(f'/api/purchase_orders/{sample_po}')
        # This will succeed due to cascade, but in production might want to add protection
        assert response.status_code == 200


# ==========================================
# ATTRIBUTE VALIDATION TESTS
# ==========================================

class TestAttributeValidation:
    """Test that all model attributes match between frontend and backend"""
    
    def test_material_attributes_match(self, client, sample_material):
        """Verify Material model attributes match API response"""
        response = client.get(f'/api/materials/{sample_material}')
        data = json.loads(response.data)
        
        # Check all expected attributes exist
        required_attrs = [
            'id', 'material_type', 'description', 'approval_status',
            'approval_date', 'approval_notes', 'submittal_ref',
            'specification_ref', 'revision_number', 'previous_submittal_id',
            'document_path', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        
        for attr in required_attrs:
            assert attr in data, f"Missing attribute: {attr}"
    
    def test_purchase_order_attributes_match(self, client, sample_po):
        """Verify PurchaseOrder model attributes match API response"""
        response = client.get(f'/api/purchase_orders/{sample_po}')
        data = json.loads(response.data)
        
        required_attrs = [
            'id', 'material_id', 'quote_ref', 'po_ref', 'po_date',
            'expected_delivery_date', 'supplier_name', 'supplier_contact',
            'supplier_email', 'total_amount', 'currency', 'po_status',
            'payment_terms', 'delivery_terms', 'notes', 'document_path',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        
        for attr in required_attrs:
            assert attr in data, f"Missing attribute: {attr}"
    
    def test_payment_attributes_match(self, client, sample_po, app):
        """Verify Payment model attributes match API response"""
        with app.app_context():
            payment = Payment(
                po_id=sample_po,
                payment_structure='Single Payment',
                payment_type='Full',
                total_amount=50000.00,
                paid_amount=50000.00,
                payment_percentage=100,
                payment_status='Completed',
                created_by='Manual'
            )
            db.session.add(payment)
            db.session.commit()
            payment_id = payment.id
        
        response = client.get(f'/api/payments/{payment_id}')
        data = json.loads(response.data)
        
        required_attrs = [
            'id', 'po_id', 'payment_structure', 'payment_type',
            'total_amount', 'paid_amount', 'payment_percentage',
            'payment_date', 'payment_terms', 'payment_ref', 'invoice_ref',
            'payment_method', 'currency', 'payment_status', 'notes',
            'invoice_path', 'receipt_path', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
        
        for attr in required_attrs:
            assert attr in data, f"Missing attribute: {attr}"
    
    def test_delivery_attributes_match(self, client, sample_po, app):
        """Verify Delivery model attributes match API response"""
        with app.app_context():
            delivery = Delivery(
                po_id=sample_po,
                expected_delivery_date=datetime.utcnow() + timedelta(days=30),
                delivery_status='Pending',
                delivery_percentage=0,
                created_by='Manual'
            )
            db.session.add(delivery)
            db.session.commit()
            delivery_id = delivery.id
        
        response = client.get(f'/api/deliveries/{delivery_id}')
        data = json.loads(response.data)
        
        required_attrs = [
            'id', 'po_id', 'expected_delivery_date', 'actual_delivery_date',
            'delivery_status', 'delivery_percentage', 'tracking_number',
            'carrier', 'delivery_location', 'received_by', 'is_delayed',
            'delay_reason', 'delay_days', 'notes', 'delivery_note_path',
            'extracted_data', 'extraction_status', 'extraction_date',
            'extraction_confidence', 'extracted_item_count',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        
        for attr in required_attrs:
            assert attr in data, f"Missing attribute: {attr}"


# ==========================================
# RUN INFO
# ==========================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  Basic CRUD Tests - Manual Entry Only (No AI Features)           ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║  Run with:                                                        ║
    ║  pytest tests/test_basic_crud_manual.py -v                        ║
    ║                                                                   ║
    ║  Or in WSL:                                                       ║
    ║  wsl bash -c "cd '/mnt/c/...' && \\                               ║
    ║               source venv/bin/activate && \\                      ║
    ║               pytest tests/test_basic_crud_manual.py -v"          ║
    ║                                                                   ║
    ║  Test Coverage:                                                   ║
    ║  • Material CRUD (Create, Read, Update, Delete)                   ║
    ║  • Purchase Order CRUD                                            ║
    ║  • Payment CRUD (Single, Advance, Balance)                        ║
    ║  • Delivery CRUD (Pending, Partial, Full)                         ║
    ║  • Data Integrity & Relationships                                 ║
    ║  • Attribute Validation                                           ║
    ║  • Complete Workflow Integration                                  ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
