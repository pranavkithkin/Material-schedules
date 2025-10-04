"""
Quick script to check what tables exist in the database
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
    if db_uri.startswith('sqlite:///'):
        return db_uri.replace('sqlite:///', '')
    return db_uri

db_path = get_db_path()
print(f"Database path from config: {db_path}")

# Check if instance folder exists
instance_path = os.path.join(parent_dir, 'instance', 'delivery_dashboard.db')
if os.path.exists(instance_path):
    print(f"Found database in instance folder: {instance_path}")
    print("Using instance database...")
    db_path = instance_path
else:
    print(f"Instance database not found, using: {db_path}")

if not os.path.exists(db_path):
    print(f"\n❌ Database file does not exist: {db_path}")
    print("\nYou need to initialize the database first.")
    print("Run: python init_db.py")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nFound {len(tables)} tables:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n{table_name}: {len(columns)} columns")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
