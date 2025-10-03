from flask import Blueprint, request, jsonify
from models import db
from models.delivery import Delivery
from datetime import datetime

deliveries_bp = Blueprint('deliveries', __name__)

@deliveries_bp.route('', methods=['GET'])
def get_deliveries():
    """Get all deliveries"""
    try:
        deliveries = Delivery.query.all()
        
        # Check for delays
        for delivery in deliveries:
            delivery.check_delay()
        db.session.commit()
        
        return jsonify([delivery.to_dict() for delivery in deliveries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/<int:id>', methods=['GET'])
def get_delivery(id):
    """Get a specific delivery"""
    try:
        delivery = Delivery.query.get_or_404(id)
        delivery.check_delay()
        db.session.commit()
        
        return jsonify(delivery.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/pending', methods=['GET'])
def get_pending_deliveries():
    """Get pending deliveries (for n8n integration)"""
    try:
        deliveries = Delivery.query.filter(
            Delivery.delivery_status.in_(['Pending', 'In Transit'])
        ).all()
        
        return jsonify([delivery.to_dict() for delivery in deliveries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/delayed', methods=['GET'])
def get_delayed_deliveries():
    """Get delayed deliveries"""
    try:
        deliveries = Delivery.query.filter_by(is_delayed=True).all()
        return jsonify([delivery.to_dict() for delivery in deliveries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('', methods=['POST'])
def create_delivery():
    """Create a new delivery"""
    try:
        data = request.get_json()
        
        delivery = Delivery(
            po_id=data.get('po_id'),
            delivery_status=data.get('delivery_status', 'Pending'),
            ordered_quantity=data.get('ordered_quantity'),
            delivered_quantity=data.get('delivered_quantity', 0),
            unit=data.get('unit'),
            tracking_number=data.get('tracking_number'),
            carrier=data.get('carrier'),
            delivery_location=data.get('delivery_location'),
            received_by=data.get('received_by'),
            delay_reason=data.get('delay_reason'),
            notes=data.get('notes'),
            delivery_note_path=data.get('delivery_note_path'),
            created_by=data.get('created_by', 'Manual')
        )
        
        if data.get('expected_delivery_date'):
            delivery.expected_delivery_date = datetime.fromisoformat(data['expected_delivery_date'])
        if data.get('actual_delivery_date'):
            delivery.actual_delivery_date = datetime.fromisoformat(data['actual_delivery_date'])
        
        delivery.check_delay()
        
        db.session.add(delivery)
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery created successfully',
            'delivery': delivery.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/<int:id>', methods=['PUT'])
def update_delivery(id):
    """Update a delivery"""
    try:
        delivery = Delivery.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'po_id' in data:
            delivery.po_id = data['po_id']
        if 'delivery_status' in data:
            delivery.delivery_status = data['delivery_status']
        if 'ordered_quantity' in data:
            delivery.ordered_quantity = data['ordered_quantity']
        if 'delivered_quantity' in data:
            delivery.delivered_quantity = data['delivered_quantity']
        if 'unit' in data:
            delivery.unit = data['unit']
        if 'tracking_number' in data:
            delivery.tracking_number = data['tracking_number']
        if 'carrier' in data:
            delivery.carrier = data['carrier']
        if 'delivery_location' in data:
            delivery.delivery_location = data['delivery_location']
        if 'received_by' in data:
            delivery.received_by = data['received_by']
        if 'delay_reason' in data:
            delivery.delay_reason = data['delay_reason']
        if 'notes' in data:
            delivery.notes = data['notes']
        if 'delivery_note_path' in data:
            delivery.delivery_note_path = data['delivery_note_path']
        if 'expected_delivery_date' in data:
            delivery.expected_delivery_date = datetime.fromisoformat(data['expected_delivery_date']) if data['expected_delivery_date'] else None
        if 'actual_delivery_date' in data:
            delivery.actual_delivery_date = datetime.fromisoformat(data['actual_delivery_date']) if data['actual_delivery_date'] else None
        
        delivery.check_delay()
        delivery.updated_by = data.get('updated_by', 'Manual')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery updated successfully',
            'delivery': delivery.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/<int:id>', methods=['DELETE'])
def delete_delivery(id):
    """Delete a delivery"""
    try:
        delivery = Delivery.query.get_or_404(id)
        db.session.delete(delivery)
        db.session.commit()
        
        return jsonify({'message': 'Delivery deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@deliveries_bp.route('/po/<int:po_id>', methods=['GET'])
def get_deliveries_by_po(po_id):
    """Get all deliveries for a specific PO"""
    try:
        deliveries = Delivery.query.filter_by(po_id=po_id).all()
        for delivery in deliveries:
            delivery.check_delay()
        db.session.commit()
        
        return jsonify([delivery.to_dict() for delivery in deliveries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
