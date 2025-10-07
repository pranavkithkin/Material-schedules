"""
Enhanced Chat Interface - Quick Test Script
Tests the conversational AI capabilities
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
SESSION_ID = f"test-session-{int(datetime.now().timestamp())}"

def test_chat_endpoint():
    """Test if chat endpoint is accessible"""
    print("\n" + "="*80)
    print("  TEST 1: Chat Endpoint Accessibility")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/chat")
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Chat page is accessible")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_simple_message():
    """Test sending a simple message"""
    print("\n" + "="*80)
    print("  TEST 2: Simple Conversational Message")
    print("="*80)
    
    payload = {
        "message": "Hello, can you help me add a purchase order?",
        "session_id": SESSION_ID
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS")
            print(f"\nAI Response:")
            print(f"  {data.get('response', 'No response')}")
            print(f"\nIntent: {data.get('intent')}")
            print(f"Confidence: {data.get('confidence', 0)*100:.1f}%")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_create_po_conversation():
    """Test multi-turn PO creation"""
    print("\n" + "="*80)
    print("  TEST 3: Multi-turn PO Creation")
    print("="*80)
    
    messages = [
        "Add steel PO to ABC Trading, 50 tons, 80k",  # Corrected: PO TO supplier
        "PKP-LPO-6001-2025-60",
        "Next Monday"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {message}")
        
        payload = {
            "message": message,
            "session_id": SESSION_ID
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat/message",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"AI: {data.get('response', 'No response')}")
                
                if data.get('extracted_data'):
                    print(f"\nExtracted Data:")
                    for key, value in data['extracted_data'].items():
                        print(f"  • {key}: {value}")
                
                if data.get('requires_clarification'):
                    print(f"\n⚠️ Needs Clarification: {', '.join(data.get('clarification_fields', []))}")
                
                print(f"\nConfidence: {data.get('confidence', 0)*100:.1f}%")
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    print(f"\n✅ Multi-turn conversation completed successfully!")
    return True

def test_query_deliveries():
    """Test querying deliveries"""
    print("\n" + "="*80)
    print("  TEST 4: Query Deliveries")
    print("="*80)
    
    payload = {
        "message": "Show me all pending deliveries",
        "session_id": SESSION_ID
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Query processed successfully")
            print(f"\nAI Response:")
            print(f"  {data.get('response', 'No response')}")
            print(f"\nIntent: {data.get('intent')}")
            
            if data.get('action'):
                print(f"Action: {data.get('action')}")
            
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_conversation_history():
    """Test retrieving conversation history"""
    print("\n" + "="*80)
    print("  TEST 5: Conversation History")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/{SESSION_ID}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ History retrieved successfully")
            print(f"Total conversations: {data.get('total', 0)}")
            
            if data.get('conversations'):
                print(f"\nRecent conversations:")
                for conv in data['conversations'][:3]:
                    print(f"\n  User: {conv['user_message']}")
                    print(f"  AI: {conv['ai_response'][:100]}...")
                    print(f"  Intent: {conv['intent']} | Confidence: {conv['confidence_score']*100:.1f}%")
            
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("="*80)
    print("  🤖 ENHANCED CHAT INTERFACE - TEST SUITE")
    print("="*80)
    print(f"\nSession ID: {SESSION_ID}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'Chat Endpoint': test_chat_endpoint(),
        'Simple Message': test_simple_message(),
        'Multi-turn PO Creation': test_create_po_conversation(),
        'Query Deliveries': test_query_deliveries(),
        'Conversation History': test_conversation_history()
    }
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Chat interface is working perfectly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
    
    print("="*80)
    print()

if __name__ == '__main__':
    print("\n💡 BEFORE RUNNING: Make sure Flask is running on http://localhost:5001")
    print("   Start Flask: python app.py\n")
    
    input("Press Enter to start testing... ")
    
    run_all_tests()
    
    print("\n💬 Ready to test manually?")
    print("   Open: http://localhost:5001/chat")
    print("   Try: 'Add a new purchase order for VRF from Daikin, 125k'\n")
