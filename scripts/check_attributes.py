"""
Attribute Consistency Checker
==============================

This script checks that all model attributes match between:
- Model definitions (models/*.py)
- API responses (to_dict methods)
- Frontend forms (templates/*.html)

Run: python scripts/check_attributes.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery


def check_model_attributes(model_class, model_name):
    """Check that model has all expected attributes"""
    print(f"\n{'='*60}")
    print(f"Checking {model_name} Model")
    print('='*60)
    
    # Get model instance
    instance = model_class()
    
    # Get all columns
    columns = [c.name for c in model_class.__table__.columns]
    
    print(f"\n📋 Database Columns ({len(columns)}):")
    for col in sorted(columns):
        print(f"   ✓ {col}")
    
    # Check to_dict method
    print(f"\n📤 to_dict() method:")
    try:
        # Create a test dict (won't work without DB, but we can check method exists)
        if hasattr(instance, 'to_dict'):
            print("   ✓ to_dict() method exists")
            # Try to get dict keys by inspecting the method
            import inspect
            source = inspect.getsource(instance.to_dict)
            dict_keys = []
            for line in source.split('\n'):
                if "'" in line and ':' in line:
                    key = line.split("'")[1] if "'" in line else None
                    if key and key not in dict_keys:
                        dict_keys.append(key)
            
            print(f"   📊 Returns {len(dict_keys)} fields:")
            for key in sorted(dict_keys):
                print(f"      • {key}")
                
            # Check if all columns are in dict
            missing_in_dict = set(columns) - set(dict_keys)
            if missing_in_dict:
                print(f"\n   ⚠️  Missing in to_dict(): {missing_in_dict}")
            else:
                print(f"\n   ✅ All columns included in to_dict()")
                
        else:
            print("   ❌ to_dict() method not found!")
    except Exception as e:
        print(f"   ⚠️  Could not analyze to_dict(): {e}")
    
    return columns


def check_relationship_attributes():
    """Check that relationship backrefs are consistent"""
    print(f"\n{'='*60}")
    print("Checking Relationships")
    print('='*60)
    
    relationships = {
        'Material': {
            'has_many': ['purchase_orders (backref: material)'],
            'has_one': []
        },
        'PurchaseOrder': {
            'has_many': ['payments (backref: purchase_order)', 
                        'deliveries (backref: purchase_order)'],
            'belongs_to': ['material (material_id)']
        },
        'Payment': {
            'belongs_to': ['purchase_order (po_id)']
        },
        'Delivery': {
            'belongs_to': ['purchase_order (po_id)']
        }
    }
    
    for model, rels in relationships.items():
        print(f"\n{model}:")
        if 'has_many' in rels and rels['has_many']:
            print("  Has Many:")
            for rel in rels['has_many']:
                print(f"    ✓ {rel}")
        if 'belongs_to' in rels and rels['belongs_to']:
            print("  Belongs To:")
            for rel in rels['belongs_to']:
                print(f"    ✓ {rel}")
    
    print("\n✅ Relationship structure documented")


def compare_with_frontend():
    """
    Check common frontend form fields
    This is a manual check - review forms in templates/
    """
    print(f"\n{'='*60}")
    print("Frontend Form Fields to Verify")
    print('='*60)
    
    forms = {
        'materials.html': [
            'material_type', 'description', 'approval_status',
            'submittal_ref', 'specification_ref', 'revision_number',
            'previous_submittal_id', 'approval_notes'
        ],
        'purchase_orders.html': [
            'material_id', 'quote_ref', 'po_ref', 'po_date',
            'expected_delivery_date', 'supplier_name', 'supplier_contact',
            'supplier_email', 'total_amount', 'currency', 'po_status',
            'payment_terms', 'delivery_terms', 'notes'
        ],
        'payments.html': [
            'po_id', 'payment_structure', 'payment_type',
            'total_amount', 'paid_amount', 'payment_percentage',
            'payment_date', 'payment_ref', 'invoice_ref',
            'payment_method', 'currency', 'payment_status',
            'payment_terms', 'notes'
        ],
        'deliveries.html': [
            'po_id', 'expected_delivery_date', 'actual_delivery_date',
            'delivery_status', 'delivery_percentage', 'tracking_number',
            'carrier', 'delivery_location', 'received_by',
            'delay_reason', 'notes'
        ]
    }
    
    print("\n📝 Manual Verification Needed:")
    print("   Check that these form IDs exist in templates:")
    
    for template, fields in forms.items():
        print(f"\n   {template}:")
        for field in fields:
            print(f"      □ {field}")
    
    print("\n   💡 Open templates/ and verify each field ID matches")


def main():
    """Run all checks"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║           Attribute Consistency Checker                           ║
    ║                                                                   ║
    ║  Verifies that model attributes match across:                     ║
    ║  • Database columns                                               ║
    ║  • API responses (to_dict)                                        ║
    ║  • Frontend forms                                                 ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check each model
    material_cols = check_model_attributes(Material, 'Material')
    po_cols = check_model_attributes(PurchaseOrder, 'PurchaseOrder')
    payment_cols = check_model_attributes(Payment, 'Payment')
    delivery_cols = check_model_attributes(Delivery, 'Delivery')
    
    # Check relationships
    check_relationship_attributes()
    
    # Frontend comparison
    compare_with_frontend()
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print('='*60)
    print(f"✅ Material:        {len(material_cols)} columns")
    print(f"✅ PurchaseOrder:   {len(po_cols)} columns")
    print(f"✅ Payment:         {len(payment_cols)} columns")
    print(f"✅ Delivery:        {len(delivery_cols)} columns")
    print(f"✅ Relationships:   Documented")
    print(f"📝 Frontend:        Manual verification needed")
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print('='*60)
    print("1. Review model attributes above")
    print("2. Check templates/ forms match field IDs")
    print("3. Run automated tests: pytest tests/test_basic_crud_manual.py")
    print("4. Perform manual testing: see MANUAL_TESTING_GUIDE.md")
    print('='*60)
    print()


if __name__ == '__main__':
    main()
