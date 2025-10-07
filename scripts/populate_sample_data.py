"""
Script to populate database with sample data for analytics testing
Run this to see the analytics dashboard with meaningful data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.purchase_order import PurchaseOrder
from models.material import Material
from models.delivery import Delivery
from models.payment import Payment
from datetime import datetime, timedelta
import random

def populate_sample_data():
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting sample data population...")
        
        # Sample suppliers
        suppliers = [
            "Al Masood Steel LLC",
            "Dubai Steel Trading",
            "Emirates Construction Supplies",
            "Gulf Building Materials",
            "National Cement Factory"
        ]
        
        # Sample materials
        material_types = [
            "Reinforcement Steel",
            "Cement",
            "Concrete Blocks",
            "Steel Beams",
            "Aluminum Sheets",
            "Ceramic Tiles",
            "Paint & Coatings",
            "Electrical Cables",
            "Plumbing Fixtures",
            "HVAC Equipment"
        ]
        
        # Create 30 Materials and POs over the last 6 months
        print("📄 Creating Materials and Purchase Orders...")
        for i in range(30):
            days_ago = random.randint(0, 180)
            date = datetime.now() - timedelta(days=days_ago)
            supplier = random.choice(suppliers)
            material_type = random.choice(material_types)
            
            # Create Material
            material = Material(
                material_type=material_type,
                description=f"{material_type} - Grade {random.choice(['A', 'B', 'Premium'])}",
                approval_status=random.choice(['Approved', 'Approved', 'Approved', 'Pending']),
                approval_date=date if random.random() < 0.8 else None,
                submittal_ref=f"SUB-2024-{1000 + i}",
                specification_ref=f"SPEC-{random.randint(100, 999)}",
                created_by='Sample Data Generator'
            )
            db.session.add(material)
            db.session.flush()
            
            # Create PO for this material
            total_amount = random.uniform(50000, 500000)
            po = PurchaseOrder(
                material_id=material.id,
                po_ref=f"PO-2024-{1000 + i}",
                quote_ref=f"QT-2024-{1000 + i}",
                po_date=date,
                expected_delivery_date=date + timedelta(days=random.randint(30, 90)),
                supplier_name=supplier,
                supplier_contact=f"+971-{random.randint(50, 59)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                supplier_email=f"contact@{supplier.lower().replace(' ', '')}.ae",
                total_amount=total_amount,
                currency='AED',
                po_status=random.choice(['Released', 'Released', 'Released', 'Not Released']),
                payment_terms=random.choice(['30 Days', '60 Days', '90 Days', 'Net 30']),
                delivery_terms=random.choice(['Ex-Works', 'FOB', 'CIF', 'DDP']),
                created_by='Sample Data Generator'
            )
            db.session.add(po)
            db.session.flush()
            
            # Create deliveries for released POs (70% complete, 20% partial, 10% pending)
            if po.po_status == 'Released':
                delivery_status = random.choices(
                    ['Completed', 'Partial', 'Pending'],
                    weights=[0.7, 0.2, 0.1]
                )[0]
                
                if delivery_status in ['Completed', 'Partial']:
                    # Calculate delivery date (some on time, some delayed)
                    delay_factor = random.choices(
                        [-10, -5, 0, 5, 10, 20, 30],  # days variation
                        weights=[0.1, 0.15, 0.3, 0.2, 0.15, 0.05, 0.05]
                    )[0]
                    delivery_date = po.expected_delivery_date + timedelta(days=delay_factor) if po.expected_delivery_date else date + timedelta(days=random.randint(30, 90))
                    
                    delivery = Delivery(
                        po_id=po.id,
                        expected_delivery_date=po.expected_delivery_date,
                        actual_delivery_date=delivery_date,
                        delivery_status=delivery_status,
                        delivery_percentage=100 if delivery_status == 'Completed' else random.uniform(50, 90),
                        tracking_number=f"TRK-{po.po_ref}",
                        carrier=random.choice(['Aramex', 'DHL', 'FedEx', 'Own Transport']),
                        notes=f"Delivered by {supplier}",
                        created_by='Sample Data Generator'
                    )
                    delivery.check_delay()  # Calculate delay info
                    db.session.add(delivery)
                    db.session.flush()
                    
                    # Create payment for deliveries (80% chance)
                    if random.random() < 0.8:
                        payment_days = random.randint(0, 60)
                        payment_date = delivery_date + timedelta(days=payment_days)
                        payment_amount = total_amount * random.uniform(0.3, 1.0)  # Partial or full payment
                        
                        # Determine if payment is made yet
                        is_paid = payment_date < datetime.now()
                        
                        payment = Payment(
                            po_id=po.id,
                            total_amount=total_amount,
                            paid_amount=payment_amount if is_paid else 0,
                            payment_date=payment_date if is_paid else None,
                            payment_status='Completed' if is_paid else 'Pending',
                            payment_type='Full' if payment_amount >= total_amount * 0.95 else 'Partial',
                            payment_method=random.choice(['Bank Transfer', 'Cheque', 'Cash']) if is_paid else None,
                            payment_ref=f"PAY-{po.po_ref}" if is_paid else None,
                            invoice_ref=f"INV-{po.po_ref}",
                            payment_terms=po.payment_terms,
                            created_by='Sample Data Generator'
                        )
                        payment.calculate_percentage()
                        db.session.add(payment)
        
        db.session.commit()
        
        # Print summary
        materials_count = Material.query.count()
        pos_count = PurchaseOrder.query.count()
        deliveries_count = Delivery.query.count()
        payments_count = Payment.query.count()
        
        print(f"\n✅ Sample data created successfully!")
        print(f"📊 Summary:")
        print(f"   - Materials: {materials_count}")
        print(f"   - Purchase Orders: {pos_count}")
        print(f"   - Deliveries: {deliveries_count}")
        print(f"   - Payments: {payments_count}")
        print(f"\n🎉 Your analytics dashboard should now show meaningful data!")
        print(f"🌐 Visit: http://localhost:5001/analytics")

if __name__ == '__main__':
    populate_sample_data()
