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
        ).order_by(AISuggestion.created_date.desc()).limit(limit).all()
        
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
            AISuggestion.created_date >= yesterday
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
    
    Expected JSON body:
    {
        "delivery_id": 1,
        "file_id": 5,
        "extraction_status": "completed",
        "extraction_confidence": 92.5,
        "extracted_data": {
            "delivery_order_number": "DO-2025-001",
            "delivery_date": "2025-01-15",
            "items": [
                {
                    "item_description": "Shower Mixer - Model SM-500",
                    "quantity": 20,
                    "unit": "pcs",
                    "delivered": true
                },
                {
                    "item_description": "Basin Mixer - Model BM-300",
                    "quantity": 15,
                    "unit": "pcs",
                    "delivered": true
                }
            ],
            "total_items": 2,
            "supplier": "ABC Sanitary Wares",
            "notes": "All items inspected and accepted"
        },
        "error_message": null
    }
    
    Returns:
        200: Extraction data saved successfully
        400: Invalid request data
        404: Delivery not found
        500: Server error
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
        
        # Update delivery with extraction results
        delivery.extraction_status = data['extraction_status']
        delivery.extraction_date = datetime.utcnow()
        
        if 'extracted_data' in data and data['extracted_data']:
            delivery.extracted_data = data['extracted_data']
            
            # Extract item count from data
            if 'items' in data['extracted_data']:
                delivery.extracted_item_count = len(data['extracted_data']['items'])
            elif 'total_items' in data['extracted_data']:
                delivery.extracted_item_count = data['extracted_data']['total_items']
        
        if 'extraction_confidence' in data:
            delivery.extraction_confidence = data['extraction_confidence']
        
        # If extraction completed successfully, auto-calculate delivery percentage
        if data['extraction_status'] == 'completed' and delivery.extracted_data:
            items = delivery.extracted_data.get('items', [])
            if items:
                delivered_items = sum(1 for item in items if item.get('delivered', False))
                total_items = len(items)
                if total_items > 0:
                    delivery.delivery_percentage = round((delivered_items / total_items) * 100, 2)
                    
                    # Auto-update status based on percentage
                    if delivery.delivery_percentage == 100:
                        delivery.delivery_status = 'Delivered'
                    elif delivery.delivery_percentage > 0:
                        delivery.delivery_status = 'Partial'
        
        delivery.updated_at = datetime.utcnow()
        delivery.updated_by = 'AI'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Extraction data saved successfully',
            'delivery_id': delivery.id,
            'extraction_status': delivery.extraction_status,
            'extraction_confidence': delivery.extraction_confidence,
            'extracted_item_count': delivery.extracted_item_count,
            'delivery_percentage': delivery.delivery_percentage,
            'delivery_status': delivery.delivery_status
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
    Receive extracted Purchase Order data from n8n + Claude API workflow.
    
    Expected JSON body:
    {
        "po_id": 1,
        "file_id": 5,
        "extraction_status": "completed",
        "extraction_confidence": 88.5,
        "extracted_data": {
            "po_number": "SAB_6001_49-2025",
            "po_date": "2025-10-01",
            "expected_delivery_date": "2025-10-15",
            "supplier_name": "ABC Suppliers LLC",
            "supplier_contact": "+971-50-123-4567",
            "supplier_email": "sales@abcsuppliers.ae",
            "material_type": "Distribution Board (DB)",
            "total_amount": 50000.00,
            "currency": "AED",
            "payment_terms": "Net 30 days",
            "delivery_terms": "FOB Destination",
            "items": [
                {
                    "description": "Main Distribution Board - 400A",
                    "quantity": "2",
                    "unit": "sets",
                    "unit_price": 25000.00
                }
            ],
            "notes": "Include installation manual"
        },
        "error_message": null
    }
    
    Returns:
        200: Extraction data saved successfully
        400: Invalid request data
        404: PO not found
        500: Server error
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
        
        # Update PO with extraction results
        if 'extracted_data' in data and data['extracted_data']:
            extracted = data['extracted_data']
            
            # Update PO fields from extracted data
            if 'po_number' in extracted and not po.po_ref:
                po.po_ref = extracted['po_number']
            
            if 'po_date' in extracted:
                try:
                    po.po_date = datetime.fromisoformat(extracted['po_date'])
                except:
                    pass
            
            if 'expected_delivery_date' in extracted:
                try:
                    po.expected_delivery_date = datetime.fromisoformat(extracted['expected_delivery_date'])
                except:
                    pass
            
            if 'supplier_name' in extracted:
                po.supplier_name = extracted['supplier_name']
            
            if 'supplier_contact' in extracted:
                po.supplier_contact = extracted['supplier_contact']
            
            if 'supplier_email' in extracted:
                po.supplier_email = extracted['supplier_email']
            
            if 'total_amount' in extracted:
                po.total_amount = float(extracted['total_amount'])
            
            if 'currency' in extracted:
                po.currency = extracted['currency']
            
            if 'payment_terms' in extracted:
                po.payment_terms = extracted['payment_terms']
            
            if 'delivery_terms' in extracted:
                po.delivery_terms = extracted['delivery_terms']
            
            if 'notes' in extracted:
                po.notes = extracted['notes']
        
        po.updated_at = datetime.utcnow()
        po.updated_by = 'AI'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'PO extraction data saved successfully',
            'po_id': po.id,
            'po_ref': po.po_ref,
            'extraction_confidence': data.get('extraction_confidence'),
            'supplier_name': po.supplier_name,
            'total_amount': po.total_amount
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save PO extraction data',
            'message': str(e)
        }), 500


