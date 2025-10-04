"""
Database Migration: Field Structure Update
Date: October 4, 2025
Purpose: Update Payment, Material, and Delivery models to reflect simplified tracking

Changes:
1. Payment Model:
   - ADD: payment_terms field (TEXT) - from PO reference
   - REMOVE: quantity, unit fields (not applicable to payments)
   
2. Material Model:
   - ADD: revision_number field (INTEGER, default 0)
   - ADD: previous_submittal_id field (INTEGER, FK to materials.id)
   - ADD: document_path field (VARCHAR 500)
   - REMOVE: quantity, unit fields (tracked at PO level, not material type level)
   
3. Delivery Model:
   - ADD: delivery_percentage field (FLOAT, default 0) - for partial deliveries
   - REMOVE: ordered_quantity, delivered_quantity, unit fields
   - UPDATE: delivery_status values to: Pending, Partial, Delivered, Rejected/Returned
"""

import sys
import os

# Add parent directory to Python path to import modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from flask import Flask
from config import Config
from models import db
from models.payment import Payment
from models.material import Material
from models.delivery import Delivery
from sqlalchemy import text

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

# Create app instance
app = create_app()

def backup_data():
    """Backup existing data before migration"""
    print("Backing up existing data...")
    
    with app.app_context():
        # Backup payments (no data loss, just adding field)
        payments = Payment.query.all()
        print(f"Found {len(payments)} payments to migrate")
        
        # Backup materials (will lose quantity/unit data - inform user)
        materials = Material.query.all()
        material_qty_data = []
        for m in materials:
            if hasattr(m, 'quantity') and m.quantity:
                material_qty_data.append({
                    'id': m.id,
                    'material_type': m.material_type,
                    'quantity': m.quantity,
                    'unit': m.unit
                })
        
        if material_qty_data:
            print(f"\n⚠️  WARNING: {len(material_qty_data)} materials have quantity data that will be removed:")
            for m in material_qty_data[:5]:  # Show first 5
                print(f"   - {m['material_type']}: {m['quantity']} {m['unit']}")
            if len(material_qty_data) > 5:
                print(f"   ... and {len(material_qty_data) - 5} more")
        
        # Backup deliveries (will lose quantity data - inform user)
        deliveries = Delivery.query.all()
        delivery_qty_data = []
        for d in deliveries:
            if hasattr(d, 'delivered_quantity') and d.delivered_quantity:
                delivery_qty_data.append({
                    'id': d.id,
                    'po_id': d.po_id,
                    'ordered_quantity': d.ordered_quantity,
                    'delivered_quantity': d.delivered_quantity,
                    'unit': d.unit
                })
        
        if delivery_qty_data:
            print(f"\n⚠️  WARNING: {len(delivery_qty_data)} deliveries have quantity data that will be removed:")
            for d in delivery_qty_data[:5]:  # Show first 5
                print(f"   - PO ID {d['po_id']}: {d['delivered_quantity']}/{d['ordered_quantity']} {d['unit']}")
            if len(delivery_qty_data) > 5:
                print(f"   ... and {len(delivery_qty_data) - 5} more")
        
        return material_qty_data, delivery_qty_data

def run_migration():
    """Run the database migration"""
    print("\n" + "="*60)
    print("DATABASE MIGRATION: Field Structure Update")
    print("="*60 + "\n")
    
    with app.app_context():
        # Backup data
        material_qty_data, delivery_qty_data = backup_data()
        
        # Ask for confirmation
        print("\nThis migration will:")
        print("✓ Add payment_terms to Payment model")
        print("✓ Add revision tracking to Material model")
        print("✓ Add document_path to Material model")
        print("✓ Add delivery_percentage to Delivery model")
        print("✗ Remove quantity/unit from Material model")
        print("✗ Remove quantity fields from Delivery model")
        
        if material_qty_data or delivery_qty_data:
            print("\n⚠️  DATA LOSS WARNING:")
            print(f"   - {len(material_qty_data)} material quantity records will be lost")
            print(f"   - {len(delivery_qty_data)} delivery quantity records will be lost")
            print("   (This data is now tracked at PO level, not individual records)")
        
        response = input("\nContinue with migration? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
        
        print("\nExecuting migration...")
        
        try:
            # Get connection
            connection = db.engine.connect()
            
            # 1. Add new columns to payments
            print("\n1. Updating Payment model...")
            try:
                connection.execute(text("""
                    ALTER TABLE payments 
                    ADD COLUMN payment_terms TEXT
                """))
                print("   ✓ Added payment_terms column")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("   ✓ payment_terms column already exists")
                else:
                    raise
            
            # 2. Update materials table
            print("\n2. Updating Material model...")
            
            # Add new columns
            try:
                connection.execute(text("""
                    ALTER TABLE materials 
                    ADD COLUMN revision_number INTEGER DEFAULT 0
                """))
                print("   ✓ Added revision_number column")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("   ✓ revision_number column already exists")
                else:
                    raise
            
            try:
                connection.execute(text("""
                    ALTER TABLE materials 
                    ADD COLUMN previous_submittal_id INTEGER
                """))
                connection.execute(text("""
                    ALTER TABLE materials 
                    ADD FOREIGN KEY (previous_submittal_id) REFERENCES materials(id)
                """))
                print("   ✓ Added previous_submittal_id column with FK")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("   ✓ previous_submittal_id column already exists")
                else:
                    raise
            
            try:
                connection.execute(text("""
                    ALTER TABLE materials 
                    ADD COLUMN document_path VARCHAR(500)
                """))
                print("   ✓ Added document_path column")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("   ✓ document_path column already exists")
                else:
                    raise
            
            # Remove old columns (SQLite doesn't support DROP COLUMN easily, so we note it)
            print("   ⚠️  Note: quantity and unit columns still exist in database")
            print("      They are removed from the model and won't be used")
            print("      Run VACUUM to reclaim space if needed")
            
            # 3. Update deliveries table
            print("\n3. Updating Delivery model...")
            
            try:
                connection.execute(text("""
                    ALTER TABLE deliveries 
                    ADD COLUMN delivery_percentage FLOAT DEFAULT 0
                """))
                print("   ✓ Added delivery_percentage column")
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("   ✓ delivery_percentage column already exists")
                else:
                    raise
            
            print("   ⚠️  Note: ordered_quantity, delivered_quantity, unit columns still exist")
            print("      They are removed from the model and won't be used")
            
            # Commit changes
            connection.commit()
            connection.close()
            
            print("\n" + "="*60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("="*60)
            print("\nNext steps:")
            print("1. Restart the application")
            print("2. Test all forms with the new field structure")
            print("3. Update any existing records if needed")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            print("Database may be in inconsistent state. Please check and restore backup if needed.")
            raise

if __name__ == '__main__':
    run_migration()
