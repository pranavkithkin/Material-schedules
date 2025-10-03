"""
Chat Service for natural language queries
Processes user questions and returns relevant data
"""

import json
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery
from config import Config
from sqlalchemy import or_, and_

# Import AI libraries conditionally
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class ChatService:
    """Service for processing natural language queries"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize Claude if available
        if ANTHROPIC_AVAILABLE and Config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.openai_client = openai
    
    def process_query(self, query):
        """Process a natural language query"""
        query_lower = query.lower()
        
        # Simple keyword-based routing (can be enhanced with AI)
        if any(word in query_lower for word in ['delayed', 'late', 'overdue']):
            return self._get_delayed_deliveries()
        
        elif any(word in query_lower for word in ['pending', 'waiting', 'not delivered']):
            return self._get_pending_deliveries()
        
        elif any(word in query_lower for word in ['payment', 'paid', 'invoice']):
            return self._get_payment_status()
        
        elif any(word in query_lower for word in ['approved', 'approval']):
            return self._get_approval_status()
        
        elif any(word in query_lower for word in ['material', 'materials']):
            return self._get_materials_info(query_lower)
        
        elif any(word in query_lower for word in ['po', 'purchase order', 'orders']):
            return self._get_po_info()
        
        else:
            # Use AI to interpret complex queries
            return self._ai_query(query)
    
    def _get_delayed_deliveries(self):
        """Get delayed deliveries"""
        deliveries = Delivery.query.filter_by(is_delayed=True).all()
        
        if not deliveries:
            return {
                'answer': 'No delayed deliveries at the moment.',
                'data': [],
                'source': 'deliveries table'
            }
        
        data = []
        for delivery in deliveries:
            data.append({
                'material': delivery.purchase_order.material.material_type if delivery.purchase_order and delivery.purchase_order.material else 'Unknown',
                'po_ref': delivery.purchase_order.po_ref if delivery.purchase_order else 'Unknown',
                'expected_date': delivery.expected_delivery_date.strftime('%Y-%m-%d') if delivery.expected_delivery_date else 'N/A',
                'delay_days': delivery.delay_days,
                'status': delivery.delivery_status
            })
        
        return {
            'answer': f'Found {len(deliveries)} delayed deliveries.',
            'data': data,
            'source': 'deliveries table'
        }
    
    def _get_pending_deliveries(self):
        """Get pending deliveries"""
        deliveries = Delivery.query.filter(
            Delivery.delivery_status.in_(['Pending', 'In Transit'])
        ).all()
        
        if not deliveries:
            return {
                'answer': 'No pending deliveries.',
                'data': [],
                'source': 'deliveries table'
            }
        
        data = []
        for delivery in deliveries:
            data.append({
                'material': delivery.purchase_order.material.material_type if delivery.purchase_order and delivery.purchase_order.material else 'Unknown',
                'po_ref': delivery.purchase_order.po_ref if delivery.purchase_order else 'Unknown',
                'expected_date': delivery.expected_delivery_date.strftime('%Y-%m-%d') if delivery.expected_delivery_date else 'N/A',
                'status': delivery.delivery_status,
                'tracking': delivery.tracking_number or 'N/A'
            })
        
        return {
            'answer': f'Found {len(deliveries)} pending deliveries.',
            'data': data,
            'source': 'deliveries table'
        }
    
    def _get_payment_status(self):
        """Get payment status overview"""
        payments = Payment.query.all()
        
        total_amount = sum(p.total_amount for p in payments)
        paid_amount = sum(p.paid_amount for p in payments)
        pending_count = sum(1 for p in payments if p.payment_status == 'Pending')
        
        return {
            'answer': f'Payment Overview: Total Amount: {Config.CURRENCY} {total_amount:,.2f}, Paid: {Config.CURRENCY} {paid_amount:,.2f}, Pending Payments: {pending_count}',
            'data': {
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'pending_payments': pending_count,
                'payment_percentage': (paid_amount / total_amount * 100) if total_amount > 0 else 0
            },
            'source': 'payments table'
        }
    
    def _get_approval_status(self):
        """Get material approval status"""
        materials = Material.query.all()
        
        status_counts = {}
        for material in materials:
            status = material.approval_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'answer': f'Material Approval Status: {", ".join([f"{k}: {v}" for k, v in status_counts.items()])}',
            'data': status_counts,
            'source': 'materials table'
        }
    
    def _get_materials_info(self, query):
        """Get information about specific materials"""
        # Try to extract material name from query
        materials = Material.query.all()
        
        # Simple search in material names
        matching = []
        for material in materials:
            if any(word in material.material_type.lower() for word in query.split()):
                matching.append(material)
        
        if not matching:
            return {
                'answer': f'Found {len(materials)} materials in total. Try asking about a specific material like "DB" or "VRF System".',
                'data': [{'material_type': m.material_type, 'approval_status': m.approval_status} for m in materials[:10]],
                'source': 'materials table'
            }
        
        data = []
        for material in matching:
            data.append({
                'material_type': material.material_type,
                'approval_status': material.approval_status,
                'quantity': material.quantity,
                'unit': material.unit
            })
        
        return {
            'answer': f'Found {len(matching)} matching materials.',
            'data': data,
            'source': 'materials table'
        }
    
    def _get_po_info(self):
        """Get purchase order information"""
        pos = PurchaseOrder.query.all()
        
        status_counts = {}
        total_value = 0
        
        for po in pos:
            status = po.po_status
            status_counts[status] = status_counts.get(status, 0) + 1
            total_value += po.total_amount
        
        return {
            'answer': f'Purchase Orders: Total {len(pos)}, Total Value: {Config.CURRENCY} {total_value:,.2f}',
            'data': {
                'total_pos': len(pos),
                'total_value': total_value,
                'by_status': status_counts
            },
            'source': 'purchase_orders table'
        }
    
    def _ai_query(self, query):
        """Use AI to interpret and answer complex queries"""
        # Get database context
        context = self._get_database_context()
        
        prompt = f"""You are a helpful assistant for a construction material delivery tracking system.
        
Database Context:
{json.dumps(context, indent=2)}

User Query: {query}

Please provide a helpful answer based on the database context. If you don't have enough information, say so.
Format your response as JSON with these fields:
- answer: Your natural language answer
- data: Any relevant data points (can be empty)
- source: Which tables you used

Response:"""
        
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                return self._parse_ai_response(content)
            except Exception as e:
                print(f"AI query error: {e}")
        
        # Fallback response
        return {
            'answer': 'I\'m not sure how to answer that question. Try asking about delayed deliveries, pending materials, payment status, or specific materials.',
            'data': {},
            'source': 'fallback'
        }
    
    def _get_database_context(self):
        """Get summary of database for AI context"""
        return {
            'total_materials': Material.query.count(),
            'total_pos': PurchaseOrder.query.count(),
            'total_deliveries': Delivery.query.count(),
            'delayed_deliveries': Delivery.query.filter_by(is_delayed=True).count(),
            'pending_deliveries': Delivery.query.filter(
                Delivery.delivery_status.in_(['Pending', 'In Transit'])
            ).count()
        }
    
    def _parse_ai_response(self, response_text):
        """Parse AI response"""
        try:
            # Try to find JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Return as plain answer
                return {
                    'answer': response_text,
                    'data': {},
                    'source': 'ai'
                }
        except json.JSONDecodeError:
            return {
                'answer': response_text,
                'data': {},
                'source': 'ai'
            }
