"""
Test script for conversational chat system
Tests multi-turn conversations and data entry
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.conversation import Conversation, ConversationMessage
from services.chat_service import ConversationalChatService
import json

def test_conversational_chat():
    """Test conversational chat with multi-turn data entry"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("🧪 TESTING CONVERSATIONAL CHAT SYSTEM")
        print("="*60 + "\n")
        
        # Initialize chat service
        chat_service = ConversationalChatService()
        
        # Test 1: Start a conversation to add a PO
        print("📝 Test 1: Adding PO through conversation")
        print("-" * 60)
        
        # First message: User wants to add a PO
        response1 = chat_service.process_message(
            user_message="Add a new PO for steel from ABC Suppliers, 50 tons, 80000 AED"
        )
        
        print(f"User: Add a new PO for steel from ABC Suppliers, 50 tons, 80000 AED")
        print(f"AI: {response1['answer']}")
        print(f"Intent: {response1.get('intent')}")
        print(f"Context: {json.dumps(response1.get('context_data', {}), indent=2)}")
        print()
        
        conversation_id = response1.get('conversation_id')
        
        # Second message: Provide PO number
        if conversation_id:
            response2 = chat_service.process_message(
                user_message="PO-12345",
                conversation_id=conversation_id
            )
            
            print(f"User: PO-12345")
            print(f"AI: {response2['answer']}")
            print(f"Context: {json.dumps(response2.get('context_data', {}), indent=2)}")
            print()
        
        # Test 2: Query data
        print("\n📊 Test 2: Querying data")
        print("-" * 60)
        
        response3 = chat_service.process_message(
            user_message="Show me all delayed deliveries"
        )
        
        print(f"User: Show me all delayed deliveries")
        print(f"AI: {response3['answer']}")
        if response3.get('data'):
            print(f"Data: {json.dumps(response3.get('data'), indent=2)}")
        print()
        
        # Test 3: Check conversation history
        print("\n💬 Test 3: Conversation history")
        print("-" * 60)
        
        conversations = Conversation.query.filter_by(status='active').all()
        print(f"Active conversations: {len(conversations)}")
        
        for conv in conversations[:3]:  # Show first 3
            messages = conv.get_messages()
            print(f"\nConversation {conv.conversation_id}:")
            print(f"  Intent: {conv.intent}")
            print(f"  Messages: {len(messages)}")
            print(f"  Status: {conv.status}")
            
            for msg in messages:
                print(f"    - {msg.role}: {msg.content[:50]}...")
        
        print("\n" + "="*60)
        print("✅ CONVERSATIONAL CHAT TESTS COMPLETE!")
        print("="*60 + "\n")

if __name__ == '__main__':
    test_conversational_chat()
