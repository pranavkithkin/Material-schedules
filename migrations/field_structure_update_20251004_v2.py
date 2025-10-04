"""
Database Migration: Field Structure Update v2
Date: October 4, 2025
Purpose: Update Payment, Material, and Delivery models using raw SQL

Changes:
1. Payment Model:
   - ADD: payment_terms field (TEXT)
   
2. Material Model:
   - ADD: revision_number field (INTEGER, default 0)
   - ADD: previous_submittal_id field (INTEGER, FK to materials.id)
   - REMOVE: quantity, unit fields (if they exist)
   
3. Delivery Model:
   - ADD: delivery_percentage field (FLOAT, default 0)
   - REMOVE: ordered_quantity, delivered_quantity, unit fields (if they exist)
"""

import sys
import os
import sqlite3

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import Config

def get_db_path():
    """Get database path from config"""
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    # Remove 'sqlite:///' prefix
    if db_uri.startswith('sqlite:///'):
        return db_uri.replace('sqlite:///', '')
    return db_uri

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def run_migration():
    """Run the database migration using raw SQL"""
    print("\n" + "="*60)
    print("DATABASE MIGRATION: Field Structure Update v2")
    print("="*60 + "\n")
    
    db_path = get_db_path()
    print(f"Database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n1. Updating PAYMENTS table...")
        
        # Add payment_terms if it doesn't exist
        if not check_column_exists(cursor, 'payments', 'payment_terms'):
            cursor.execute("ALTER TABLE payments ADD COLUMN payment_terms TEXT")
            print("   ✓ Added payment_terms column")
        else:
            print("   ℹ payment_terms column already exists")
        
        # Remove quantity and unit if they exist
        if check_column_exists(cursor, 'payments', 'quantity'):
            print("   ⚠️  Found quantity column in payments (will be removed in table recreation)")
        if check_column_exists(cursor, 'payments', 'unit'):
            print("   ⚠️  Found unit column in payments (will be removed in table recreation)")
        
        print("\n2. Updating MATERIALS table...")
        
        # Add revision_number if it doesn't exist
        if not check_column_exists(cursor, 'materials', 'revision_number'):
            cursor.execute("ALTER TABLE materials ADD COLUMN revision_number INTEGER DEFAULT 0")
            print("   ✓ Added revision_number column")
        else:
            print("   ℹ revision_number column already exists")
        
        # Add previous_submittal_id if it doesn't exist
        if not check_column_exists(cursor, 'materials', 'previous_submittal_id'):
            cursor.execute("ALTER TABLE materials ADD COLUMN previous_submittal_id INTEGER")
            print("   ✓ Added previous_submittal_id column")
        else:
            print("   ℹ previous_submittal_id column already exists")
        
        # Check for quantity/unit fields
        if check_column_exists(cursor, 'materials', 'quantity'):
            print("   ⚠️  Found quantity column in materials (will be removed in table recreation)")
        if check_column_exists(cursor, 'materials', 'unit'):
            print("   ⚠️  Found unit column in materials (will be removed in table recreation)")
        
        print("\n3. Updating DELIVERIES table...")
        
        # Add delivery_percentage if it doesn't exist
        if not check_column_exists(cursor, 'deliveries', 'delivery_percentage'):
            cursor.execute("ALTER TABLE deliveries ADD COLUMN delivery_percentage FLOAT DEFAULT 0")
            print("   ✓ Added delivery_percentage column")
        else:
            print("   ℹ delivery_percentage column already exists")
        
        # Check for quantity fields
        if check_column_exists(cursor, 'deliveries', 'ordered_quantity'):
            print("   ⚠️  Found ordered_quantity column (will be removed in table recreation)")
        if check_column_exists(cursor, 'deliveries', 'delivered_quantity'):
            print("   ⚠️  Found delivered_quantity column (will be removed in table recreation)")
        if check_column_exists(cursor, 'deliveries', 'unit'):
            print("   ⚠️  Found unit column (will be removed in table recreation)")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60)
        
        print("\n⚠️  IMPORTANT NOTES:")
        print("1. New columns added: payment_terms, revision_number, previous_submittal_id, delivery_percentage")
        print("2. To remove old columns (quantity, unit), you need to recreate tables")
        print("3. SQLite doesn't support DROP COLUMN, so old columns remain but are unused")
        print("4. The updated models will ignore the old columns")
        print("5. For a clean schema, export data, drop tables, and recreate")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        run_migration()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
