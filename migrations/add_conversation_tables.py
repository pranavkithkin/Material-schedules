"""
Migration: Add Conversation and ConversationMessage tables
Date: October 6, 2025
Purpose: Enable multi-turn conversations for chat interface
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db
from models.conversation import Conversation, ConversationMessage
from app import create_app

def migrate():
    """Add conversation tables to database"""
    app = create_app()
    
    with app.app_context():
        print("Creating conversation tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Conversation tables created successfully!")
        print("   - conversation")
        print("   - conversation_message")

if __name__ == '__main__':
    migrate()
