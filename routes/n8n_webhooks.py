"""
n8n Webhook Routes
API endpoints for n8n automation workflows
All endpoints require API key authentication
"""

from flask import Blueprint, request, jsonify
from models import db
from models.ai_suggestion import AISuggestion
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from routes.auth import require_api_key
from datetime import datetime
import json

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
