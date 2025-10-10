"""
n8n Webhook Routes
API endpoints for n8n automation workflows
All endpoints require API key authentication
"""

from flask import Blueprint, request, jsonify, send_file
from models import db
from models.ai_suggestion import AISuggestion
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from models.payment import Payment
from models.file import File
from routes.auth import require_api_key
from datetime import datetime
import json
import os
import PyPDF2
import io

n8n_bp = Blueprint('n8n', __name__)


@n8n_bp.route('/ai-suggestion', methods=['POST'])
@require_api_key
def receive_ai_suggestion():
    """
    Receive AI-extracted data from n8n workflow.
    
    Expected JSON body:
    {
        "material_id": 1,
        "source": "email",
        "suggestion_type": "purchase_order",
        "extracted_data": {
            "po_number": "PO-2024-001",
            "supplier": "ABC Materials",
            "amount": 50000.00,
            ...
        },
        "confidence_score": 85.5,
        "ai_reasoning": "Extracted from email attachment...",
        "metadata": {
            "email_from": "supplier@example.com",
            "email_subject": "PO Confirmation",
            "file_name": "PO-2024-001.pdf"
        }
    }
    
    Returns:
        201: Suggestion created successfully
        400: Invalid request data
        500: Server error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['source', 'suggestion_type', 'extracted_data', 'confidence_score']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Create AI suggestion
        suggestion = AISuggestion(
            material_id=data.get('material_id'),
            source=data['source'],
            suggestion_type=data['suggestion_type'],
            extracted_data=data['extracted_data'],
            confidence_score=data['confidence_score'],
            status='pending',
            ai_reasoning=data.get('ai_reasoning', ''),
            created_by='AI'
        )
        
        db.session.add(suggestion)
        db.session.commit()
        
        # Build response with action recommendation
        action = 'auto_approve' if suggestion.confidence_score >= 90 else 'manual_review'
        
        return jsonify({
            'success': True,
            'message': 'AI suggestion created successfully',
            'suggestion_id': suggestion.id,
            'action': action,
            'confidence_score': suggestion.confidence_score,
            'requires_review': suggestion.confidence_score < 90
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create AI suggestion',
            'message': str(e)
        }), 500


@n8n_bp.route('/conversation', methods=['POST'])
@require_api_key
def store_conversation():
    """
    Store conversation messages from n8n chat workflows.
    
    Expected JSON body:
    {
        "conversation_id": "conv-123",
        "user_message": "When is cement delivery?",
        "ai_response": "The cement delivery is scheduled for Oct 5, 2025",
        "context": {
            "material_id": 5,
            "query_type": "delivery_status"
        }
    }
    
    Returns:
        200: Message stored successfully
        400: Invalid request data
    """
    try:
        data = request.get_json()
        
        # For now, just acknowledge receipt
        # TODO: Create Conversation model to store chat history
        
        return jsonify({
            'success': True,
            'message': 'Conversation stored',
            'conversation_id': data.get('conversation_id')
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to store conversation',
            'message': str(e)
        }), 500


@n8n_bp.route('/clarification', methods=['POST'])
@require_api_key
def handle_clarification():
    """
    Handle clarification responses from users via n8n.
    
    Expected JSON body:
    {
        "suggestion_id": 123,
        "clarifications": {
            "supplier_email": "supplier@example.com",
            "delivery_date": "2025-10-15"
        },
        "ready_to_create": true
    }
    
    Returns:
        200: Clarification processed
        404: Suggestion not found
        400: Invalid data
    """
    try:
        data = request.get_json()
        
        suggestion_id = data.get('suggestion_id')
        if not suggestion_id:
            return jsonify({
                'error': 'Missing suggestion_id'
            }), 400
        
        # Find the suggestion
        suggestion = AISuggestion.query.get(suggestion_id)
        if not suggestion:
            return jsonify({
                'error': 'Suggestion not found'
            }), 404
        
        # Update extracted data with clarifications
        clarifications = data.get('clarifications', {})
        updated_data = {**suggestion.extracted_data, **clarifications}
        
        suggestion.extracted_data = updated_data
        suggestion.status = 'clarified'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Clarifications applied',
            'suggestion_id': suggestion.id,
            'updated_data': updated_data,
            'ready_to_create': data.get('ready_to_create', False)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to process clarification',
            'message': str(e)
        }), 500


@n8n_bp.route('/file-processed', methods=['POST'])
@require_api_key
def file_processed_notification():
    """
    Receive notification when n8n finishes processing a file.
    
    Expected JSON body:
    {
        "file_id": 123,
        "status": "completed",
        "processing_result": {
            "suggestions_created": 2,
            "confidence_avg": 87.5
        }
    }
    
    Returns:
        200: Notification received
    """
    try:
        data = request.get_json()
        
        # TODO: Update File model with processing status
        # For now, just acknowledge
        
        return jsonify({
            'success': True,
            'message': 'File processing notification received',
            'file_id': data.get('file_id')
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to process notification',
            'message': str(e)
        }), 500


@n8n_bp.route('/pending-reviews', methods=['GET'])
@require_api_key
def get_pending_reviews():
    """
    Get list of AI suggestions pending manual review.
    Used by n8n to send review reminders.
    
    Query parameters:
        - confidence_max: Maximum confidence score (default: 90)
        - limit: Number of results (default: 50)
    
    Returns:
        200: List of pending suggestions
    """
    try:
        confidence_max = request.args.get('confidence_max', 90, type=float)
        limit = request.args.get('limit', 50, type=int)
        
        # Query pending suggestions below confidence threshold
        suggestions = AISuggestion.query.filter(
            AISuggestion.status == 'pending',
            AISuggestion.confidence_score < confidence_max
        ).order_by(AISuggestion.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(suggestions),
            'pending_reviews': [s.to_dict() for s in suggestions]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch pending reviews',
            'message': str(e)
        }), 500


@n8n_bp.route('/stats', methods=['GET'])
@require_api_key
def get_n8n_stats():
    """
    Get statistics for n8n monitoring dashboard.
    
    Returns:
        200: Statistics data
    """
    try:
        from sqlalchemy import func
        
        # AI Suggestions stats
        total_suggestions = AISuggestion.query.count()
        pending_suggestions = AISuggestion.query.filter_by(status='pending').count()
        approved_suggestions = AISuggestion.query.filter_by(status='approved').count()
        
        # Average confidence by status
        avg_confidence = db.session.query(
            func.avg(AISuggestion.confidence_score)
        ).scalar() or 0
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_suggestions = AISuggestion.query.filter(
            AISuggestion.created_at >= yesterday
        ).count()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_suggestions': total_suggestions,
                'pending_review': pending_suggestions,
                'approved': approved_suggestions,
                'average_confidence': round(avg_confidence, 2),
                'last_24h': recent_suggestions
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch statistics',
            'message': str(e)
        }), 500


@n8n_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (no authentication required).
    Used by n8n to verify API is accessible.
    
    Returns:
        200: API is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Material Delivery Dashboard API',
        'timestamp': datetime.now().isoformat()
    }), 200


@n8n_bp.route('/delivery-extraction', methods=['POST'])
@require_api_key  
def receive_delivery_extraction():
    """
    Sprint 2: Receive extracted delivery data from n8n + Claude API workflow.
    Enhanced with confidence-based validation - only auto-saves if confidence ≥ 90%
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['delivery_id', 'extraction_status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Get delivery record
        delivery = Delivery.query.get_or_404(data['delivery_id'])
        
        # Get confidence score (default to 0 if not provided)
        confidence_score = data.get('extraction_confidence', 0)
        
        # Update delivery extraction status
        delivery.extraction_status = data['extraction_status']
        delivery.extraction_date = datetime.utcnow()
        
        if 'extracted_data' in data and data['extracted_data']:
            extracted = data['extracted_data']
            delivery.extracted_data = extracted
            
            # Check if confidence is HIGH (≥ 90%) - auto-apply
            if confidence_score >= 90:
                # HIGH CONFIDENCE - Auto-apply changes
                
                # Map extracted fields to delivery fields
                if 'dn_number' in extracted:
                    delivery.dn_ref = extracted['dn_number']
                if 'supplier' in extracted:
                    delivery.supplier = extracted['supplier']
                if 'buyer' in extracted:
                    delivery.buyer = extracted['buyer']
                if 'delivery_date' in extracted:
                    try:
                        delivery.delivery_date = datetime.strptime(extracted['delivery_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                if 'received_date' in extracted:
                    try:
                        delivery.received_date = datetime.strptime(extracted['received_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                
                delivery.extraction_confidence = confidence_score
                delivery.updated_at = datetime.utcnow()
                delivery.updated_by = 'AI (Auto)'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'auto_applied',
                    'message': f'High confidence ({confidence_score}%) - Changes applied automatically',
                    'delivery_id': delivery.id,
                    'extraction_confidence': confidence_score
                }), 200
                
            else:
                # LOW CONFIDENCE (< 90%) - Create AI Suggestion for manual review
                
                suggestion = AISuggestion(
                    target_table='deliveries',
                    target_id=delivery.id,
                    action_type='update',
                    ai_model='Claude via n8n',
                    confidence_score=confidence_score,
                    extraction_source='document_upload',
                    source_document_path=data.get('document_path'),
                    ai_reasoning=f"Extracted from delivery note. Confidence: {confidence_score}%. Please review fields - values like '{extracted.get('buyer', 'N/A')}' may be incorrect."
                )
                
                # Set suggested data using the proper method
                suggestion.set_suggested_data({
                    'dn_ref': extracted.get('dn_number'),
                    'supplier': extracted.get('supplier'),
                    'buyer': extracted.get('buyer'),
                    'delivery_date': extracted.get('delivery_date'),
                    'received_date': extracted.get('received_date'),
                    'items': extracted.get('items', [])
                })
                
                # Set current data for comparison
                suggestion.set_current_data({
                    'dn_ref': delivery.dn_ref,
                    'supplier': delivery.supplier,
                    'buyer': delivery.buyer,
                    'delivery_date': str(delivery.delivery_date) if delivery.delivery_date else None,
                    'received_date': str(delivery.received_date) if delivery.received_date else None
                })
                
                db.session.add(suggestion)
                
                # Mark delivery as needing review
                delivery.extraction_confidence = confidence_score
                delivery.extraction_status = 'needs_review'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'suggestion_created',
                    'message': f'Low confidence ({confidence_score}%) - Created AI suggestion for manual review',
                    'delivery_id': delivery.id,
                    'suggestion_id': suggestion.id,
                    'extraction_confidence': confidence_score,
                    'requires_review': True,
                    'reason': 'Confidence below 90% threshold - please verify extracted values'
                }), 200
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Extraction data received',
            'delivery_id': delivery.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save extraction data',
            'message': str(e)
        }), 500


