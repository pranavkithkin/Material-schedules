"""
Analytics Service - Advanced analytics and business intelligence
Provides supplier performance, predictive analytics, financial insights, and delivery intelligence
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case
from models import db
from models.purchase_order import PurchaseOrder
from models.delivery import Delivery
from models.payment import Payment
from models.material import Material
import statistics


class AnalyticsService:
    """Service for advanced analytics and business intelligence"""
    
    # ==================== SUPPLIER PERFORMANCE ====================
    
    @staticmethod
    def get_supplier_performance(supplier_name=None, date_range_days=180):
        """
        Calculate comprehensive supplier performance metrics
        
        Args:
            supplier_name: Optional specific supplier to analyze
            date_range_days: Number of days to look back (default 180 = 6 months)
            
        Returns:
            List of supplier performance dictionaries with metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        # Base query
        query = db.session.query(
            PurchaseOrder.supplier_name,
            func.count(PurchaseOrder.id).label('total_orders'),
            func.sum(PurchaseOrder.total_amount).label('total_value'),
            func.count(case((PurchaseOrder.po_status == 'Released', 1))).label('released_orders')
        ).filter(
            PurchaseOrder.po_date >= cutoff_date
        ).group_by(PurchaseOrder.supplier_name)
        
        if supplier_name:
            query = query.filter(PurchaseOrder.supplier_name == supplier_name)
        
        supplier_data = query.all()
        
        results = []
        for supplier in supplier_data:
            # Get delivery metrics
            delivery_metrics = AnalyticsService._calculate_delivery_metrics(
                supplier.supplier_name, cutoff_date
            )
            
            # Calculate risk score
            risk_score = AnalyticsService._calculate_risk_score(
                supplier.supplier_name, delivery_metrics
            )
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = '🔴 High'
                risk_color = 'red'
            elif risk_score >= 40:
                risk_level = '🟡 Medium'
                risk_color = 'yellow'
            else:
                risk_level = '🟢 Low'
                risk_color = 'green'
            
            results.append({
                'supplier_name': supplier.supplier_name,
                'total_orders': supplier.total_orders,
                'released_orders': supplier.released_orders,
                'total_value': round(supplier.total_value or 0, 2),
                'on_time_delivery_rate': delivery_metrics['on_time_rate'],
                'average_delay_days': delivery_metrics['avg_delay'],
                'completed_deliveries': delivery_metrics['completed'],
                'pending_deliveries': delivery_metrics['pending'],
                'delayed_deliveries': delivery_metrics['delayed'],
                'quality_score': delivery_metrics['quality_score'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_color': risk_color,
                'performance_trend': delivery_metrics['trend']
            })
        
        # Sort by risk score (lowest first = best performers)
        results.sort(key=lambda x: x['risk_score'])
        
        return results
    
    @staticmethod
    def _calculate_delivery_metrics(supplier_name, cutoff_date):
        """Calculate delivery-specific metrics for a supplier"""
        # Get all deliveries for this supplier
        deliveries = db.session.query(Delivery).join(
            PurchaseOrder, Delivery.po_id == PurchaseOrder.id
        ).filter(
            PurchaseOrder.supplier_name == supplier_name,
            PurchaseOrder.po_date >= cutoff_date
        ).all()
        
        if not deliveries:
            return {
                'on_time_rate': 0,
                'avg_delay': 0,
                'completed': 0,
                'pending': 0,
                'delayed': 0,
                'quality_score': 0,
                'trend': 'neutral'
            }
        
        total = len(deliveries)
        completed = sum(1 for d in deliveries if d.delivery_status in ['Delivered', 'Partial'])
        pending = sum(1 for d in deliveries if d.delivery_status == 'Pending')
        delayed = sum(1 for d in deliveries if d.is_delayed)
        on_time = completed - sum(1 for d in deliveries if d.is_delayed and d.delivery_status in ['Delivered', 'Partial'])
        
        on_time_rate = round((on_time / completed * 100) if completed > 0 else 0, 1)
        
        # Calculate average delay (only for delayed deliveries)
        delay_days = [d.delay_days for d in deliveries if d.is_delayed and d.delay_days]
        avg_delay = round(statistics.mean(delay_days), 1) if delay_days else 0
        
        # Quality score (inverse of delay rate + completion rate)
        quality_score = round((on_time_rate * 0.7) + ((completed / total * 100) * 0.3), 1)
        
        # Trend analysis (compare recent vs older deliveries)
        mid_point = len(deliveries) // 2
        if mid_point > 0:
            recent_deliveries = deliveries[:mid_point]
            older_deliveries = deliveries[mid_point:]
            
            recent_delay_rate = sum(1 for d in recent_deliveries if d.is_delayed) / len(recent_deliveries)
            older_delay_rate = sum(1 for d in older_deliveries if d.is_delayed) / len(older_deliveries)
            
            if recent_delay_rate < older_delay_rate - 0.1:
                trend = 'improving'
            elif recent_delay_rate > older_delay_rate + 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'neutral'
        
        return {
            'on_time_rate': on_time_rate,
            'avg_delay': avg_delay,
            'completed': completed,
            'pending': pending,
            'delayed': delayed,
            'quality_score': quality_score,
            'trend': trend
        }
    
    @staticmethod
    def _calculate_risk_score(supplier_name, delivery_metrics):
        """
        Calculate comprehensive risk score (0-100, higher = riskier)
        
        Factors:
        - Delay rate (40% weight)
        - Average delay days (30% weight)
        - Order completion rate (20% weight)
        - Performance trend (10% weight)
        """
        # Factor 1: Delay rate (40% weight)
        delay_rate = 100 - delivery_metrics['on_time_rate']  # Invert on-time rate
        delay_score = (delay_rate / 100) * 40
        
        # Factor 2: Average delay days (30% weight)
        # Cap at 10 days for scoring purposes
        avg_delay = min(delivery_metrics['avg_delay'], 10)
        delay_days_score = (avg_delay / 10) * 30
        
        # Factor 3: Order completion rate (20% weight)
        total_deliveries = delivery_metrics['completed'] + delivery_metrics['pending']
        completion_rate = (delivery_metrics['completed'] / total_deliveries) if total_deliveries > 0 else 1
        completion_score = (1 - completion_rate) * 20
        
        # Factor 4: Performance trend (10% weight)
        trend_scores = {
            'improving': 0,
            'stable': 5,
            'neutral': 5,
            'declining': 10
        }
        trend_score = trend_scores.get(delivery_metrics['trend'], 5)
        
        total_score = delay_score + delay_days_score + completion_score + trend_score
        
        return round(total_score, 1)
    
    # ==================== PREDICTIVE ANALYTICS ====================
    
    @staticmethod
    def predict_delivery_delays(po_id=None):
        """
        Predict potential delivery delays based on historical patterns
        
        Args:
            po_id: Optional specific PO to analyze, if None analyzes all pending
            
        Returns:
            List of predictions with risk scores and recommendations
        """
        # Get pending deliveries
        query = db.session.query(Delivery, PurchaseOrder).join(
            PurchaseOrder, Delivery.po_id == PurchaseOrder.id
        ).filter(
            Delivery.delivery_status.in_(['Pending', 'Partial']),
            Delivery.actual_delivery_date.is_(None)
        )
        
        if po_id:
            query = query.filter(PurchaseOrder.id == po_id)
        
        pending_deliveries = query.all()
        
        predictions = []
        for delivery, po in pending_deliveries:
            # Get supplier historical performance
            supplier_history = AnalyticsService._calculate_delivery_metrics(
                po.supplier_name, datetime.utcnow() - timedelta(days=365)
            )
            
            # Calculate prediction
            prediction = AnalyticsService._predict_delay(delivery, po, supplier_history)
            predictions.append(prediction)
        
        # Sort by risk score (highest first)
        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return predictions
    
    @staticmethod
    def _predict_delay(delivery, po, supplier_history):
        """Predict delay for a specific delivery"""
        risk_factors = []
        risk_score = 0
        
        # Factor 1: Supplier historical delay rate
        delay_rate = 100 - supplier_history['on_time_rate']
        if delay_rate > 50:
            risk_score += 30
            risk_factors.append(f"Supplier has {delay_rate:.0f}% delay rate")
        elif delay_rate > 30:
            risk_score += 20
            risk_factors.append(f"Supplier has {delay_rate:.0f}% delay rate")
        
        # Factor 2: Average historical delay
        if supplier_history['avg_delay'] > 5:
            risk_score += 25
            risk_factors.append(f"Average delay: {supplier_history['avg_delay']} days")
        elif supplier_history['avg_delay'] > 2:
            risk_score += 15
            risk_factors.append(f"Average delay: {supplier_history['avg_delay']} days")
        
        # Factor 3: Performance trend
        if supplier_history['trend'] == 'declining':
            risk_score += 20
            risk_factors.append("Supplier performance declining recently")
        
        # Factor 4: High order value (more risk)
        if po.total_amount > 100000:
            risk_score += 15
            risk_factors.append("High-value order (>100K)")
        
        # Factor 5: Already approaching expected date
        if delivery.expected_delivery_date:
            days_until_delivery = (delivery.expected_delivery_date - datetime.utcnow()).days
            if days_until_delivery < 3:
                risk_score += 10
                risk_factors.append(f"Delivery due in {days_until_delivery} days")
        
        # Calculate predicted delay
        if risk_score >= 70:
            predicted_delay_days = round(supplier_history['avg_delay'] * 1.5)
            confidence = 85
        elif risk_score >= 40:
            predicted_delay_days = round(supplier_history['avg_delay'])
            confidence = 70
        else:
            predicted_delay_days = 0
            confidence = 60
        
        # Generate recommendation
        if risk_score >= 70:
            recommendation = "Immediate follow-up required - High risk of delay"
        elif risk_score >= 40:
            recommendation = "Schedule follow-up call - Monitor closely"
        else:
            recommendation = "Low risk - Continue standard monitoring"
        
        return {
            'po_id': po.id,
            'po_ref': po.po_ref,
            'supplier_name': po.supplier_name,
            'expected_date': delivery.expected_delivery_date.isoformat() if delivery.expected_delivery_date else None,
            'predicted_delay_days': predicted_delay_days,
            'risk_score': min(risk_score, 100),
            'confidence': confidence,
            'risk_factors': risk_factors,
            'recommendation': recommendation,
            'material_type': po.material.material_type if po.material else 'Unknown'
        }
    
    # ==================== FINANCIAL ANALYTICS ====================
    
    @staticmethod
    def get_financial_analytics(date_range_days=180):
        """
        Get comprehensive financial analytics
        
        Returns:
            Dictionary with payment trends, budget tracking, cash flow forecast
        """
        cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        # Payment trends by month
        payment_trends = AnalyticsService._get_payment_trends(cutoff_date)
        
        # Budget vs Actual
        budget_tracking = AnalyticsService._get_budget_tracking(cutoff_date)
        
        # Cash flow forecast
        cash_flow_data = AnalyticsService._get_cash_flow_forecast()
        
        # Supplier payment analysis
        supplier_payments = AnalyticsService._get_supplier_payment_analysis(cutoff_date)
        
        # Return structure that matches frontend expectations
        return {
            'payment_trends': payment_trends,
            'budget': {
                'total': budget_tracking['total_planned'],
                'spent': budget_tracking['total_paid'],
                'remaining': budget_tracking['remaining_budget'],
                'utilization_rate': budget_tracking['utilization_rate']
            },
            'cash_flow': {
                'overdue': cash_flow_data['overdue'],
                'next_30_days': cash_flow_data['next_30_days'],
                'next_60_days': cash_flow_data['next_60_days'],
                'next_90_days': cash_flow_data['next_90_days'],
                'total_forecast': cash_flow_data['total_forecast']
            },
            'supplier_payments': supplier_payments
        }
    
    @staticmethod
    def _get_payment_trends(cutoff_date):
        """Get monthly payment trends"""
        payments = db.session.query(
            func.strftime('%Y-%m', Payment.payment_date).label('month'),
            func.sum(Payment.paid_amount).label('total_paid'),
            func.count(Payment.id).label('payment_count')
        ).filter(
            Payment.payment_date >= cutoff_date,
            Payment.payment_date.isnot(None)
        ).group_by('month').order_by('month').all()
        
        return [{
            'month': p.month,
            'total_paid': round(p.total_paid or 0, 2),
            'payment_count': p.payment_count
        } for p in payments]
    
    @staticmethod
    def _get_budget_tracking(cutoff_date):
        """Calculate budget vs actual spending"""
        # Total PO value (budget/planned)
        total_planned = db.session.query(
            func.sum(PurchaseOrder.total_amount)
        ).filter(
            PurchaseOrder.po_date >= cutoff_date
        ).scalar() or 0
        
        # Total paid (actual)
        total_paid = db.session.query(
            func.sum(Payment.paid_amount)
        ).filter(
            Payment.payment_date >= cutoff_date
        ).scalar() or 0
        
        # Pending payments
        total_pending = db.session.query(
            func.sum(Payment.total_amount - Payment.paid_amount)
        ).filter(
            Payment.payment_status.in_(['Pending', 'Partial'])
        ).scalar() or 0
        
        utilization_rate = round((total_paid / total_planned * 100) if total_planned > 0 else 0, 1)
        
        return {
            'total_planned': round(total_planned, 2),
            'total_paid': round(total_paid, 2),
            'total_pending': round(total_pending, 2),
            'utilization_rate': utilization_rate,
            'remaining_budget': round(total_planned - total_paid, 2)
        }
    
    @staticmethod
    def _get_cash_flow_forecast():
        """Forecast upcoming payment obligations"""
        # Get pending payments
        pending_payments = db.session.query(
            Payment,
            PurchaseOrder
        ).join(
            PurchaseOrder, Payment.po_id == PurchaseOrder.id
        ).filter(
            Payment.payment_status.in_(['Pending', 'Partial'])
        ).all()
        
        # Group by expected timeline
        next_30_days = 0
        next_60_days = 0
        next_90_days = 0
        overdue = 0
        
        today = datetime.utcnow()
        
        for payment, po in pending_payments:
            amount_due = payment.total_amount - payment.paid_amount
            
            # Use expected delivery date as proxy for payment due date
            if po.expected_delivery_date:
                days_until = (po.expected_delivery_date - today).days
                
                if days_until < 0:
                    overdue += amount_due
                elif days_until <= 30:
                    next_30_days += amount_due
                elif days_until <= 60:
                    next_60_days += amount_due
                elif days_until <= 90:
                    next_90_days += amount_due
        
        return {
            'overdue': round(overdue, 2),
            'next_30_days': round(next_30_days, 2),
            'next_60_days': round(next_60_days, 2),
            'next_90_days': round(next_90_days, 2),
            'total_forecast': round(overdue + next_30_days + next_60_days + next_90_days, 2)
        }
    
    @staticmethod
    def _get_supplier_payment_analysis(cutoff_date):
        """Analyze payment patterns by supplier"""
        supplier_payments = db.session.query(
            PurchaseOrder.supplier_name,
            func.sum(Payment.paid_amount).label('total_paid'),
            func.sum(Payment.total_amount - Payment.paid_amount).label('outstanding'),
            func.count(Payment.id).label('payment_count')
        ).join(
            PurchaseOrder, Payment.po_id == PurchaseOrder.id
        ).filter(
            Payment.created_at >= cutoff_date
        ).group_by(
            PurchaseOrder.supplier_name
        ).order_by(
            func.sum(Payment.paid_amount).desc()
        ).limit(10).all()
        
        return [{
            'supplier_name': sp.supplier_name,
            'total_paid': round(sp.total_paid or 0, 2),
            'outstanding': round(sp.outstanding or 0, 2),
            'payment_count': sp.payment_count
        } for sp in supplier_payments]
    
    # ==================== DELIVERY INTELLIGENCE ====================
    
    @staticmethod
    def get_delivery_intelligence(date_range_days=180):
        """Get comprehensive delivery insights and metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        # Average delivery time by material type
        material_lead_times = AnalyticsService._get_material_lead_times(cutoff_date)
        
        # Delivery volume trends
        delivery_trends = AnalyticsService._get_delivery_trends(cutoff_date)
        
        # On-time delivery metrics
        on_time_metrics = AnalyticsService._get_on_time_metrics(cutoff_date)
        
        # Delay analysis
        delay_analysis = AnalyticsService._get_delay_analysis(cutoff_date)
        
        return {
            'material_lead_times': material_lead_times,
            'delivery_trends': delivery_trends,
            'on_time_metrics': on_time_metrics,
            'delay_analysis': delay_analysis
        }
    
    @staticmethod
    def _get_material_lead_times(cutoff_date):
        """Calculate average lead time by material type"""
        lead_times = db.session.query(
            Material.material_type,
            func.avg(
                func.julianday(Delivery.actual_delivery_date) - 
                func.julianday(PurchaseOrder.po_date)
            ).label('avg_lead_time'),
            func.count(Delivery.id).label('delivery_count')
        ).join(
            PurchaseOrder, Delivery.po_id == PurchaseOrder.id
        ).join(
            Material, PurchaseOrder.material_id == Material.id
        ).filter(
            Delivery.actual_delivery_date.isnot(None),
            PurchaseOrder.po_date >= cutoff_date
        ).group_by(
            Material.material_type
        ).all()
        
        return [{
            'material_type': lt.material_type,
            'avg_lead_time_days': round(lt.avg_lead_time or 0, 1),
            'delivery_count': lt.delivery_count
        } for lt in lead_times]
    
    @staticmethod
    def _get_delivery_trends(cutoff_date):
        """Get monthly delivery volume trends"""
        trends = db.session.query(
            func.strftime('%Y-%m', Delivery.created_at).label('month'),
            func.count(Delivery.id).label('total_deliveries'),
            func.count(case((Delivery.delivery_status == 'Delivered', 1))).label('completed'),
            func.count(case((Delivery.is_delayed == True, 1))).label('delayed')
        ).filter(
            Delivery.created_at >= cutoff_date
        ).group_by('month').order_by('month').all()
        
        return [{
            'month': t.month,
            'total_deliveries': t.total_deliveries,
            'completed': t.completed,
            'delayed': t.delayed,
            'on_time_rate': round(((t.completed - t.delayed) / t.completed * 100) if t.completed > 0 else 0, 1)
        } for t in trends]
    
    @staticmethod
    def _get_on_time_metrics(cutoff_date):
        """Calculate overall on-time delivery metrics"""
        total_deliveries = db.session.query(func.count(Delivery.id)).filter(
            Delivery.created_at >= cutoff_date,
            Delivery.delivery_status.in_(['Delivered', 'Partial'])
        ).scalar() or 0
        
        delayed_deliveries = db.session.query(func.count(Delivery.id)).filter(
            Delivery.created_at >= cutoff_date,
            Delivery.is_delayed == True,
            Delivery.delivery_status.in_(['Delivered', 'Partial'])
        ).scalar() or 0
        
        on_time = total_deliveries - delayed_deliveries
        on_time_rate = round((on_time / total_deliveries * 100) if total_deliveries > 0 else 0, 1)
        
        return {
            'total_deliveries': total_deliveries,
            'on_time': on_time,
            'delayed': delayed_deliveries,
            'on_time_rate': on_time_rate
        }
    
    @staticmethod
    def _get_delay_analysis(cutoff_date):
        """Analyze delay patterns and reasons"""
        delays = db.session.query(
            Delivery.delay_reason,
            func.count(Delivery.id).label('count'),
            func.avg(Delivery.delay_days).label('avg_delay_days')
        ).filter(
            Delivery.is_delayed == True,
            Delivery.created_at >= cutoff_date,
            Delivery.delay_reason.isnot(None)
        ).group_by(
            Delivery.delay_reason
        ).order_by(
            func.count(Delivery.id).desc()
        ).limit(10).all()
        
        return [{
            'reason': d.delay_reason,
            'count': d.count,
            'avg_delay_days': round(d.avg_delay_days or 0, 1)
        } for d in delays]
    
    # ==================== EXECUTIVE SUMMARY ====================
    
    @staticmethod
    def get_executive_summary():
        """Get high-level KPIs for executive dashboard"""
        # Total project value
        total_project_value = db.session.query(
            func.sum(PurchaseOrder.total_amount)
        ).scalar() or 0
        
        # Completion metrics
        total_pos = db.session.query(func.count(PurchaseOrder.id)).scalar() or 0
        released_pos = db.session.query(func.count(PurchaseOrder.id)).filter(
            PurchaseOrder.po_status == 'Released'
        ).scalar() or 0
        
        completion_rate = round((released_pos / total_pos * 100) if total_pos > 0 else 0, 1)
        
        # Delivery metrics
        total_deliveries = db.session.query(func.count(Delivery.id)).scalar() or 0
        completed_deliveries = db.session.query(func.count(Delivery.id)).filter(
            Delivery.delivery_status.in_(['Delivered', 'Partial'])
        ).scalar() or 0
        delayed_deliveries = db.session.query(func.count(Delivery.id)).filter(
            Delivery.is_delayed == True
        ).scalar() or 0
        
        on_time_rate = round(
            ((completed_deliveries - delayed_deliveries) / completed_deliveries * 100) 
            if completed_deliveries > 0 else 0, 1
        )
        
        # Budget utilization
        total_paid = db.session.query(func.sum(Payment.paid_amount)).scalar() or 0
        budget_utilization = round((total_paid / total_project_value * 100) if total_project_value > 0 else 0, 1)
        
        # Active suppliers
        active_suppliers = db.session.query(
            func.count(func.distinct(PurchaseOrder.supplier_name))
        ).filter(
            PurchaseOrder.po_status == 'Released'
        ).scalar() or 0
        
        # Pending actions
        pending_deliveries = total_deliveries - completed_deliveries
        overdue_deliveries = db.session.query(func.count(Delivery.id)).filter(
            Delivery.is_delayed == True,
            Delivery.delivery_status == 'Pending'
        ).scalar() or 0
        
        # High risk items (pending deliveries that are overdue)
        high_risk_items = overdue_deliveries
        
        return {
            # Frontend expects these exact field names
            'total_value': round(total_project_value, 2),
            'active_pos': released_pos,
            'pending_deliveries': pending_deliveries,
            'high_risk_items': high_risk_items,
            
            # Additional metrics
            'completion_rate': completion_rate,
            'on_time_delivery_rate': on_time_rate,
            'budget_utilization': budget_utilization,
            'active_suppliers': active_suppliers,
            'total_pos': total_pos,
            'released_pos': released_pos,
            'overdue_deliveries': overdue_deliveries,
            'delayed_deliveries': delayed_deliveries
        }
