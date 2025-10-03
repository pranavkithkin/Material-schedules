from flask import Blueprint, request, jsonify
from models import db
from models.ai_suggestion import AISuggestion
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery
from config import Config
from datetime import datetime

ai_suggestions_bp = Blueprint('ai_suggestions', __name__)

@ai_suggestions_bp.route('', methods=['GET'])
def get_suggestions():
    """Get all AI suggestions"""
    try:
        suggestions = AISuggestion.query.order_by(AISuggestion.created_at.desc()).all()
        return jsonify([suggestion.to_dict() for suggestion in suggestions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_suggestions_bp.route('/pending', methods=['GET'])
def get_pending_suggestions():
    """Get pending AI suggestions"""
    try:
        suggestions = AISuggestion.query.filter_by(status='pending').order_by(
            AISuggestion.confidence_score.desc()
        ).all()
        return jsonify([suggestion.to_dict() for suggestion in suggestions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_suggestions_bp.route('/<int:id>', methods=['GET'])
def get_suggestion(id):
    """Get a specific AI suggestion"""
    try:
        suggestion = AISuggestion.query.get_or_404(id)
        return jsonify(suggestion.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_suggestions_bp.route('', methods=['POST'])
def create_suggestion():
    """Create a new AI suggestion (called by n8n)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['target_table', 'action_type', 'confidence_score', 'suggested_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create suggestion
        suggestion = AISuggestion(
            target_table=data['target_table'],
            target_id=data.get('target_id'),
            action_type=data['action_type'],
            ai_model=data.get('ai_model', 'unknown'),
            confidence_score=data['confidence_score'],
            extraction_source=data.get('extraction_source'),
            source_document_path=data.get('source_document_path'),
            ai_reasoning=data.get('ai_reasoning')
        )
        
        suggestion.set_suggested_data(data['suggested_data'])
        
        if data.get('current_data'):
            suggestion.set_current_data(data['current_data'])
        
        if data.get('missing_fields'):
            suggestion.set_missing_fields(data['missing_fields'])
        
        # Check if should auto-apply
        if suggestion.should_auto_apply(Config.AI_AUTO_UPDATE_THRESHOLD):
            # Auto-apply high confidence suggestions
            success = apply_suggestion(suggestion)
            if success:
                suggestion.status = 'auto_applied'
                suggestion.reviewed_at = datetime.utcnow()
            else:
                suggestion.status = 'pending'  # Fallback to manual review if auto-apply fails
        else:
            suggestion.status = 'pending'
        
        db.session.add(suggestion)
        db.session.commit()
        
        return jsonify({
            'message': 'AI suggestion created successfully',
            'suggestion': suggestion.to_dict(),
            'auto_applied': suggestion.status == 'auto_applied'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_suggestions_bp.route('/<int:id>/approve', methods=['PUT'])
def approve_suggestion(id):
    """Approve and apply an AI suggestion"""
    try:
        suggestion = AISuggestion.query.get_or_404(id)
        
        if suggestion.status != 'pending':
            return jsonify({'error': 'Suggestion is not pending'}), 400
        
        # Apply the suggestion
        success = apply_suggestion(suggestion)
        
        if success:
            suggestion.status = 'approved'
            suggestion.reviewed_by = request.json.get('reviewed_by', 'User')
            suggestion.reviewed_at = datetime.utcnow()
            suggestion.review_notes = request.json.get('review_notes')
            
            db.session.commit()
            
            return jsonify({
                'message': 'Suggestion approved and applied successfully',
                'suggestion': suggestion.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to apply suggestion'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ai_suggestions_bp.route('/<int:id>/reject', methods=['PUT'])
def reject_suggestion(id):
    """Reject an AI suggestion"""
    try:
        suggestion = AISuggestion.query.get_or_404(id)
        
        if suggestion.status != 'pending':
            return jsonify({'error': 'Suggestion is not pending'}), 400
        
        suggestion.status = 'rejected'
        suggestion.reviewed_by = request.json.get('reviewed_by', 'User')
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.review_notes = request.json.get('review_notes')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Suggestion rejected successfully',
            'suggestion': suggestion.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def apply_suggestion(suggestion):
    """Apply an AI suggestion to the database"""
    try:
        suggested_data = suggestion.get_suggested_data()
        
        # Add audit trail
        suggested_data['updated_by'] = f'AI ({suggestion.ai_model})'
        
        if suggestion.target_table == 'materials':
            if suggestion.action_type == 'create':
                record = Material(**suggested_data)
                db.session.add(record)
            else:  # update
                record = Material.query.get(suggestion.target_id)
                if not record:
                    return False
                for key, value in suggested_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
        
        elif suggestion.target_table == 'purchase_orders':
            if suggestion.action_type == 'create':
                record = PurchaseOrder(**suggested_data)
                db.session.add(record)
            else:  # update
                record = PurchaseOrder.query.get(suggestion.target_id)
                if not record:
                    return False
                for key, value in suggested_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
        
        elif suggestion.target_table == 'payments':
            if suggestion.action_type == 'create':
                record = Payment(**suggested_data)
                record.calculate_percentage()
                db.session.add(record)
            else:  # update
                record = Payment.query.get(suggestion.target_id)
                if not record:
                    return False
                for key, value in suggested_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                record.calculate_percentage()
        
        elif suggestion.target_table == 'deliveries':
            if suggestion.action_type == 'create':
                record = Delivery(**suggested_data)
                record.check_delay()
                db.session.add(record)
            else:  # update
                record = Delivery.query.get(suggestion.target_id)
                if not record:
                    return False
                for key, value in suggested_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                record.check_delay()
        else:
            return False
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error applying suggestion: {e}")
        db.session.rollback()
        return False
