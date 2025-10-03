from flask import Blueprint, request, jsonify
from models import db
from models.payment import Payment
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('', methods=['GET'])
def get_payments():
    """Get all payments"""
    try:
        payments = Payment.query.all()
        return jsonify([payment.to_dict() for payment in payments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:id>', methods=['GET'])
def get_payment(id):
    """Get a specific payment"""
    try:
        payment = Payment.query.get_or_404(id)
        return jsonify(payment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('', methods=['POST'])
def create_payment():
    """Create a new payment"""
    try:
        data = request.get_json()
        
        payment = Payment(
            po_id=data.get('po_id'),
            payment_structure=data.get('payment_structure', 'Single Payment'),
            payment_type=data.get('payment_type'),
            total_amount=data.get('total_amount'),
            paid_amount=data.get('paid_amount', 0),
            payment_ref=data.get('payment_ref'),
            invoice_ref=data.get('invoice_ref'),
            payment_method=data.get('payment_method'),
            currency=data.get('currency', 'AED'),
            payment_status=data.get('payment_status', 'Pending'),
            notes=data.get('notes'),
            invoice_path=data.get('invoice_path'),
            receipt_path=data.get('receipt_path'),
            created_by=data.get('created_by', 'Manual')
        )
        
        if data.get('payment_date'):
            payment.payment_date = datetime.fromisoformat(data['payment_date'])
        
        payment.calculate_percentage()
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment': payment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:id>', methods=['PUT'])
def update_payment(id):
    """Update a payment"""
    try:
        payment = Payment.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'po_id' in data:
            payment.po_id = data['po_id']
        if 'payment_structure' in data:
            payment.payment_structure = data['payment_structure']
        if 'payment_type' in data:
            payment.payment_type = data['payment_type']
        if 'total_amount' in data:
            payment.total_amount = data['total_amount']
        if 'paid_amount' in data:
            payment.paid_amount = data['paid_amount']
        if 'payment_ref' in data:
            payment.payment_ref = data['payment_ref']
        if 'invoice_ref' in data:
            payment.invoice_ref = data['invoice_ref']
        if 'payment_method' in data:
            payment.payment_method = data['payment_method']
        if 'currency' in data:
            payment.currency = data['currency']
        if 'payment_status' in data:
            payment.payment_status = data['payment_status']
        if 'notes' in data:
            payment.notes = data['notes']
        if 'invoice_path' in data:
            payment.invoice_path = data['invoice_path']
        if 'receipt_path' in data:
            payment.receipt_path = data['receipt_path']
        if 'payment_date' in data:
            payment.payment_date = datetime.fromisoformat(data['payment_date']) if data['payment_date'] else None
        
        payment.calculate_percentage()
        payment.updated_by = data.get('updated_by', 'Manual')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment updated successfully',
            'payment': payment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:id>', methods=['DELETE'])
def delete_payment(id):
    """Delete a payment"""
    try:
        payment = Payment.query.get_or_404(id)
        db.session.delete(payment)
        db.session.commit()
        
        return jsonify({'message': 'Payment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/po/<int:po_id>', methods=['GET'])
def get_payments_by_po(po_id):
    """Get all payments for a specific PO"""
    try:
        payments = Payment.query.filter_by(po_id=po_id).all()
        return jsonify([payment.to_dict() for payment in payments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
