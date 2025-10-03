"""
Database initialization script
Run this file to create all database tables and optionally populate with sample data
"""

from app import create_app
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery
from models.ai_suggestion import AISuggestion
from models.file import File
from config import Config
from datetime import datetime, timedelta

def init_database(with_sample_data=False):
    """Initialize database and optionally populate with sample data"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (be careful in production!)
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        if with_sample_data:
            print("\nPopulating with sample data...")
            populate_sample_data()
            print("✓ Sample data added successfully!")
        
        print("\n✓ Database initialization complete!")

def populate_sample_data():
    """Add sample data for testing"""
    
    # Sample Materials
    materials_data = [
        {
            'material_type': 'PVC Conduits & Accessories',
            'description': '25mm PVC conduits with accessories',
            'approval_status': 'Approved',
            'approval_date': datetime.utcnow() - timedelta(days=30),
            'quantity': 500,
            'unit': 'meters'
        },
        {
            'material_type': 'Cables & Wires',
            'description': '4mm² copper cables',
            'approval_status': 'Pending',
            'quantity': 1000,
            'unit': 'meters'
        },
        {
            'material_type': 'DB',
            'description': 'Distribution Board 24-way',
            'approval_status': 'Under Review',
            'quantity': 5,
            'unit': 'units'
        },
        {
            'material_type': 'VRF System',
            'description': 'Variable Refrigerant Flow HVAC System',
            'approval_status': 'Approved as Noted',
            'approval_date': datetime.utcnow() - timedelta(days=15),
            'quantity': 2,
            'unit': 'systems'
        },
        {
            'material_type': 'Fire Alarm system',
            'description': 'Addressable Fire Alarm Control Panel',
            'approval_status': 'Approved',
            'approval_date': datetime.utcnow() - timedelta(days=20),
            'quantity': 1,
            'unit': 'system'
        }
    ]
    
    materials = []
    for data in materials_data:
        material = Material(**data)
        db.session.add(material)
        materials.append(material)
    
    db.session.commit()
    
    # Sample Purchase Orders
    po1 = PurchaseOrder(
        material_id=materials[0].id,
        quote_ref='Q-2025-001',
        po_ref='PO-2025-001',
        po_date=datetime.utcnow() - timedelta(days=25),
        supplier_name='ABC Electrical Supplies',
        supplier_contact='+971-50-1234567',
        supplier_email='sales@abcelectrical.ae',
        total_amount=15000,
        po_status='Released',
        payment_terms='30 days from delivery'
    )
    
    po2 = PurchaseOrder(
        material_id=materials[3].id,
        quote_ref='Q-2025-002',
        po_ref='PO-2025-002',
        po_date=datetime.utcnow() - timedelta(days=10),
        supplier_name='Dubai HVAC Systems',
        supplier_contact='+971-50-9876543',
        supplier_email='info@dubaihvac.ae',
        total_amount=250000,
        po_status='Released',
        payment_terms='Advance 30%, Balance on delivery'
    )
    
    db.session.add(po1)
    db.session.add(po2)
    db.session.commit()
    
    # Sample Payments
    payment1 = Payment(
        po_id=po1.id,
        payment_structure='Single Payment',
        payment_type='Full',
        total_amount=15000,
        paid_amount=0,
        payment_status='Pending'
    )
    payment1.calculate_percentage()
    
    payment2 = Payment(
        po_id=po2.id,
        payment_structure='Advance + Balance',
        payment_type='Advance',
        total_amount=250000,
        paid_amount=75000,
        payment_date=datetime.utcnow() - timedelta(days=5),
        payment_ref='PAY-2025-001',
        payment_status='Partial'
    )
    payment2.calculate_percentage()
    
    db.session.add(payment1)
    db.session.add(payment2)
    db.session.commit()
    
    # Sample Deliveries
    delivery1 = Delivery(
        po_id=po1.id,
        expected_delivery_date=datetime.utcnow() + timedelta(days=10),
        delivery_status='In Transit',
        ordered_quantity=500,
        delivered_quantity=0,
        unit='meters',
        tracking_number='TRK-12345',
        carrier='Emirates Post'
    )
    
    delivery2 = Delivery(
        po_id=po2.id,
        expected_delivery_date=datetime.utcnow() + timedelta(days=30),
        delivery_status='Pending',
        ordered_quantity=2,
        delivered_quantity=0,
        unit='systems'
    )
    
    db.session.add(delivery1)
    db.session.add(delivery2)
    db.session.commit()
    
    # Sample AI Suggestion
    suggestion = AISuggestion(
        target_table='deliveries',
        target_id=delivery1.id,
        action_type='update',
        ai_model='claude-3-sonnet',
        confidence_score=85,
        extraction_source='email',
        ai_reasoning='Extracted delivery update from supplier email confirmation',
        status='pending'
    )
    suggestion.set_suggested_data({
        'delivery_status': 'In Transit',
        'tracking_number': 'TRK-12345',
        'carrier': 'Emirates Post'
    })
    suggestion.set_missing_fields(['actual_delivery_date'])
    
    db.session.add(suggestion)
    db.session.commit()
    
    print(f"  - Created {len(materials)} materials")
    print(f"  - Created 2 purchase orders")
    print(f"  - Created 2 payment records")
    print(f"  - Created 2 delivery records")
    print(f"  - Created 1 AI suggestion")

if __name__ == '__main__':
    import sys
    
    # Check if user wants sample data
    with_samples = '--with-samples' in sys.argv or '-s' in sys.argv
    skip_confirm = '-y' in sys.argv or '--yes' in sys.argv
    
    print("=" * 60)
    print("Material Delivery Dashboard - Database Initialization")
    print("=" * 60)
    
    if with_samples:
        print("\nMode: Initialize with sample data")
    else:
        print("\nMode: Initialize empty database")
        print("(Use --with-samples or -s flag to add sample data)")
    
    if skip_confirm:
        confirm = 'yes'
    else:
        confirm = input("\nProceed with database initialization? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        init_database(with_sample_data=with_samples)
    else:
        print("Database initialization cancelled.")
