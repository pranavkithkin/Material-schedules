#!/usr/bin/env python3
"""
Create test delivery record for n8n workflow testing
Creates Material → Purchase Order → Delivery chain
"""

from app import create_app
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("🔧 Creating test data for n8n workflow...")
    
    # Check if test material exists
    material = Material.query.filter_by(material_type='DB').first()
    
    if not material:
        print("📦 Creating test material (DB)...")
        material = Material(
            material_type='DB',
            description='Distribution Board for electrical system',
            submittal_ref='SUB-DB-001',
            specification_ref='SPEC-DB-001',
            approval_status='Approved',
            created_by='System'
        )
        db.session.add(material)
        db.session.flush()
        print(f'   ✅ Created material ID: {material.id}')
    else:
        print(f'   ✅ Using existing material ID: {material.id}')
    
    # Check if test PO exists
    po = PurchaseOrder.query.filter_by(po_ref='TEST-PO-001').first()
    
    if not po:
        print("📝 Creating test purchase order...")
        po = PurchaseOrder(
            material_id=material.id,
            po_ref='TEST-PO-001',
            supplier_name='Test Supplier LLC',
            po_date=datetime.now(),
            total_amount=50000.00,
            currency='AED',
            payment_terms='Net 30',
            po_status='Released',
            created_by='System'
        )
        db.session.add(po)
        db.session.flush()
        print(f'   ✅ Created PO ID: {po.id}')
        print(f'   ✅ PO Reference: {po.po_ref}')
    else:
        print(f'   ✅ Using existing PO ID: {po.id}')
        print(f'   ✅ PO Reference: {po.po_ref}')
    
    # Check if test delivery exists
    delivery = Delivery.query.filter_by(po_id=po.id).first()
    
    if not delivery:
        print("🚚 Creating test delivery...")
        delivery = Delivery(
            po_id=po.id,
            expected_delivery_date=datetime.now() + timedelta(days=7),
            delivery_status='Pending',
            delivery_location='Test Site Office',
            extraction_status='pending',
            created_by='System'
        )
        db.session.add(delivery)
        db.session.commit()
        print(f'   ✅ Created delivery ID: {delivery.id}')
    else:
        print(f'   ✅ Using existing delivery ID: {delivery.id}')
    
    print("\n" + "="*60)
    print("✅ TEST DATA READY!")
    print("="*60)
    print(f"\n📊 Test Record Details:")
    print(f"   Material ID:     {material.id}")
    print(f"   Material Type:   {material.material_type}")
    print(f"   PO ID:           {po.id}")
    print(f"   PO Reference:    {po.po_ref}")
    print(f"   Delivery ID:     {delivery.id}")
    print(f"   Delivery Status: {delivery.delivery_status}")
    print(f"\n🧪 Use this in your n8n test:")
    print(f"   delivery_id: {delivery.id}")
    print(f"   file_id: 1")
    print(f"   po_ref: '{po.po_ref}'")
    print("\n🚀 Test command:")
    print(f"   python3 test_n8n_extraction.py")
    print("="*60)
