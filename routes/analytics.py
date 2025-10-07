"""
Analytics Routes Blueprint
Provides API endpoints for advanced analytics and business intelligence
"""
from flask import Blueprint, render_template, jsonify, request
from services.analytics_service import AnalyticsService
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


# ==================== PAGE ROUTES ====================

@analytics_bp.route('/')
def analytics_page():
    """Analytics dashboard page"""
    return render_template('analytics.html')


# ==================== SUPPLIER PERFORMANCE ====================

@analytics_bp.route('/api/supplier-performance')
def supplier_performance():
    """
    Get supplier performance metrics
    
    Query Parameters:
        supplier_name (optional): Filter by specific supplier
        date_range_days (optional): Number of days to analyze (default: 180)
    """
    try:
        supplier_name = request.args.get('supplier_name')
        date_range_days = int(request.args.get('date_range_days', 180))
        
        results = AnalyticsService.get_supplier_performance(
            supplier_name=supplier_name,
            date_range_days=date_range_days
        )
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== PREDICTIVE ANALYTICS ====================

@analytics_bp.route('/api/delay-predictions')
def delay_predictions():
    """
    Get delivery delay predictions
    
    Query Parameters:
        po_id (optional): Filter by specific PO
    """
    try:
        po_id = request.args.get('po_id', type=int)
        
        predictions = AnalyticsService.predict_delivery_delays(po_id=po_id)
        
        return jsonify({
            'success': True,
            'data': predictions,
            'count': len(predictions),
            'high_risk_count': sum(1 for p in predictions if p['risk_score'] >= 70),
            'medium_risk_count': sum(1 for p in predictions if 40 <= p['risk_score'] < 70),
            'low_risk_count': sum(1 for p in predictions if p['risk_score'] < 40)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== FINANCIAL ANALYTICS ====================

@analytics_bp.route('/api/financial-analytics')
def financial_analytics():
    """
    Get comprehensive financial analytics
    
    Query Parameters:
        date_range_days (optional): Number of days to analyze (default: 180)
    """
    try:
        date_range_days = int(request.args.get('date_range_days', 180))
        
        analytics = AnalyticsService.get_financial_analytics(
            date_range_days=date_range_days
        )
        
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== DELIVERY INTELLIGENCE ====================

@analytics_bp.route('/api/delivery-intelligence')
def delivery_intelligence():
    """
    Get delivery intelligence and insights
    
    Query Parameters:
        date_range_days (optional): Number of days to analyze (default: 180)
    """
    try:
        date_range_days = int(request.args.get('date_range_days', 180))
        
        intelligence = AnalyticsService.get_delivery_intelligence(
            date_range_days=date_range_days
        )
        
        return jsonify({
            'success': True,
            'data': intelligence
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== EXECUTIVE SUMMARY ====================

@analytics_bp.route('/api/executive-summary')
def executive_summary():
    """Get executive-level KPIs and summary metrics"""
    try:
        summary = AnalyticsService.get_executive_summary()
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== COMBINED ANALYTICS ====================

@analytics_bp.route('/api/dashboard-data')
def dashboard_data():
    """
    Get all analytics data for dashboard in one call
    Optimized for dashboard loading
    """
    try:
        date_range_days = int(request.args.get('date_range_days', 180))
        
        # Get all analytics in parallel
        executive = AnalyticsService.get_executive_summary()
        supplier_perf = AnalyticsService.get_supplier_performance(date_range_days=date_range_days)
        predictions = AnalyticsService.predict_delivery_delays()
        financial = AnalyticsService.get_financial_analytics(date_range_days=date_range_days)
        delivery = AnalyticsService.get_delivery_intelligence(date_range_days=date_range_days)
        
        return jsonify({
            'success': True,
            'data': {
                'executive_summary': executive,
                'supplier_performance': supplier_perf[:10],  # Top 10 suppliers
                'delay_predictions': predictions[:10],  # Top 10 risks
                'financial_analytics': financial,
                'delivery_intelligence': delivery
            },
            'generated_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== SPECIFIC INSIGHTS ====================

@analytics_bp.route('/api/insights/top-risks')
def top_risks():
    """Get top delivery risks requiring immediate attention"""
    try:
        predictions = AnalyticsService.predict_delivery_delays()
        high_risk = [p for p in predictions if p['risk_score'] >= 70]
        
        return jsonify({
            'success': True,
            'data': high_risk[:5],  # Top 5 high-risk items
            'count': len(high_risk)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/api/insights/best-suppliers')
def best_suppliers():
    """Get top-performing suppliers"""
    try:
        suppliers = AnalyticsService.get_supplier_performance()
        best_performers = [s for s in suppliers if s['risk_score'] < 40][:5]
        
        return jsonify({
            'success': True,
            'data': best_performers,
            'count': len(best_performers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/api/insights/worst-suppliers')
def worst_suppliers():
    """Get worst-performing suppliers requiring attention"""
    try:
        suppliers = AnalyticsService.get_supplier_performance()
        poor_performers = [s for s in suppliers if s['risk_score'] >= 70]
        
        return jsonify({
            'success': True,
            'data': poor_performers,
            'count': len(poor_performers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/api/insights/payment-alerts')
def payment_alerts():
    """Get payment alerts and upcoming obligations"""
    try:
        financial = AnalyticsService.get_financial_analytics()
        cash_flow = financial['cash_flow']
        
        alerts = []
        
        if cash_flow['overdue'] > 0:
            alerts.append({
                'type': 'danger',
                'message': f"Overdue payments: {cash_flow['overdue']:,.2f} AED",
                'amount': cash_flow['overdue']
            })
        
        if cash_flow['next_30_days'] > 100000:
            alerts.append({
                'type': 'warning',
                'message': f"High upcoming payments (30 days): {cash_flow['next_30_days']:,.2f} AED",
                'amount': cash_flow['next_30_days']
            })
        
        return jsonify({
            'success': True,
            'data': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
