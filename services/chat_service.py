"""
Chat Service for natural language queries and conversational data entry
Supports multi-turn conversations with context tracking
"""

import json
import re
from datetime import datetime, timedelta
from models import db
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery
from models.conversation import Conversation, ConversationMessage
from config import Config
from sqlalchemy import or_, and_
import uuid

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


class ConversationalChatService:
    """Enhanced chat service with conversation tracking and data entry"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize Claude if available
        if ANTHROPIC_AVAILABLE and Config.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                openai.api_key = Config.OPENAI_API_KEY
                self.openai_client = openai
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def process_message(self, user_message, conversation_id=None, user_id=None):
        """
        Process a message with conversation context.
        Supports both queries and data entry.
        """
        # Get or create conversation
        if conversation_id:
            conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()
            if not conversation:
                conversation = self._create_conversation(user_id)
        else:
            conversation = self._create_conversation(user_id)
        
        # Add user message to conversation
        conversation.add_message('user', user_message)
        
        # Check if this is an action command first (NEW)
        action_response = self._detect_and_execute_action(user_message)
        if action_response:
            conversation.add_message('assistant', action_response['answer'], extra_data=action_response.get('metadata', {}))
            db.session.commit()
            action_response['conversation_id'] = conversation.conversation_id
            return action_response
        
        # Determine intent if not set
        if not conversation.intent:
            conversation.intent = self._detect_intent(user_message)
        
        # Process based on intent
        if conversation.intent and conversation.intent.startswith('add_'):
            response = self._handle_data_entry(conversation, user_message)
        else:
            response = self._handle_query(conversation, user_message)
        
        # Add assistant response to conversation
        conversation.add_message('assistant', response['answer'], extra_data=response.get('metadata', {}))
        
        # Save conversation
        db.session.commit()
        
        # Include conversation context in response
        response['conversation_id'] = conversation.conversation_id
        response['intent'] = conversation.intent
        response['context_data'] = conversation.context_data
        
        return response
    
    def _create_conversation(self, user_id=None):
        """Create a new conversation"""
        conversation = Conversation(
            conversation_id=str(uuid.uuid4()),
            user_id=user_id,
            status='active'
        )
        db.session.add(conversation)
        db.session.flush()
        return conversation
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Data entry intents
        if any(word in message_lower for word in ['add', 'create', 'new']):
            if any(word in message_lower for word in ['po', 'purchase order', 'order']):
                return 'add_po'
            elif any(word in message_lower for word in ['payment', 'invoice']):
                return 'add_payment'
            elif any(word in message_lower for word in ['delivery', 'shipment']):
                return 'add_delivery'
            elif any(word in message_lower for word in ['material']):
                return 'add_material'
        
        # Query intents
        return 'query'
    
    def _handle_data_entry(self, conversation, user_message):
        """Handle conversational data entry (e.g., adding PO)"""
        intent = conversation.intent
        context = conversation.context_data or {}
        
        # Extract entities from current message
        entities = self._extract_entities(user_message)
        
        # Merge entities into context
        for key, value in entities.items():
            if value is not None:
                context[key] = value
        
        conversation.context_data = context
        
        # Check what's still missing based on intent
        if intent == 'add_po':
            return self._handle_add_po(conversation, context, entities)
        elif intent == 'add_payment':
            return self._handle_add_payment(conversation, context, entities)
        elif intent == 'add_delivery':
            return self._handle_add_delivery(conversation, context, entities)
        else:
            return {
                'answer': "I can help you add a Purchase Order, Payment, or Delivery. What would you like to create?",
                'action': 'clarify_intent',
                'metadata': {}
            }
    
    def _handle_add_po(self, conversation, context, entities):
        """Handle adding a Purchase Order conversationally"""
        required_fields = {
            'po_ref': 'PO number',
            'supplier_name': 'supplier name',
            'total_amount': 'total amount',
            'material_id': 'material type'
        }
        
        # Check what's missing
        missing = [field for field in required_fields.keys() if field not in context or context[field] is None]
        
        if missing:
            # Ask for the next missing field
            next_field = missing[0]
            field_name = required_fields[next_field]
            
            # Special handling for material_id
            if next_field == 'material_id':
                materials = Material.query.limit(10).all()
                material_list = ', '.join([m.material_type for m in materials])
                return {
                    'answer': f"What type of material is this for? (e.g., {material_list})",
                    'action': 'collect_field',
                    'field': next_field,
                    'metadata': {'missing_fields': missing}
                }
            
            return {
                'answer': f"Got it! What's the {field_name}?",
                'action': 'collect_field',
                'field': next_field,
                'metadata': {'missing_fields': missing, 'collected': list(context.keys())}
            }
        
        # All required fields collected - confirm before creating
        if not context.get('confirmed'):
            summary = f"""
