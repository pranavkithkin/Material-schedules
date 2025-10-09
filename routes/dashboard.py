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
import os
import requests

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

@dashboard_bp.route('/lpo')
def lpo_page():
    """Local Purchase Orders (LPO) management page"""
    import os
    api_key = os.getenv('N8N_TO_FLASK_API_KEY', '')
    return render_template('lpo.html', config={'N8N_TO_FLASK_API_KEY': api_key})

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
        
        # AI Document Intelligence stats
        total_extractions = Delivery.query.filter(
            Delivery.extraction_status == 'completed'
        ).count()
        
        # Count successful extractions (confidence >= 80%)
        successful_extractions = Delivery.query.filter(
            Delivery.extraction_status == 'completed',
            Delivery.extraction_confidence >= 80
        ).count()
        
        # Calculate success rate
        success_rate = round((successful_extractions / total_extractions * 100), 1) if total_extractions > 0 else 0
        
        # Average confidence
        avg_confidence = db.session.query(
            func.avg(Delivery.extraction_confidence)
        ).filter(
            Delivery.extraction_status == 'completed'
        ).scalar() or 0
        avg_confidence = round(avg_confidence, 1)
        
        # Total items extracted
        total_items = db.session.query(
            func.sum(Delivery.extracted_item_count)
        ).scalar() or 0
        
        return jsonify({
            'materials_count': total_materials,
            'materials': {
                'total': total_materials,
                'approved': approved_materials,
                'pending': pending_materials
            },
            'purchase_orders_count': total_pos,
            'purchase_orders': {
                'total': total_pos,
                'released': released_pos,
                'total_value': total_po_value
            },
            'deliveries_count': total_deliveries,
            'deliveries': {
                'total': total_deliveries,
                'pending': pending_deliveries,
                'delayed': delayed_deliveries,
                'completed': completed_deliveries
            },
            'payments_count': Payment.query.count(),
            'ai_suggestions_count': pending_suggestions,
            'ai_suggestions': {
                'pending': pending_suggestions,
                'high_confidence': high_confidence_suggestions
            },
            'ai_document_intelligence': {
                'success_rate': success_rate,
                'total_extractions': total_extractions,
                'po_count': 0,  # Will be implemented when PO extraction is added
                'invoice_count': 0,  # Will be implemented when invoice extraction is added
                'delivery_count': total_extractions,
                'avg_confidence': avg_confidence,
                'total_items': int(total_items)
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

@dashboard_bp.route('/api/dashboard/n8n-status')
def n8n_status():
    """Check if n8n and AI features are available"""
    
    status = {
        'n8n_live': False,
        'ai_features_available': False,
        'mode': 'manual',
        'last_checked': datetime.now().isoformat(),
        'details': {}
    }
    
    try:
        # Check if n8n URL is configured
        n8n_base_url = os.getenv('N8N_BASE_URL', '')
        
        if not n8n_base_url:
            # Fallback to webhook URL base
            webhook_url = os.getenv('N8N_WEBHOOK_URL', '')
            if webhook_url:
                # Extract base URL from webhook URL (remove /webhook path)
                n8n_base_url = webhook_url.replace('/webhook', '')
            else:
                status['details']['message'] = 'n8n URL not configured'
                return jsonify(status)
        
        status['details']['n8n_url'] = n8n_base_url
        
        # Try to ping n8n health endpoint (with timeout)
        try:
            response = requests.get(
                f"{n8n_base_url}/healthz",
                timeout=5,  # 5 second timeout
                verify=True  # Verify SSL certificates
            )
            
            if response.status_code == 200:
                status['n8n_live'] = True
                status['details']['n8n_status'] = 'online'
                status['details']['n8n_response'] = response.json() if response.headers.get('content-type') == 'application/json' else 'OK'
            else:
                status['details']['n8n_status'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            status['details']['n8n_status'] = 'timeout (>5s)'
        except requests.exceptions.SSLError as e:
            status['details']['n8n_status'] = f'SSL error: {str(e)[:50]}'
        except requests.exceptions.ConnectionError as e:
            status['details']['n8n_status'] = f'connection error: {str(e)[:50]}'
        except Exception as e:
            status['details']['n8n_status'] = f'error: {str(e)[:50]}'
        
        # Check if AI API keys are configured
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')
        openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
        
        ai_configured = bool(anthropic_key or openai_key or openrouter_key)
        
        if ai_configured:
            status['details']['ai_api'] = 'configured'
            if anthropic_key:
                status['details']['ai_provider'] = 'Anthropic Claude'
            elif openai_key:
                status['details']['ai_provider'] = 'OpenAI'
            elif openrouter_key:
                status['details']['ai_provider'] = 'OpenRouter'
        else:
            status['details']['ai_api'] = 'not configured'
        
        # Both n8n and AI must be available for AI features
        status['ai_features_available'] = status['n8n_live'] and ai_configured
        
        # Set mode
        if status['ai_features_available']:
            status['mode'] = 'ai_assisted'
            status['details']['message'] = 'AI document processing available ✓'
        elif status['n8n_live'] and not ai_configured:
            status['mode'] = 'partial'
            status['details']['message'] = 'n8n online but AI API not configured'
        else:
            status['mode'] = 'manual'
            status['details']['message'] = 'Manual mode only - AI features unavailable'
        
    except Exception as e:
        status['details']['error'] = str(e)
    
    return jsonify(status)

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
        
        # Sum payments for this month - use paid_amount field
        total = db.session.query(func.sum(Payment.paid_amount)).filter(
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
        Material.description,
        func.sum(PurchaseOrder.total_amount).label('total_value')
    ).join(
        PurchaseOrder, Material.id == PurchaseOrder.material_id
    ).group_by(
        Material.description
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
