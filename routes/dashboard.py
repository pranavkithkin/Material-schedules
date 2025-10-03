from flask import Blueprint, render_template, jsonify
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from models.ai_suggestion import AISuggestion
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@dashboard_bp.route('/materials')
def materials_page():
    """Materials management page"""
    return render_template('materials.html')

@dashboard_bp.route('/purchase_orders')
def purchase_orders_page():
    """Purchase orders management page"""
    return render_template('purchase_orders.html')

@dashboard_bp.route('/payments')
def payments_page():
    """Payments management page"""
    return render_template('payments.html')

@dashboard_bp.route('/deliveries')
def deliveries_page():
    """Deliveries management page"""
    return render_template('deliveries.html')

@dashboard_bp.route('/ai_suggestions')
def ai_suggestions_page():
    """AI suggestions review page"""
    return render_template('ai_suggestions.html')

@dashboard_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Material stats
        total_materials = Material.query.count()
        approved_materials = Material.query.filter_by(approval_status='Approved').count()
        pending_materials = Material.query.filter_by(approval_status='Pending').count()
        
        # PO stats
        total_pos = PurchaseOrder.query.count()
        released_pos = PurchaseOrder.query.filter_by(po_status='Released').count()
        
        # Delivery stats
        total_deliveries = Delivery.query.count()
        pending_deliveries = Delivery.query.filter_by(delivery_status='Pending').count()
        delayed_deliveries = Delivery.query.filter_by(is_delayed=True).count()
        completed_deliveries = Delivery.query.filter_by(delivery_status='Completed').count()
        
        # AI suggestions stats
        pending_suggestions = AISuggestion.query.filter_by(status='pending').count()
        high_confidence_suggestions = AISuggestion.query.filter(
            AISuggestion.status == 'pending',
            AISuggestion.confidence_score >= 90
        ).count()
        
        # Total PO value
        total_po_value = db.session.query(func.sum(PurchaseOrder.total_amount)).scalar() or 0
        
        return jsonify({
            'materials': {
                'total': total_materials,
                'approved': approved_materials,
                'pending': pending_materials
            },
            'purchase_orders': {
                'total': total_pos,
                'released': released_pos,
                'total_value': total_po_value
            },
            'deliveries': {
                'total': total_deliveries,
                'pending': pending_deliveries,
                'delayed': delayed_deliveries,
                'completed': completed_deliveries
            },
            'ai_suggestions': {
                'pending': pending_suggestions,
                'high_confidence': high_confidence_suggestions
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