✅ Ready to create Purchase Order:
- PO Number: {context['po_ref']}
- Supplier: {context['supplier_name']}
- Amount: {Config.CURRENCY} {context['total_amount']:,.2f}
- Material: {self._get_material_name(context['material_id'])}
{f"- Expected Delivery: {context.get('expected_delivery_date', 'Not specified')}" if context.get('expected_delivery_date') else ''}

Type 'confirm' to create this PO, or 'cancel' to abort.
"""
            return {
                'answer': summary,
                'action': 'confirm',
                'metadata': {'pending_po': context}
            }
        
        # Create the PO
        try:
            po = self._create_purchase_order(context)
            conversation.complete()
            
            return {
                'answer': f"✅ Purchase Order {po.po_ref} created successfully! (ID: {po.id})",
                'action': 'completed',
                'data': po.to_dict(),
                'metadata': {'po_id': po.id}
            }
        except Exception as e:
            return {
                'answer': f"❌ Error creating PO: {str(e)}. Please try again.",
                'action': 'error',
                'metadata': {'error': str(e)}
            }
    
    def _handle_add_payment(self, conversation, context, entities):
        """Handle adding payment conversationally"""
        required_fields = {
            'po_id': 'Purchase Order (PO number)',
            'paid_amount': 'payment amount'
        }
        
        missing = [field for field in required_fields.keys() if field not in context or context[field] is None]
        
        if missing:
            next_field = missing[0]
            field_name = required_fields[next_field]
            
            if next_field == 'po_id':
                recent_pos = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(5).all()
                po_list = ', '.join([po.po_ref for po in recent_pos])
                return {
                    'answer': f"Which Purchase Order is this payment for? (Recent POs: {po_list})",
                    'action': 'collect_field',
                    'field': next_field,
                    'metadata': {'missing_fields': missing}
                }
            
            return {
                'answer': f"What's the {field_name}?",
                'action': 'collect_field',
                'field': next_field,
                'metadata': {'missing_fields': missing}
            }
        
        # Confirm and create
        if not context.get('confirmed'):
            po = PurchaseOrder.query.get(context['po_id'])
            summary = f"""
✅ Ready to record payment:
- PO: {po.po_ref if po else 'Unknown'}
- Amount: {Config.CURRENCY} {context['paid_amount']:,.2f}
- Payment Type: {context.get('payment_type', 'Advance')}

