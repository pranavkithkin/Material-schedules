"""
Database migration script to create LPO tables
Run this after creating the models to add the tables to the database
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.lpo import LPO, LPOHistory

def create_lpo_tables():
    """Create LPO and LPOHistory tables"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        print("Creating LPO tables...")
        db.create_all()
        print("✓ LPO tables created successfully!")
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'lpos' in tables:
            print("✓ Table 'lpos' exists")
        else:
            print("✗ Table 'lpos' not found")
        
        if 'lpo_history' in tables:
            print("✓ Table 'lpo_history' exists")
        else:
            print("✗ Table 'lpo_history' not found")
        
        print("\nDatabase migration complete!")

if __name__ == '__main__':
    create_lpo_tables()
