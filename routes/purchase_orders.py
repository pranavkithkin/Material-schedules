from flask import Blueprint, request, jsonify
from models import db
from models.purchase_order import PurchaseOrder
from datetime import datetime

purchase_orders_bp = Blueprint('purchase_orders', __name__)

@purchase_orders_bp.route('', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders"""
    try:
        pos = PurchaseOrder.query.all()
        return jsonify([po.to_dict() for po in pos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@purchase_orders_bp.route('/<int:id>', methods=['GET'])
def get_purchase_order(id):
    """Get a specific purchase order"""
    try:
        po = PurchaseOrder.query.get_or_404(id)
        result = po.to_dict()
        
        # Include related data
        result['payments'] = [payment.to_dict() for payment in po.payments]
        result['deliveries'] = [delivery.to_dict() for delivery in po.deliveries]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@purchase_orders_bp.route('', methods=['POST'])
def create_purchase_order():
    """Create a new purchase order"""
    try:
        data = request.get_json()
        
        po = PurchaseOrder(
            material_id=data.get('material_id'),
            quote_ref=data.get('quote_ref'),
            po_ref=data.get('po_ref'),
            supplier_name=data.get('supplier_name'),
            supplier_contact=data.get('supplier_contact'),
            supplier_email=data.get('supplier_email'),
            total_amount=data.get('total_amount'),
            currency=data.get('currency', 'AED'),
            po_status=data.get('po_status', 'Not Released'),
            payment_terms=data.get('payment_terms'),
            delivery_terms=data.get('delivery_terms'),
            notes=data.get('notes'),
            document_path=data.get('document_path'),
            created_by=data.get('created_by', 'Manual')
        )
        
        if data.get('po_date'):
            po.po_date = datetime.fromisoformat(data['po_date'])
        
        db.session.add(po)
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase order created successfully',
            'purchase_order': po.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@purchase_orders_bp.route('/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    """Update a purchase order"""
    try:
        po = PurchaseOrder.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'material_id' in data:
            po.material_id = data['material_id']
        if 'quote_ref' in data:
            po.quote_ref = data['quote_ref']
        if 'po_ref' in data:
            po.po_ref = data['po_ref']
        if 'supplier_name' in data:
            po.supplier_name = data['supplier_name']
        if 'supplier_contact' in data:
            po.supplier_contact = data['supplier_contact']
        if 'supplier_email' in data:
            po.supplier_email = data['supplier_email']
        if 'total_amount' in data:
            po.total_amount = data['total_amount']
        if 'currency' in data:
            po.currency = data['currency']
        if 'po_status' in data:
            po.po_status = data['po_status']
        if 'payment_terms' in data:
            po.payment_terms = data['payment_terms']
        if 'delivery_terms' in data:
            po.delivery_terms = data['delivery_terms']
        if 'notes' in data:
            po.notes = data['notes']
        if 'document_path' in data:
            po.document_path = data['document_path']
        if 'po_date' in data:
            po.po_date = datetime.fromisoformat(data['po_date']) if data['po_date'] else None
        
        po.updated_by = data.get('updated_by', 'Manual')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase order updated successfully',
            'purchase_order': po.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@purchase_orders_bp.route('/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    """Delete a purchase order"""
    try:
        po = PurchaseOrder.query.get_or_404(id)
        db.session.delete(po)
        db.session.commit()
        
        return jsonify({'message': 'Purchase order deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