Type 'confirm' to record this payment.
"""
            return {
                'answer': summary,
                'action': 'confirm',
                'metadata': {'pending_payment': context}
            }
        
        try:
            payment = self._create_payment(context)
            conversation.complete()
            
            return {
                'answer': f"✅ Payment of {Config.CURRENCY} {payment.paid_amount:,.2f} recorded successfully!",
                'action': 'completed',
                'data': payment.to_dict(),
                'metadata': {'payment_id': payment.id}
            }
        except Exception as e:
            return {
                'answer': f"❌ Error recording payment: {str(e)}",
                'action': 'error',
                'metadata': {'error': str(e)}
            }
    
    def _handle_add_delivery(self, conversation, context, entities):
        """Handle adding delivery conversationally"""
        return {
            'answer': "Delivery tracking is coming soon! For now, please use the web form to add deliveries.",
            'action': 'not_implemented',
            'metadata': {}
        }
    
    def _extract_entities(self, message):
        """Extract entities from message (amounts, dates, names, etc.)"""
        entities = {}
        message_lower = message.lower()
        
        # Extract amounts (with k/m suffixes) - improved patterns
        amount_patterns = [
            (r'(\d+(?:,\d{3})*)\s*(?:aed|usd|dollars?|dirhams?)', 1),  # Amount before currency
            (r'(?:aed|usd)\s*(\d+(?:,\d{3})*)', 1),  # Amount after currency
            (r'(\d+)k', 1000),  # 80k format
            (r'(\d+)\s*(?:thousand)', 1000),  # 80 thousand
        ]
        
        found_amounts = []
        for pattern, multiplier in amount_patterns:
            matches = re.finditer(pattern, message_lower)
            for match in matches:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str) * (multiplier if isinstance(multiplier, int) else 1)
                found_amounts.append(amount)
        
        # Use the largest amount found (likely the total, not quantity)
        if found_amounts:
            entities['total_amount'] = max(found_amounts)
            entities['paid_amount'] = max(found_amounts)
        
        # Extract PO number - improved pattern
        po_patterns = [
            r'po[-\s]?([a-z0-9-]+)',
            r'purchase\s+order\s+([a-z0-9-]+)',
        ]
        
        for pattern in po_patterns:
            match = re.search(pattern, message_lower)
            if match:
                po_ref = match.group(1).upper()
                # Avoid extracting "FOR" from "material for X"
                if len(po_ref) > 2 and po_ref not in ['FOR', 'FROM', 'THE']:
                    entities['po_ref'] = po_ref
                    break
        
        # Extract dates (simple patterns)
        date_patterns = {
            'tomorrow': datetime.now().date() + timedelta(days=1),
            'next week': datetime.now().date() + timedelta(days=7),
            'next monday': self._next_weekday(0),
            'next friday': self._next_weekday(4),
        }
        
        for phrase, date_value in date_patterns.items():
            if phrase in message_lower:
                entities['expected_delivery_date'] = date_value.isoformat()
                break
        
        # Extract supplier name (supports both "to supplier" and "from supplier" for natural language)
        # Note: POs are TO suppliers, but users might say "from" naturally
        to_match = re.search(r'to\s+([a-z\s&]+?)(?:\s+suppliers?|,|$|\d)', message_lower, re.IGNORECASE)
        from_match = re.search(r'from\s+([a-z\s&]+?)(?:\s+suppliers?|,|$|\d)', message_lower, re.IGNORECASE)
        
        if to_match:
            entities['supplier_name'] = to_match.group(1).strip().title()
        elif from_match:
            entities['supplier_name'] = from_match.group(1).strip().title()
        
        # Extract material type
        materials = Material.query.all()
        for material in materials:
            if material.material_type.lower() in message_lower:
                entities['material_id'] = material.id
                break
        
        # Check for confirmation keywords
        if any(word in message_lower for word in ['confirm', 'yes', 'correct', 'create']):
            entities['confirmed'] = True
        elif any(word in message_lower for word in ['cancel', 'no', 'abort', 'stop']):
            entities['cancelled'] = True
        
        return entities
    
    def _next_weekday(self, weekday):
        """Get next occurrence of weekday (0=Monday, 6=Sunday)"""
        today = datetime.now().date()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    def _get_material_name(self, material_id):
        """Get material name by ID"""
        material = Material.query.get(material_id)
        return material.material_type if material else 'Unknown'
    
    def _create_purchase_order(self, context):
        """Create a PO from context data"""
        po = PurchaseOrder(
            po_ref=context['po_ref'],
            supplier_name=context['supplier_name'],
            total_amount=context['total_amount'],
            material_id=context['material_id'],
            po_date=datetime.now().date(),
            expected_delivery_date=context.get('expected_delivery_date'),
            supplier_contact=context.get('supplier_contact'),
            supplier_email=context.get('supplier_email'),
            currency=context.get('currency', Config.CURRENCY),
            po_status='Released',
            created_by='Chat'
        )
        db.session.add(po)
        db.session.commit()
        return po
    
    def _create_payment(self, context):
        """Create a payment from context data"""
        from models.payment import Payment
        
        payment = Payment(
            po_id=context['po_id'],
            paid_amount=context['paid_amount'],
            total_amount=context.get('total_amount', context['paid_amount']),
            payment_type=context.get('payment_type', 'Advance'),
            payment_status='Partial',
            payment_date=datetime.now().date(),
            currency=context.get('currency', Config.CURRENCY),
            created_by='Chat'
        )
        payment.calculate_percentage()
        db.session.add(payment)
        db.session.commit()
        return payment
    
    def _handle_query(self, conversation, user_message):
        """Handle query with conversation context"""
        # Use the original ChatService query logic
        chat_service = ChatService()
        result = chat_service.process_query(user_message)
        
        return result
    
    def _detect_and_execute_action(self, message):
        """
        Detect and execute action commands like:
        - "change all status to approved"
        - "approve all pending materials"
        - "update delivery status to delivered"
        - "mark all as complete"
        """
        message_lower = message.lower()
        
        # Action: Change/Update approval status
        if any(word in message_lower for word in ['change', 'update', 'set', 'mark']) and \
           any(word in message_lower for word in ['status', 'approval']):
            
            # Detect target status
            target_status = None
            if 'approved' in message_lower or 'approve' in message_lower:
                target_status = 'Approved'
            elif 'pending' in message_lower:
                target_status = 'Pending'
            elif 'rejected' in message_lower or 'reject' in message_lower:
                target_status = 'Rejected'
            
            if not target_status:
                return None
            
            # Detect scope: all, specific material, or pending
            scope = 'all'
            material_filter = None
            
            if 'all' in message_lower:
                scope = 'all'
            elif 'pending' in message_lower and target_status != 'Pending':
                scope = 'pending'
            
            # Execute the action
            return self._execute_approval_status_change(target_status, scope, material_filter)
        
        # Action: Update delivery status
        if any(word in message_lower for word in ['update', 'change', 'mark']) and \
           'delivery' in message_lower:
            
            target_status = None
            if 'delivered' in message_lower or 'complete' in message_lower:
                target_status = 'Delivered'
            elif 'in transit' in message_lower or 'transit' in message_lower:
                target_status = 'In Transit'
            elif 'pending' in message_lower:
                target_status = 'Pending'
            
            if target_status:
                return self._execute_delivery_status_change(target_status)
        
        # Action: Approve/Reject specific PO
        if any(word in message_lower for word in ['approve', 'reject']) and 'po' in message_lower:
            # Extract PO reference
            po_match = re.search(r'po[-\s]?([a-z0-9-]+)', message_lower)
            if po_match:
                po_ref = po_match.group(1).upper()
                action = 'approve' if 'approve' in message_lower else 'reject'
                return self._execute_po_action(po_ref, action)
        
        return None
    
    def _execute_approval_status_change(self, target_status, scope='all', material_filter=None):
        """
        Execute approval status change for materials
        """
        try:
            # Build query based on scope
            query = Material.query
            
            if scope == 'pending':
                query = query.filter_by(approval_status='Pending')
            elif scope == 'all':
                # Change all materials
                pass
            
            materials = query.all()
            
            if not materials:
                return {
                    'answer': f"No materials found to update.",
                    'action': 'status_change',
                    'success': False,
                    'metadata': {'count': 0}
                }
            
            # Update all matching materials
            count = 0
            updated_materials = []
            
            for material in materials:
                old_status = material.approval_status
                material.approval_status = target_status
                material.updated_at = datetime.now()
                count += 1
                updated_materials.append({
                    'material_type': material.material_type,
                    'old_status': old_status,
                    'new_status': target_status
                })
            
            db.session.commit()
            
            # Get updated counts
            status_counts = self._get_approval_status_counts()
            
            return {
                'answer': f"✅ Successfully changed {count} material(s) to '{target_status}'!\n\n" + 
                         f"📊 Current Status:\n" +
                         f"- Approved: {status_counts.get('Approved', 0)}\n" +
                         f"- Pending: {status_counts.get('Pending', 0)}\n" +
                         f"- Rejected: {status_counts.get('Rejected', 0)}",
                'action': 'status_change',
                'success': True,
                'data': {
                    'updated_count': count,
                    'target_status': target_status,
                    'scope': scope,
                    'updated_materials': updated_materials[:10],  # First 10 for display
                    'current_counts': status_counts
                },
                'metadata': {
                    'action_type': 'bulk_status_update',
                    'count': count,
                    'status': target_status
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'answer': f"❌ Error updating status: {str(e)}",
                'action': 'status_change',
                'success': False,
                'metadata': {'error': str(e)}
            }
    
    def _execute_delivery_status_change(self, target_status):
        """Execute delivery status change"""
        try:
            deliveries = Delivery.query.filter(
                Delivery.delivery_status.in_(['Pending', 'In Transit'])
            ).all()
            
            if not deliveries:
                return {
                    'answer': "No pending deliveries to update.",
                    'action': 'delivery_update',
                    'success': False
                }
            
            count = 0
            for delivery in deliveries:
                delivery.delivery_status = target_status
                if target_status == 'Delivered':
                    delivery.actual_delivery_date = datetime.now().date()
                count += 1
            
            db.session.commit()
            
            return {
                'answer': f"✅ Updated {count} deliveries to '{target_status}'!",
                'action': 'delivery_update',
                'success': True,
                'data': {'count': count, 'status': target_status}
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'answer': f"❌ Error: {str(e)}",
                'action': 'delivery_update',
                'success': False
            }
    
    def _execute_po_action(self, po_ref, action):
        """Execute action on specific PO"""
        try:
            po = PurchaseOrder.query.filter_by(po_ref=po_ref).first()
            
            if not po:
                return {
                    'answer': f"❌ Purchase Order {po_ref} not found.",
                    'action': 'po_action',
                    'success': False
                }
            
            if action == 'approve':
                po.po_status = 'Approved'
                message = f"✅ Purchase Order {po_ref} approved!"
            else:
                po.po_status = 'Rejected'
                message = f"❌ Purchase Order {po_ref} rejected."
            
            db.session.commit()
            
            return {
                'answer': message,
                'action': 'po_action',
                'success': True,
                'data': po.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'answer': f"❌ Error: {str(e)}",
                'action': 'po_action',
                'success': False
            }
    
    def _get_approval_status_counts(self):
        """Get current approval status counts"""
        materials = Material.query.all()
        counts = {}
        for material in materials:
            status = material.approval_status
            counts[status] = counts.get(status, 0) + 1
        return counts


class ChatService:
    """Original chat service for queries (kept for backward compatibility)"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        # Initialize Claude if available (with error handling)
        if ANTHROPIC_AVAILABLE and Config.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                print("Chat service will work with limited functionality")
        
        # Initialize OpenAI if available (with error handling)
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                openai.api_key = Config.OPENAI_API_KEY
                self.openai_client = openai
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                print("Chat service will work with limited functionality")
    
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
                    model="claude-3-5-sonnet-20241022",  # Upgraded to Claude 3.5 Sonnet (latest)
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