@n8n_bp.route('/invoice-extraction', methods=['POST'])
@require_api_key
def receive_invoice_extraction():
    """
    Receive extracted Invoice/Payment data from n8n + Claude API workflow.
    
    Expected JSON body:
    {
        "payment_id": 1,
        "file_id": 5,
        "extraction_status": "completed",
        "extraction_confidence": 91.0,
        "extracted_data": {
            "invoice_number": "INV-2025-001",
            "invoice_date": "2025-10-05",
            "due_date": "2025-11-04",
            "po_reference": "SAB_6001_49-2025",
            "supplier_name": "ABC Suppliers LLC",
            "total_amount": 50000.00,
            "paid_amount": 25000.00,
            "payment_type": "Advance",
            "currency": "AED",
            "payment_terms": "50% Advance, 50% on Delivery",
            "items": [
                {
                    "description": "Distribution Board",
                    "quantity": "2",
                    "unit_price": 25000.00,
                    "amount": 50000.00
                }
            ],
            "bank_details": "IBAN: AE123456789",
            "notes": "Payment via bank transfer"
        },
        "error_message": null
    }
    
    Returns:
        200: Extraction data saved successfully
        400: Invalid request data
        404: Payment not found
        500: Server error
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
        
        # Get Payment record
        from models.payment import Payment
        payment = Payment.query.get_or_404(data['payment_id'])
        
        # Update payment with extraction results
        if 'extracted_data' in data and data['extracted_data']:
            extracted = data['extracted_data']
            
            # Update payment fields from extracted data
            if 'invoice_number' in extracted:
                payment.invoice_ref = extracted['invoice_number']
            
            if 'invoice_date' in extracted:
                try:
                    payment.payment_date = datetime.fromisoformat(extracted['invoice_date'])
                except:
                    pass
            
            if 'total_amount' in extracted:
                payment.total_amount = float(extracted['total_amount'])
            
            if 'paid_amount' in extracted:
                payment.paid_amount = float(extracted['paid_amount'])
            
            if 'payment_type' in extracted:
                payment.payment_type = extracted['payment_type']
            
            if 'currency' in extracted:
                payment.currency = extracted['currency']
            
            if 'payment_terms' in extracted:
                payment.payment_terms = extracted['payment_terms']
            
            if 'notes' in extracted:
                payment.notes = extracted['notes']
            
            # Calculate payment percentage
            payment.calculate_percentage()
            
            # Update payment status based on percentage
            if payment.payment_percentage >= 100:
                payment.payment_status = 'Full'
            elif payment.payment_percentage > 0:
                payment.payment_status = 'Partial'
        
        payment.updated_at = datetime.utcnow()
        payment.updated_by = 'AI'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice extraction data saved successfully',
            'payment_id': payment.id,
            'invoice_ref': payment.invoice_ref,
            'extraction_confidence': data.get('extraction_confidence'),
            'total_amount': payment.total_amount,
            'paid_amount': payment.paid_amount,
            'payment_percentage': payment.payment_percentage
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save invoice extraction data',
            'message': str(e)
        }), 500
