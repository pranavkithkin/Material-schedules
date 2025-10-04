"""
Sprint 2 Database Migration: Document Intelligence Fields
Date: October 4, 2025
Purpose: Add fields for document extraction and AI processing
"""

import sys
import os
import sqlite3

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import Config

def get_db_path():
    """Get database path from config"""
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    if db_uri.startswith('sqlite:///'):
        path = db_uri.replace('sqlite:///', '')
        # Check for instance folder
        instance_path = os.path.join(parent_dir, 'instance', 'delivery_dashboard.db')
        if os.path.exists(instance_path):
            return instance_path
        return path
    return db_uri

def run_migration():
    """Add document intelligence fields to Delivery model"""
    print("\n" + "="*60)
    print("SPRINT 2 DATABASE MIGRATION")
    print("Adding Document Intelligence Fields")
    print("="*60 + "\n")
    
    db_path = get_db_path()
    print(f"Database: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding new fields to deliveries table...\n")
        
        # 1. extracted_data (JSON) - Store full extracted data
        try:
            cursor.execute("ALTER TABLE deliveries ADD COLUMN extracted_data JSON")
            print("   ✓ Added: extracted_data (JSON)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ extracted_data already exists")
            else:
                raise
        
        # 2. extraction_status (String) - pending, processing, completed, failed
        try:
            cursor.execute("ALTER TABLE deliveries ADD COLUMN extraction_status VARCHAR(50) DEFAULT 'pending'")
            print("   ✓ Added: extraction_status (VARCHAR 50)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ extraction_status already exists")
            else:
                raise
        
        # 3. extraction_date (DateTime) - When extraction completed
        try:
            cursor.execute("ALTER TABLE deliveries ADD COLUMN extraction_date DATETIME")
            print("   ✓ Added: extraction_date (DATETIME)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ extraction_date already exists")
            else:
                raise
        
        # 4. extraction_confidence (Float) - AI confidence score 0-100
        try:
            cursor.execute("ALTER TABLE deliveries ADD COLUMN extraction_confidence FLOAT")
            print("   ✓ Added: extraction_confidence (FLOAT)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ extraction_confidence already exists")
            else:
                raise
        
        # 5. extracted_item_count (Integer) - Number of items extracted
        try:
            cursor.execute("ALTER TABLE deliveries ADD COLUMN extracted_item_count INTEGER DEFAULT 0")
            print("   ✓ Added: extracted_item_count (INTEGER)")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ extracted_item_count already exists")
            else:
                raise
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*60)
        print("✓ Migration Completed Successfully!")
        print("="*60)
        
        print("\n📋 New Fields Added:")
        print("   • extracted_data (JSON) - Full extraction results")
        print("   • extraction_status (VARCHAR) - pending/processing/completed/failed")
        print("   • extraction_date (DATETIME) - Completion timestamp")
        print("   • extraction_confidence (FLOAT) - AI confidence 0-100%")
        print("   • extracted_item_count (INTEGER) - Number of items found")
        
        print("\n🎯 Ready for:")
        print("   ✓ Document upload")
        print("   ✓ n8n workflow integration")
        print("   ✓ Claude API extraction")
        print("   ✓ Chatbot queries")
        
        print("\n📌 Next Steps:")
        print("   1. Update Delivery model in models/delivery.py")
        print("   2. Add file upload field to deliveries form")
        print("   3. Create extraction API endpoints")
        print("   4. Set up n8n workflow\n")
        
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
