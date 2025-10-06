from flask import Blueprint, request, jsonify
from services.chat_service import ChatService, ConversationalChatService
from models.conversation import Conversation, ConversationMessage
from models import db
from models.file import File
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from models.payment import Payment
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import requests

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()
conversational_service = ConversationalChatService()

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')

def get_upload_path():
    """Get organized upload path by year/month"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    path = os.path.join(UPLOAD_FOLDER, year, month)
    os.makedirs(path, exist_ok=True)
    return path, f"{year}/{month}"

@chat_bp.route('', methods=['POST'])
def chat():
    """Handle natural language chat queries and conversational data entry"""
    try:
        data = request.get_json()
        message = data.get('message') or data.get('query')
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Use conversational service for multi-turn conversations
        response = conversational_service.process_message(
            user_message=message,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/upload', methods=['POST'])
def chat_upload():
    """Handle document uploads from chat interface - triggers n8n workflow for AI extraction"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        doc_type = request.form.get('doc_type', 'purchase_order')
        user_message = request.form.get('user_message', '')
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400
        
        # Create entity record first based on document type
        entity_id = None
        entity_record = None
        
        if doc_type == 'purchase_order':
            # Create new PO record
            new_po = PurchaseOrder(
                material_id=1,  # Default material
                po_ref=f"CHAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                supplier_name="Pending AI Extraction",
                total_amount=0,
                currency="AED",
                po_status="Draft",
                created_by="Chat Upload",
                created_at=datetime.utcnow()
            )
            db.session.add(new_po)
            db.session.flush()
            entity_id = new_po.id
            entity_record = new_po
            
        elif doc_type == 'delivery_note':
            # Create new delivery record
            new_delivery = Delivery(
                po_id=None,  # Will be linked by AI if PO ref found
                delivery_order_number=f"CHAT-DN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                tracking_number="Pending",
                carrier="Pending AI Extraction",
                delivery_status="Pending",
                extraction_status="pending",
                created_at=datetime.utcnow()
            )
            db.session.add(new_delivery)
            db.session.flush()
            entity_id = new_delivery.id
            entity_record = new_delivery
            
        elif doc_type == 'invoice':
            # Create new payment record
            new_payment = Payment(
                po_id=None,  # Will be linked by AI
                invoice_ref=f"CHAT-INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                payment_ref="Pending",
                total_amount=0,
                paid_amount=0,
                payment_status="Pending",
                created_at=datetime.utcnow()
            )
            db.session.add(new_payment)
            db.session.flush()
            entity_id = new_payment.id
            entity_record = new_payment
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"chat_{doc_type}_{entity_id}_{timestamp}_{filename}"
        
        # Get organized upload path
        upload_path, relative_path = get_upload_path()
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create File record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=os.path.join(relative_path, filename),
            file_size=file_size,
            file_type=file_ext,
            mime_type=file.content_type,
            processing_status='pending',
            uploaded_by='Chat Interface'
        )
        
        # Link file to entity
        if doc_type == 'purchase_order':
            file_record.purchase_order_id = entity_id
        elif doc_type == 'delivery_note':
            file_record.delivery_id = entity_id
        elif doc_type == 'invoice':
            file_record.payment_id = entity_id
        
        db.session.add(file_record)
        db.session.commit()
        
        # Trigger n8n workflow for AI extraction
        n8n_triggered = False
        try:
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk')
            n8n_api_key = os.getenv('N8N_API_KEY', '')
            
            file_url = f"http://localhost:5001/uploads/{filename}"
            
            webhook_payload = {
                'file_id': file_record.id,
                'file_url': file_url,
                'file_path': file_record.file_path,
                'document_context': doc_type,
                'user_message': user_message,
                'source': 'chat_interface'
            }
            
            # Add entity-specific fields
            if doc_type == 'purchase_order':
                webhook_payload['po_id'] = entity_id
                webhook_payload['po_ref'] = entity_record.po_ref
            elif doc_type == 'delivery_note':
                webhook_payload['delivery_id'] = entity_id
            elif doc_type == 'invoice':
                webhook_payload['payment_id'] = entity_id
            
            response = requests.post(
                f"{n8n_webhook_url}/webhook/extract-document",
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {n8n_api_key}'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                n8n_triggered = True
                print(f"✅ n8n document intelligence triggered from chat for {doc_type}")
            else:
                print(f"⚠️ n8n workflow trigger failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not trigger n8n workflow: {str(e)}")
        
        # Format success response
        doc_type_display = doc_type.replace('_', ' ').title()
        message = f"✅ {doc_type_display} uploaded successfully!\n\n"
        message += f"📋 Reference: {entity_record.po_ref if doc_type == 'purchase_order' else entity_record.delivery_order_number if doc_type == 'delivery_note' else entity_record.invoice_ref}\n"
        message += f"🤖 AI is processing your document...\n"
        message += f"📊 Data will be extracted automatically"
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'entity_id': entity_id,
                'file_id': file_record.id,
                'file_name': file.filename,
                'document_type': doc_type_display,
                'processing_status': 'pending',
                'n8n_triggered': n8n_triggered
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error processing document: {str(e)}'
        }), 500

@chat_bp.route('/simple', methods=['POST'])
def simple_chat():
    """Simple query endpoint without conversation tracking (backward compatible)"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process the query without conversation context
        response = chat_service.process_query(query)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all active conversations"""
    try:
        user_id = request.args.get('user_id')
        
        query = Conversation.query.filter_by(status='active')
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        conversations = query.order_by(Conversation.updated_at.desc()).limit(20).all()
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    try:
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        messages = conversation.get_messages()
        
        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({'message': 'Conversation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get chat history (alias for conversations endpoint)"""
    return get_conversations()