@n8n_bp.route('/files/<int:file_id>', methods=['GET'])
@require_api_key
def get_file_for_n8n(file_id):
    """
    Get file metadata for n8n workflows.
    Used by n8n to fetch file details before processing.
    
    Returns:
        200: File metadata with download URL
        404: File not found
    """
    try:
        file = File.query.get_or_404(file_id)
        
        # Build full file URL for n8n to download
        from flask import url_for
        download_url = url_for('uploads.download_file', filename=file.filename, _external=True)
        
        return jsonify({
            'success': True,
            'file': {
                **file.to_dict(),
                'download_url': download_url,
                'full_path': os.path.join('static/uploads', file.file_path)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'File not found',
            'message': str(e)
        }), 404


@n8n_bp.route('/files/<int:file_id>/download', methods=['GET'])
@require_api_key
def download_file_for_n8n(file_id):
    """
    Download file directly for n8n processing.
    Returns the actual file binary for n8n to process.
    
    Returns:
        200: File binary
        404: File not found
    """
    try:
        file = File.query.get_or_404(file_id)
        
        # Build full path
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        full_path = os.path.join(upload_folder, file.file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        return send_file(
            full_path,
            mimetype=file.mime_type,
            as_attachment=True,
            download_name=file.original_filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@n8n_bp.route('/extract-pdf-text', methods=['POST'])
@require_api_key
def extract_pdf_text():
    """
    Extract text from PDF file sent as base64.
    Used by n8n to extract text from PDF documents.
    
    Request body:
        {
            "file_data": "base64_encoded_pdf_data",
            "file_id": 1 (optional)
        }
    
    Returns:
        200: {
            "success": true,
            "text": "extracted text",
            "num_pages": 5
        }
        400: Invalid request
    """
    try:
        data = request.get_json()
        
        if not data or 'file_data' not in data:
            return jsonify({
                'error': 'Missing file_data in request body',
                'message': 'Please provide base64 encoded PDF data in file_data field'
            }), 400
        
        # Get base64 data
        import base64
        file_data = data['file_data']
        
        # Decode base64 to bytes
        pdf_bytes = base64.b64decode(file_data)
        
        # Create file-like object
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Extract text using PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        extracted_text = ""
        num_pages = len(pdf_reader.pages)
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text() + "\n\n"
        
        return jsonify({
            'success': True,
            'text': extracted_text.strip(),
            'num_pages': num_pages,
            'file_id': data.get('file_id')
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to extract PDF text',
            'message': str(e)
        }), 500


@n8n_bp.route('/extract-pdf-from-file/<int:file_id>', methods=['GET'])
@require_api_key
def extract_pdf_from_file_id(file_id):
    """
    Extract text from PDF file by file ID.
    Simpler endpoint that n8n can call directly after fetching file.
    
    This endpoint:
    1. Gets the file from database
    2. Reads it from disk
    3. Extracts text
    4. Returns the text
    
    URL Parameters:
        file_id: The database ID of the file to extract
    
    Returns:
        200: {
            "success": true,
            "text": "extracted text",
            "num_pages": 5,
            "file_id": 1
        }
        404: File not found
        500: Extraction error
    """
    try:
        # Get file from database
        file = File.query.get_or_404(file_id)
        
        # Build full path
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        full_path = os.path.join(upload_folder, file.file_path)
        
        if not os.path.exists(full_path):
            return jsonify({
                'error': 'File not found on disk',
                'file_path': file.file_path
            }), 404
        
        # Read PDF file
        with open(full_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            extracted_text = ""
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                extracted_text += page.extract_text() + "\n\n"
        
        return jsonify({
            'success': True,
            'text': extracted_text.strip(),
            'num_pages': num_pages,
            'file_id': file_id,
            'filename': file.original_filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to extract PDF text',
            'message': str(e)
        }), 500


@n8n_bp.route('/po-extraction', methods=['POST'])
@require_api_key
def receive_po_extraction():
    """
    Sprint 2: Receive extracted PO data from n8n + Claude API workflow.
    Enhanced with confidence-based validation - only auto-saves if confidence ≥ 90%
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['po_id', 'extraction_status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Get PO record
        po = PurchaseOrder.query.get_or_404(data['po_id'])
        
        # Get confidence score (default to 0 if not provided)
        confidence_score = data.get('extraction_confidence', 0)
        
        # Update PO extraction status
        po.extraction_status = data['extraction_status']
        po.extraction_date = datetime.utcnow()
        
        if 'extracted_data' in data and data['extracted_data']:
            extracted = data['extracted_data']
            po.extracted_data = extracted
            
            # Check if confidence is HIGH (≥ 90%) - auto-apply
            if confidence_score >= 90:
                # HIGH CONFIDENCE - Auto-apply changes
                
                # Map extracted fields to PO fields
                if 'po_number' in extracted:
                    po.po_number = extracted['po_number']
                if 'po_description' in extracted:
                    po.description = extracted['po_description']
                if 'supplier' in extracted:
                    po.supplier = extracted['supplier']
                if 'po_date' in extracted:
                    try:
                        po.po_date = datetime.strptime(extracted['po_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                if 'delivery_date' in extracted:
                    try:
                        po.delivery_date = datetime.strptime(extracted['delivery_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                if 'total_amount' in extracted:
                    try:
                        po.total_amount = float(extracted['total_amount'])
                    except (ValueError, TypeError):
                        pass
                
                po.extraction_confidence = confidence_score
                po.updated_at = datetime.utcnow()
                po.updated_by = 'AI (Auto)'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'auto_applied',
                    'message': f'High confidence ({confidence_score}%) - Changes applied automatically',
                    'po_id': po.id,
                    'extraction_confidence': confidence_score
                }), 200
                
            else:
                # LOW CONFIDENCE (< 90%) - Create AI Suggestion for manual review
                
                suggestion = AISuggestion(
                    target_table='purchase_orders',
                    target_id=po.id,
                    action_type='update',
                    ai_model='Claude via n8n',
                    confidence_score=confidence_score,
                    extraction_source='document_upload',
                    source_document_path=data.get('document_path'),
                    ai_reasoning=f"Extracted from PO document. Confidence: {confidence_score}%. Please review fields - some values may need verification."
                )
                
                # Set suggested data using the proper method
                suggestion.set_suggested_data({
                    'po_number': extracted.get('po_number'),
                    'description': extracted.get('po_description'),
                    'supplier': extracted.get('supplier'),
                    'po_date': extracted.get('po_date'),
                    'delivery_date': extracted.get('delivery_date'),
                    'total_amount': extracted.get('total_amount'),
                    'items': extracted.get('items', [])
                })
                
                # Set current data for comparison
                suggestion.set_current_data({
                    'po_number': po.po_number,
                    'description': po.description,
                    'supplier': po.supplier,
                    'po_date': str(po.po_date) if po.po_date else None,
                    'delivery_date': str(po.delivery_date) if po.delivery_date else None,
                    'total_amount': po.total_amount
                })
                
                db.session.add(suggestion)
                
                # Mark PO as needing review
                po.extraction_confidence = confidence_score
                po.extraction_status = 'needs_review'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'suggestion_created',
                    'message': f'Low confidence ({confidence_score}%) - Created AI suggestion for manual review',
                    'po_id': po.id,
                    'suggestion_id': suggestion.id,
                    'extraction_confidence': confidence_score,
                    'requires_review': True,
                    'reason': 'Confidence below 90% threshold - please verify extracted values'
                }), 200
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Extraction data received',
            'po_id': po.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save extraction data',
            'message': str(e)
        }), 500


def _map_material_type_to_id(material_type_str):
    """
    Map AI-detected material type string to database material ID.
    Handles various naming formats and returns the best match.
    
    Args:
        material_type_str: String from AI (e.g., "Distribution Board (DB)", "Sanitary Wares", "VRF")
    
    Returns:
        int: Material ID or None if no match found
    """
    if not material_type_str:
        return None
    
    # Normalize the string
    material_lower = material_type_str.lower()
    
    # Material mapping dictionary (keyword -> material_type in database)
    material_mappings = {
        'db': 'DB',
        'distribution board': 'DB',
        'panel': 'DB',
        'switchboard': 'DB',
        'electrical panel': 'DB',
        
        'vrf': 'VRF',
        'air conditioning': 'VRF',
        'ac unit': 'VRF',
        'hvac': 'VRF',
        'cooling': 'VRF',
        
        'cable': 'Cables',
        'wire': 'Cables',
        'conductor': 'Cables',
        
        'sanitary': 'Sanitary Wares',
        'bathroom': 'Sanitary Wares',
        'bathtub': 'Sanitary Wares',
        'shower': 'Sanitary Wares',
        'basin': 'Sanitary Wares',
        'toilet': 'Sanitary Wares',
        'wc': 'Sanitary Wares',
        'mixer': 'Sanitary Wares',
        'tap': 'Sanitary Wares',
        'faucet': 'Sanitary Wares',
        
        'fire': 'Fire Fighting',
        'sprinkler': 'Fire Fighting',
        'fire fighting': 'Fire Fighting',
        
        'plumbing': 'Plumbing',
        'pipe': 'Plumbing',
        'fitting': 'Plumbing',
        'valve': 'Plumbing',
        
        'light': 'Lighting',
        'lighting': 'Lighting',
        'lamp': 'Lighting',
        'led': 'Lighting',
    }
    
    # Find matching material type
    matched_material_type = None
    for keyword, mat_type in material_mappings.items():
        if keyword in material_lower:
            matched_material_type = mat_type
            break
    
    if not matched_material_type:
        return None
    
    # Look up material in database
    material = Material.query.filter_by(material_type=matched_material_type).first()
    return material.id if material else None


@n8n_bp.route('/invoice-extraction', methods=['POST'])
@require_api_key
def receive_invoice_extraction():
    """
    Sprint 2: Receive extracted invoice data from n8n + Claude API workflow.
    Enhanced with confidence-based validation - only auto-saves if confidence ≥ 90%
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_id', 'extraction_status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Get payment record
        payment = Payment.query.get_or_404(data['payment_id'])
        
        # Get confidence score (default to 0 if not provided)
        confidence_score = data.get('extraction_confidence', 0)
        
        # Update payment extraction status
        payment.extraction_status = data['extraction_status']
        payment.extraction_date = datetime.utcnow()
        
        if 'extracted_data' in data and data['extracted_data']:
            extracted = data['extracted_data']
            payment.extracted_data = extracted
            
            # Check if confidence is HIGH (≥ 90%) - auto-apply
            if confidence_score >= 90:
                # HIGH CONFIDENCE - Auto-apply changes
                
                # Map extracted fields to payment fields
                if 'invoice_number' in extracted:
                    payment.invoice_ref = extracted['invoice_number']
                if 'supplier' in extracted:
                    payment.supplier = extracted['supplier']
                if 'invoice_date' in extracted:
                    try:
                        payment.invoice_date = datetime.strptime(extracted['invoice_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                if 'due_date' in extracted:
                    try:
                        payment.due_date = datetime.strptime(extracted['due_date'], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                if 'total_amount' in extracted:
                    try:
                        payment.total_amount = float(extracted['total_amount'])
                    except (ValueError, TypeError):
                        pass
                
                payment.extraction_confidence = confidence_score
                payment.updated_at = datetime.utcnow()
                payment.updated_by = 'AI (Auto)'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'auto_applied',
                    'message': f'High confidence ({confidence_score}%) - Changes applied automatically',
                    'payment_id': payment.id,
                    'extraction_confidence': confidence_score
                }), 200
                
            else:
                # LOW CONFIDENCE (< 90%) - Create AI Suggestion for manual review
                
                suggestion = AISuggestion(
                    target_table='payments',
                    target_id=payment.id,
                    action_type='update',
                    ai_model='Claude via n8n',
                    confidence_score=confidence_score,
                    extraction_source='document_upload',
                    source_document_path=data.get('document_path'),
                    ai_reasoning=f"Extracted from invoice. Confidence: {confidence_score}%. Please review fields - some values may need verification."
                )
                
                # Set suggested data using the proper method
                suggestion.set_suggested_data({
                    'invoice_ref': extracted.get('invoice_number'),
                    'supplier': extracted.get('supplier'),
                    'invoice_date': extracted.get('invoice_date'),
                    'due_date': extracted.get('due_date'),
                    'total_amount': extracted.get('total_amount'),
                    'items': extracted.get('items', [])
                })
                
                # Set current data for comparison
                suggestion.set_current_data({
                    'invoice_ref': payment.invoice_ref,
                    'supplier': payment.supplier,
                    'invoice_date': str(payment.invoice_date) if payment.invoice_date else None,
                    'due_date': str(payment.due_date) if payment.due_date else None,
                    'total_amount': payment.total_amount
                })
                
                db.session.add(suggestion)
                
                # Mark payment as needing review
                payment.extraction_confidence = confidence_score
                payment.extraction_status = 'needs_review'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'action': 'suggestion_created',
                    'message': f'Low confidence ({confidence_score}%) - Created AI suggestion for manual review',
                    'payment_id': payment.id,
                    'suggestion_id': suggestion.id,
                    'extraction_confidence': confidence_score,
                    'requires_review': True,
                    'reason': 'Confidence below 90% threshold - please verify extracted values'
                }), 200
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Extraction data received',
            'payment_id': payment.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save extraction data',
            'message': str(e)
        }), 500


@n8n_bp.route('/pending-deliveries', methods=['GET'])
@require_api_key
def get_pending_deliveries():
    """
    Get upcoming deliveries for reminder notifications.
    Used by n8n scheduled workflow (Daily 8 AM).
    
    Query Parameters:
        days: Number of days ahead to check (default: 7)
        status: Filter by delivery status (optional)
    
    Returns:
        200: List of pending deliveries with material details
    """
    try:
        days_ahead = request.args.get('days', 7, type=int)
        status_filter = request.args.get('status', None)
        
        from datetime import timedelta
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        # Query deliveries with expected dates within range
        query = Delivery.query.filter(
            Delivery.expected_delivery_date.isnot(None),
            Delivery.expected_delivery_date >= today,
            Delivery.expected_delivery_date <= future_date
        )
        
        # Filter by status if provided
        if status_filter:
            query = query.filter(Delivery.delivery_status == status_filter)
        else:
            # Exclude completed deliveries
            query = query.filter(Delivery.delivery_status != 'Delivered')
        
        deliveries = query.order_by(Delivery.expected_delivery_date.asc()).all()
        
        # Build response with full details
        result = []
        for delivery in deliveries:
            # Calculate days until delivery
            days_until = (delivery.expected_delivery_date - today).days
            
            delivery_data = delivery.to_dict()
            delivery_data['days_until_delivery'] = days_until
            delivery_data['urgency'] = 'high' if days_until <= 2 else 'medium' if days_until <= 5 else 'low'
            
            # Add related PO and material details
            if delivery.purchase_order:
                po = delivery.purchase_order
                delivery_data['po_details'] = {
                    'po_ref': po.po_ref,
                    'supplier_name': po.supplier_name,
                    'supplier_contact': po.supplier_contact,
                    'total_amount': po.total_amount,
                    'currency': po.currency
                }
                
                if po.material:
                    delivery_data['material_details'] = {
                        'material_type': po.material.material_type,
                        'project_name': po.material.project_name
                    }
            
            result.append(delivery_data)
        
        return jsonify({
            'success': True,
            'count': len(result),
            'days_ahead': days_ahead,
            'deliveries': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch pending deliveries',
            'message': str(e)
        }), 500


@n8n_bp.route('/weekly-report-data', methods=['GET'])
@require_api_key
def get_weekly_report_data():
    """
    Get comprehensive data for weekly report generation.
    Used by n8n scheduled workflow (Friday 5 PM).
    
    Returns:
        200: Summary statistics and lists for report
    """
    try:
        from sqlalchemy import func
        
        # Materials summary
        total_materials = Material.query.count()
        materials_by_status = db.session.query(
            Material.submittal_status,
            func.count(Material.id)
        ).group_by(Material.submittal_status).all()
        
        # Purchase Orders summary
        total_pos = PurchaseOrder.query.count()
        pos_by_status = db.session.query(
            PurchaseOrder.po_status,
            func.count(PurchaseOrder.id)
        ).group_by(PurchaseOrder.po_status).all()
        
        # Payment summary
        from models.payment import Payment
        total_payments = Payment.query.count()
        total_paid = db.session.query(func.sum(Payment.paid_amount)).scalar() or 0
        total_amount = db.session.query(func.sum(Payment.total_amount)).scalar() or 0
        payment_percentage = round((total_paid / total_amount * 100), 2) if total_amount > 0 else 0
        
        # Delivery summary
        total_deliveries = Delivery.query.count()
        deliveries_by_status = db.session.query(
            Delivery.delivery_status,
            func.count(Delivery.id)
        ).group_by(Delivery.delivery_status).all()
        
        # Delayed deliveries (expected date passed but not delivered)
        today = datetime.now().date()
        delayed_deliveries = Delivery.query.filter(
            Delivery.expected_delivery_date < today,
            Delivery.delivery_status != 'Delivered'
        ).all()
        
        # Upcoming deliveries (next 7 days)
        from datetime import timedelta
        next_week = today + timedelta(days=7)
        upcoming_deliveries = Delivery.query.filter(
            Delivery.expected_delivery_date >= today,
            Delivery.expected_delivery_date <= next_week,
            Delivery.delivery_status != 'Delivered'
        ).order_by(Delivery.expected_delivery_date.asc()).all()
        
        # Pending POs (Not Released)
        pending_pos = PurchaseOrder.query.filter_by(po_status='Not Released').all()
        
        # Recent activity (last 7 days)
        last_week = today - timedelta(days=7)
        recent_pos = PurchaseOrder.query.filter(
            PurchaseOrder.created_at >= last_week
        ).count()
        
        recent_deliveries = Delivery.query.filter(
            Delivery.actual_delivery_date >= last_week
        ).count()
        
        return jsonify({
            'success': True,
            'report_date': today.isoformat(),
            'summary': {
                'materials': {
                    'total': total_materials,
                    'by_status': dict(materials_by_status)
                },
                'purchase_orders': {
                    'total': total_pos,
                    'by_status': dict(pos_by_status),
                    'pending_release': len(pending_pos)
                },
                'payments': {
                    'total_payments': total_payments,
                    'total_amount': total_amount,
                    'total_paid': total_paid,
                    'completion_percentage': payment_percentage
                },
                'deliveries': {
                    'total': total_deliveries,
                    'by_status': dict(deliveries_by_status),
                    'delayed_count': len(delayed_deliveries),
                    'upcoming_count': len(upcoming_deliveries)
                },
                'recent_activity': {
                    'new_pos_last_week': recent_pos,
                    'deliveries_last_week': recent_deliveries
                }
            },
            'details': {
                'delayed_deliveries': [d.to_dict() for d in delayed_deliveries],
                'upcoming_deliveries': [d.to_dict() for d in upcoming_deliveries],
                'pending_pos': [po.to_dict() for po in pending_pos]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate weekly report data',
            'message': str(e)
        }), 500


@n8n_bp.route('/log-notification', methods=['POST'])
@require_api_key
def log_notification():
    """
    Log notifications sent by n8n workflows.
    Tracks delivery reminders, reports, and alerts.
    
    Expected JSON body:
    {
        "notification_type": "delivery_reminder",
        "recipient": "email@example.com",
        "subject": "Delivery Reminder",
        "sent_at": "2025-10-06T08:00:00",
        "status": "sent",
        "related_entity_type": "delivery",
        "related_entity_id": 1
    }
    
    Returns:
        200: Notification logged successfully
    """
    try:
        data = request.get_json()
        
        # For now, just acknowledge - you can create a Notification model later
        # to track all sent notifications in the database
        
        print(f"📧 Notification logged: {data.get('notification_type')} to {data.get('recipient')}")
        
        return jsonify({
            'success': True,
            'message': 'Notification logged successfully',
            'notification_id': data.get('notification_type') + '_' + str(datetime.now().timestamp())
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to log notification',
            'message': str(e)
        }), 500
