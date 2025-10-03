from flask import Blueprint, request, jsonify
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()

@chat_bp.route('', methods=['POST'])
def chat():
    """Handle natural language chat queries"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process the query
        response = chat_service.process_query(query)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get chat history (optional - can be implemented with session storage)"""
    try:
        # This is a placeholder - you can implement session-based history
        return jsonify({
            'history': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
