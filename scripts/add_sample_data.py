"""
Add sample data to test the new field structure
Run: python scripts/add_sample_data.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery
from datetime import datetime, timedelta

def add_sample_data():
    """Add comprehensive sample data for testing"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("Adding Sample Data - New Field Structure")
        print("="*60)
        
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        Delivery.query.delete()
        Payment.query.delete()
        PurchaseOrder.query.delete()
        Material.query.delete()
        db.session.commit()
        print("   ✓ Existing data cleared")
        
        # 1. Create Materials with Revision Tracking
        print("\n1. Creating Material Submittals...")
        
        # Material 1: Sanitary Wares - Initial Submittal (Approved)
        material1 = Material(
            material_type='Sanitary Wares',
            description='Complete sanitary package: Shower heads (10), Shower mixers (8), Basin mixers (12), WCs (6), Shattafs (15), and accessories',
            approval_status='Approved',
            approval_date=datetime.now() - timedelta(days=30),
            revision_number=0,
            previous_submittal_id=None,
            submittal_ref='SUB-2025-001',
            specification_ref='SPEC-SANITARY-A1',
            approval_notes='All items approved as submitted',
            created_by='System',
            updated_by='System'
        )
        db.session.add(material1)
        db.session.flush()  # Get ID for material1
        print(f"   ✓ Material 1: {material1.material_type} - Rev {material1.revision_number} (Approved)")
        
        # Material 2: Electrical Conduits - Initial Submittal (Revise & Resubmit)
        material2 = Material(
            material_type='PVC Conduits & Accessories',
            description='25mm and 32mm PVC conduits with junction boxes and accessories',
            approval_status='Revise & Resubmit',
            approval_date=datetime.now() - timedelta(days=25),
            revision_number=0,
            previous_submittal_id=None,
            submittal_ref='SUB-2025-002-R0',
            specification_ref='SPEC-ELECTRICAL-B2',
            approval_notes='Change conduit material to UV-resistant type',
            created_by='System',
            updated_by='System'
        )
        db.session.add(material2)
        db.session.flush()  # Get ID for material2
        print(f"   ✓ Material 2: {material2.material_type} - Rev {material2.revision_number} (Revise & Resubmit)")
        
        # Material 3: Electrical Conduits - Resubmission (Approved)
        material3 = Material(
            material_type='PVC Conduits & Accessories',
            description='25mm and 32mm UV-resistant PVC conduits with junction boxes and accessories',
            approval_status='Approved',
            approval_date=datetime.now() - timedelta(days=15),
            revision_number=1,
            previous_submittal_id=material2.id,
            submittal_ref='SUB-2025-002-R1',
            specification_ref='SPEC-ELECTRICAL-B2',
            approval_notes='Approved with UV-resistant material as requested',
            created_by='System',
            updated_by='System'
        )
        db.session.add(material3)
        db.session.flush()
        print(f"   ✓ Material 3: {material3.material_type} - Rev {material3.revision_number} (Approved - Linked to Rev 0)")
        
        # Material 4: Floor Tiles - Under Review
        material4 = Material(
            material_type='Porcelain Floor Tiles',
            description='600x600mm anti-slip porcelain tiles for bathroom floors',
            approval_status='Under Review',
            approval_date=None,
            revision_number=0,
            previous_submittal_id=None,
            submittal_ref='SUB-2025-003',
            specification_ref='SPEC-TILES-C1',
            approval_notes='Awaiting consultant review',
            created_by='System',
            updated_by='System'
        )
        db.session.add(material4)
        db.session.flush()
        print(f"   ✓ Material 4: {material4.material_type} - Rev {material4.revision_number} (Under Review)")
        
        # 2. Create Purchase Orders with Payment Terms
        print("\n2. Creating Purchase Orders...")
        
        # PO 1: Sanitary Wares (Large multi-item PO)
        po1 = PurchaseOrder(
            material_id=material1.id,
            quote_ref='QT-2025-001',
            po_ref='PO-2025-001',
            po_date=datetime.now() - timedelta(days=28),
            supplier_name='Al Haramain Sanitary Trading LLC',
            supplier_contact='+971-4-234-5678',
            supplier_email='sales@alharamain.ae',
            total_amount=45000.00,
            currency='AED',
            po_status='Active',
            payment_terms='40% Advance Payment, 60% Balance on Delivery. Net 30 days from invoice date.',
            delivery_terms='FOB Dubai. Delivery within 45 days. Partial deliveries accepted.',
            notes='Multi-item package: 50+ items including shower heads, mixers, WCs, shattafs, and accessories',
            created_by='System',
            updated_by='System'
        )
        db.session.add(po1)
        db.session.flush()
        print(f"   ✓ PO 1: {po1.po_ref} - {po1.supplier_name} - AED {po1.total_amount:,.2f}")
        print(f"      Payment Terms: {po1.payment_terms}")
        
        # PO 2: Electrical Conduits
        po2 = PurchaseOrder(
            material_id=material3.id,
            quote_ref='QT-2025-002',
            po_ref='PO-2025-002',
            po_date=datetime.now() - timedelta(days=20),
            supplier_name='Emirates Electrical Supplies',
            supplier_contact='+971-4-567-8901',
            supplier_email='orders@emirateselectric.ae',
            total_amount=18500.00,
            currency='AED',
            po_status='Active',
            payment_terms='50% Advance, 50% on Delivery. Payment due within 15 days.',
            delivery_terms='Ex-Works. Delivery 30 days from PO date.',
            notes='UV-resistant PVC conduits as per approved submittal Rev 1',
            created_by='System',
            updated_by='System'
        )
        db.session.add(po2)
        db.session.flush()
        print(f"   ✓ PO 2: {po2.po_ref} - {po2.supplier_name} - AED {po2.total_amount:,.2f}")
        print(f"      Payment Terms: {po2.payment_terms}")
        
        # PO 3: Floor Tiles (Pending approval)
        po3 = PurchaseOrder(
            material_id=material4.id,
            quote_ref='QT-2025-003',
            po_ref='PO-2025-003',
            po_date=datetime.now() - timedelta(days=10),
            supplier_name='Dubai Tiles & Ceramics',
            supplier_contact='+971-4-789-0123',
            supplier_email='sales@dubaitiles.ae',
            total_amount=32000.00,
            currency='AED',
            po_status='Pending',
            payment_terms='100% Payment before delivery. LC payment accepted.',
            delivery_terms='FOB Jebel Ali. 60 days delivery after payment.',
            notes='Awaiting material approval before processing',
            created_by='System',
            updated_by='System'
        )
        db.session.add(po3)
        db.session.flush()
        print(f"   ✓ PO 3: {po3.po_ref} - {po3.supplier_name} - AED {po3.total_amount:,.2f}")
        print(f"      Payment Terms: {po3.payment_terms}")
        
        # 3. Create Payments with New Structure
        print("\n3. Creating Payments...")
        
        # Payment 1: PO-001 Advance (Partial - 40%)
        payment1 = Payment(
            po_id=po1.id,
            payment_structure='Advance Payment',
            payment_type='Advance',
            total_amount=45000.00,
            paid_amount=18000.00,
            payment_percentage=40.0,
            payment_date=datetime.now() - timedelta(days=27),
            payment_terms=po1.payment_terms,  # Copied from PO
            payment_ref='PAY-2025-001',
            invoice_ref='INV-AHS-2025-001',
            payment_method='Bank Transfer',
            currency='AED',
            payment_status='Partial',
            notes='40% advance payment as per PO terms. Balance AED 27,000 due on delivery.',
            created_by='System',
            updated_by='System'
        )
        db.session.add(payment1)
        print(f"   ✓ Payment 1: {payment1.payment_ref} - AED {payment1.paid_amount:,.2f} (40% - Partial)")
        print(f"      Status: {payment1.payment_status} - Balance: AED {po1.total_amount - payment1.paid_amount:,.2f}")
        
        # Payment 2: PO-002 Advance (Partial - 50%)
        payment2 = Payment(
            po_id=po2.id,
            payment_structure='Advance Payment',
            payment_type='Advance',
            total_amount=18500.00,
            paid_amount=9250.00,
            payment_percentage=50.0,
            payment_date=datetime.now() - timedelta(days=18),
            payment_terms=po2.payment_terms,
            payment_ref='PAY-2025-002',
            invoice_ref='INV-EES-2025-001',
            payment_method='Cheque',
            currency='AED',
            payment_status='Partial',
            notes='50% advance payment. Balance due on delivery.',
            created_by='System',
            updated_by='System'
        )
        db.session.add(payment2)
        print(f"   ✓ Payment 2: {payment2.payment_ref} - AED {payment2.paid_amount:,.2f} (50% - Partial)")
        print(f"      Status: {payment2.payment_status} - Balance: AED {po2.total_amount - payment2.paid_amount:,.2f}")
        
        # Payment 3: PO-002 Balance (Full - Completes PO)
        payment3 = Payment(
            po_id=po2.id,
            payment_structure='Balance Payment',
            payment_type='Balance',
            total_amount=18500.00,
            paid_amount=9250.00,
            payment_percentage=50.0,
            payment_date=datetime.now() - timedelta(days=5),
            payment_terms=po2.payment_terms,
            payment_ref='PAY-2025-003',
            invoice_ref='INV-EES-2025-002',
            payment_method='Bank Transfer',
            currency='AED',
            payment_status='Full',
            notes='Final 50% payment on delivery. PO fully paid.',
            created_by='System',
            updated_by='System'
        )
        db.session.add(payment3)
        print(f"   ✓ Payment 3: {payment3.payment_ref} - AED {payment3.paid_amount:,.2f} (50% - Full)")
        print(f"      Status: {payment3.payment_status} - PO-2025-002 fully paid (AED {payment2.paid_amount + payment3.paid_amount:,.2f})")
        
        # 4. Create Deliveries with Percentage Tracking
        print("\n4. Creating Deliveries...")
        
        # Delivery 1: PO-001 First Partial Delivery (65%)
        delivery1 = Delivery(
            po_id=po1.id,
            expected_delivery_date=datetime.now() - timedelta(days=5),
            actual_delivery_date=datetime.now() - timedelta(days=3),
            delivery_status='Partial',
            delivery_percentage=65.0,
            tracking_number='DO-2025-001',
            carrier='Emirates Logistics',
            delivery_location='Project Site - Building A',
            received_by='Site Engineer - Ahmed Hassan',
            is_delayed=False,
            delay_reason=None,
            delay_days=0,
            notes='First partial delivery: Shower heads (10/10), Mixers (8/8), WCs (4/6), Shattafs (0/15). Remaining items scheduled for next week.',
            delivery_note_path='documents/delivery_orders/DO-2025-001.pdf',
            created_by='System',
            updated_by='System'
        )
        db.session.add(delivery1)
        print(f"   ✓ Delivery 1: {delivery1.tracking_number} - {delivery1.delivery_percentage}% Complete")
        print(f"      Status: {delivery1.delivery_status} - Items delivered: Shower heads (10), Mixers (8), WCs (4/6)")
        
        # Delivery 2: PO-002 Full Delivery (100%)
        delivery2 = Delivery(
            po_id=po2.id,
            expected_delivery_date=datetime.now() - timedelta(days=8),
            actual_delivery_date=datetime.now() - timedelta(days=6),
            delivery_status='Delivered',
            delivery_percentage=100.0,
            tracking_number='DO-2025-002',
            carrier='Fast Track Shipping',
            delivery_location='Project Site - Building B',
            received_by='Electrical Foreman - Mohammad Ali',
            is_delayed=False,
            delay_reason=None,
            delay_days=0,
            notes='Complete delivery of UV-resistant PVC conduits and accessories. All items checked and verified.',
            delivery_note_path='documents/delivery_orders/DO-2025-002.pdf',
            created_by='System',
            updated_by='System'
        )
        db.session.add(delivery2)
        print(f"   ✓ Delivery 2: {delivery2.tracking_number} - {delivery2.delivery_percentage}% Complete")
        print(f"      Status: {delivery2.delivery_status} - Fully delivered")
        
        # Delivery 3: PO-001 Scheduled (Pending)
        delivery3 = Delivery(
            po_id=po1.id,
            expected_delivery_date=datetime.now() + timedelta(days=7),
            actual_delivery_date=None,
            delivery_status='Pending',
            delivery_percentage=0.0,
            tracking_number=None,
            carrier='Emirates Logistics',
            delivery_location='Project Site - Building A',
            received_by=None,
            is_delayed=False,
            delay_reason=None,
            delay_days=0,
            notes='Second delivery scheduled: Remaining WCs (2), Shattafs (15), and accessories. Will complete PO.',
            delivery_note_path=None,
            created_by='System',
            updated_by='System'
        )
        db.session.add(delivery3)
        print(f"   ✓ Delivery 3: Pending - Expected {delivery3.expected_delivery_date.strftime('%Y-%m-%d')}")
        print(f"      Status: {delivery3.delivery_status} - Remaining items: WCs (2), Shattafs (15)")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Sample Data Added Successfully!")
        print("="*60)
        
        # Summary
        print("\n📊 Summary:")
        print(f"   Materials: 4 (including 1 revision link)")
        print(f"   Purchase Orders: 3")
        print(f"   Payments: 3 (showing Full/Partial tracking)")
        print(f"   Deliveries: 3 (showing percentage completion)")
        
        print("\n🎯 Key Testing Scenarios:")
        print("   1. Material Revision: SUB-2025-002 Rev 0 → Rev 1")
        print("   2. Payment Terms: Auto-display from PO")
        print("   3. Partial Payment: PO-001 (40% paid, balance due)")
        print("   4. Full Payment: PO-002 (100% paid)")
        print("   5. Partial Delivery: PO-001 (65% delivered)")
        print("   6. Full Delivery: PO-002 (100% delivered)")
        print("   7. Pending Delivery: PO-001 second delivery")
        
        print("\n💡 Test Cases:")
        print("   ✓ Payment Reminder: PO-001 has balance due")
        print("   ✓ Revision History: Material Rev 0 → Rev 1 linked")
        print("   ✓ Progress Bars: Delivery 1 shows 65% visual")
        print("   ✓ Multi-item PO: 50+ items tracked as percentage")
        print("   ✓ Payment Terms: Display from PO reference")
        
        print("\n🚀 Ready for UI Testing!")
        print("   Run: python run.py")
        print("   Navigate to each form and verify displays\n")

if __name__ == '__main__':
    try:
        add_sample_data()
    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
