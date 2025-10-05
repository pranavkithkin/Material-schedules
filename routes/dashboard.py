from flask import Blueprint, render_template, jsonify
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from models.ai_suggestion import AISuggestion
from models.payment import Payment
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import calendar

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@dashboard_bp.route('/materials')
def materials_page():
    """Materials management page"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('materials.html', config={'N8N_TO_FLASK_API_KEY': api_key})

@dashboard_bp.route('/purchase_orders')
def purchase_orders_page():
    """Purchase orders management page"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('purchase_orders.html', config={'N8N_TO_FLASK_API_KEY': api_key})

@dashboard_bp.route('/payments')
def payments_page():
    """Payments management page"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('payments.html', config={'N8N_TO_FLASK_API_KEY': api_key})

@dashboard_bp.route('/deliveries')
def deliveries_page():
    """Deliveries management page"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('deliveries.html', config={'N8N_TO_FLASK_API_KEY': api_key})

@dashboard_bp.route('/ai_suggestions')
def ai_suggestions_page():
    """AI suggestions review page"""
    return render_template('ai_suggestions.html')

@dashboard_bp.route('/test-validation')
def test_validation_page():
    """Test validation agent page (Sprint 1)"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('test_validation.html', api_key=api_key)

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
        
        # AI Document Intelligence Stats (Sprint 2)
        # Count documents with extracted data
        from models.payment import Payment
        
        po_with_extraction = PurchaseOrder.query.filter(PurchaseOrder.extracted_data.isnot(None)).count()
        payment_with_extraction = Payment.query.filter(Payment.extracted_data.isnot(None)).count()
        delivery_with_extraction = Delivery.query.filter(Delivery.extracted_data.isnot(None)).count()
        
        total_extractions = po_with_extraction + payment_with_extraction + delivery_with_extraction
        
        # Calculate success rate (documents with extraction_status = 'completed')
        po_successful = PurchaseOrder.query.filter_by(extraction_status='completed').count()
        payment_successful = Payment.query.filter_by(extraction_status='completed').count()
        delivery_successful = Delivery.query.filter_by(extraction_status='completed').count()
        total_successful = po_successful + payment_successful + delivery_successful
        
        success_rate = round((total_successful / total_extractions * 100) if total_extractions > 0 else 0)
        
        # Calculate average confidence
        po_confidences = db.session.query(PurchaseOrder.extraction_confidence).filter(
            PurchaseOrder.extraction_confidence.isnot(None)
        ).all()
        payment_confidences = db.session.query(Payment.extraction_confidence).filter(
            Payment.extraction_confidence.isnot(None)
        ).all()
        delivery_confidences = db.session.query(Delivery.extraction_confidence).filter(
            Delivery.extraction_confidence.isnot(None)
        ).all()
        
        all_confidences = [c[0] for c in po_confidences + payment_confidences + delivery_confidences if c[0] is not None]
        avg_confidence = round(sum(all_confidences) / len(all_confidences)) if all_confidences else 0
        
        # Calculate total items extracted
        po_items = db.session.query(func.sum(PurchaseOrder.extracted_item_count)).filter(
            PurchaseOrder.extracted_item_count.isnot(None)
        ).scalar() or 0
        payment_items = db.session.query(func.sum(Payment.extracted_item_count)).filter(
            Payment.extracted_item_count.isnot(None)
        ).scalar() or 0
        delivery_items = db.session.query(func.sum(Delivery.extracted_item_count)).filter(
            Delivery.extracted_item_count.isnot(None)
        ).scalar() or 0
        
        total_items = int(po_items + payment_items + delivery_items)
        
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
            },
            'ai_document_intelligence': {
                'success_rate': success_rate,
                'total_extractions': total_extractions,
                'po_count': po_with_extraction,
                'invoice_count': payment_with_extraction,
                'delivery_count': delivery_with_extraction,
                'avg_confidence': avg_confidence,
                'total_items': total_items
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/dashboard/analytics')
def dashboard_analytics():
    """Get analytics data for charts"""
    try:
        # Payment Trends (Last 6 months)
        payment_trends = get_payment_trends()
        
        # Delivery Status Distribution
        delivery_status = get_delivery_status_distribution()
        
        # Top Materials by Value
        materials_by_type = get_top_materials()
        
        # PO Completion Rate
        po_completion = get_po_completion_rate()
        
        return jsonify({
            'payment_trends': payment_trends,
            'delivery_status': delivery_status,
            'materials_by_type': materials_by_type,
            'po_completion': po_completion
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_payment_trends():
    """Get payment trends for the last 6 months"""
    today = datetime.now()
    labels = []
    values = []
    
    for i in range(5, -1, -1):
        # Calculate month
        month = today.month - i
        year = today.year
        
        if month <= 0:
            month += 12
            year -= 1
        
        # Get month name
        month_name = calendar.month_abbr[month]
        labels.append(month_name)
        
        # Sum payments for this month
        total = db.session.query(func.sum(Payment.amount)).filter(
            extract('month', Payment.payment_date) == month,
            extract('year', Payment.payment_date) == year
        ).scalar() or 0
        
        values.append(float(total))
    
    return {'labels': labels, 'values': values}

def get_delivery_status_distribution():
    """Get delivery status distribution"""
    pending = Delivery.query.filter_by(delivery_status='Pending').count()
    in_transit = Delivery.query.filter_by(delivery_status='In Transit').count()
    completed = Delivery.query.filter_by(delivery_status='Completed').count()
    delayed = Delivery.query.filter_by(is_delayed=True).count()
    
    return {
        'labels': ['Pending', 'In Transit', 'Completed', 'Delayed'],
        'values': [pending, in_transit, completed, delayed]
    }

def get_top_materials():
    """Get top 5 materials by total value"""
    # Join with PO to get material values
    results = db.session.query(
        Material.material_description,
        func.sum(PurchaseOrder.total_amount).label('total_value')
    ).join(
        PurchaseOrder, Material.id == PurchaseOrder.material_id
    ).group_by(
        Material.material_description
    ).order_by(
        func.sum(PurchaseOrder.total_amount).desc()
    ).limit(5).all()
    
    if not results:
        return {'labels': [], 'values': []}
    
    labels = [r[0][:30] + '...' if len(r[0]) > 30 else r[0] for r in results]
    values = [float(r[1]) for r in results]
    
    return {'labels': labels, 'values': values}

def get_po_completion_rate():
    """Get PO completion metrics"""
    total_pos = PurchaseOrder.query.count()
    
    # Count POs by status
    draft = PurchaseOrder.query.filter_by(po_status='Draft').count()
    released = PurchaseOrder.query.filter_by(po_status='Released').count()
    in_progress = PurchaseOrder.query.filter_by(po_status='In Progress').count()
    completed = PurchaseOrder.query.filter_by(po_status='Completed').count()
    cancelled = PurchaseOrder.query.filter_by(po_status='Cancelled').count()
    
    return {
        'labels': ['Draft', 'Released', 'In Progress', 'Completed', 'Cancelled'],
        'values': [draft, released, in_progress, completed, cancelled]
    }
