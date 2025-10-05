#!/usr/bin/env python3
"""
Database Migration: Add expected_delivery_date to PurchaseOrder
Date: October 5, 2025
Purpose: Add expected delivery date field to capture delivery dates from PO documents
"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("🔧 Running migration: Add expected_delivery_date to purchase_orders...")
    
    try:
        # Add the new column
        with db.engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(db.text(
                "SELECT COUNT(*) FROM pragma_table_info('purchase_orders') WHERE name='expected_delivery_date'"
            ))
            exists = result.scalar() > 0
            
            if not exists:
                print("   Adding expected_delivery_date column...")
                conn.execute(db.text(
                    "ALTER TABLE purchase_orders ADD COLUMN expected_delivery_date DATETIME"
                ))
                conn.commit()
                print("   ✅ Column added successfully!")
            else:
                print("   ℹ️  Column already exists, skipping...")
        
        print("\n✅ Migration completed successfully!")
        print("=" * 60)
        print("PurchaseOrder model now has:")
        print("  - po_date (issue date)")
        print("  - expected_delivery_date (delivery date)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

print("\n🎉 All migrations complete!")
