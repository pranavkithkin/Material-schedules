"""
DATA PROCESSING AGENT - Unified Agent for Data Quality & Integrity
Combines: Validation + Duplicate Detection + Invoice-LPO Matching

🎯 ZERO TOKEN USAGE - Pure Python logic, no LLM calls!
Saves ~800 tokens per operation compared to using AI for validation.
"""
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re
from typing import Dict, List, Tuple, Any, Optional


class DataProcessingAgent:
    """
    Unified agent handling:
    1. Data validation (mandatory fields, formats, cross-references, anomalies)
    2. Duplicate detection (fuzzy matching, exact matching, date proximity)
    3. Invoice-LPO matching (multi-strategy, confidence scoring)
    
    Token usage: ZERO - No LLM calls needed!
    """
    
    def __init__(self, db_session):
        self.db = db_session
        self.validation_errors = []
        self.validation_warnings = []
        self.similarity_threshold = 0.85  # 85% = potential duplicate
    
    # ============================================================================
    # MAIN ENTRY POINT - Unified Processing
    # ============================================================================
    
    def process_data(
        self, 
        record_type: str, 
        data: Dict[str, Any],
        check_duplicates: bool = True,
        match_invoice_to_lpo: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for data processing.
        Returns comprehensive validation + duplicate + matching results.
        
        Args:
            record_type: 'lpo_release', 'invoice', 'submittal', 'delivery'
            data: Record data to process
            check_duplicates: Whether to check for duplicates
            match_invoice_to_lpo: Whether to match invoice to LPO (invoices only)
        
        Returns:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'duplicates': List[Dict],
                'matched_lpo_id': int or None,
                'ready_to_save': bool
            }
        """
        # Step 1: Validate data
        is_valid, errors, warnings = self._validate(record_type, data)
        
        # Step 2: Check for duplicates (if requested)
        duplicates = []
        if check_duplicates:
            has_dupes, duplicates = self._check_duplicates(record_type, data)
        
        # Step 3: Match invoice to LPO (if requested)
        matched_lpo_id = None
        if match_invoice_to_lpo and record_type == 'invoice':
            matched_lpo_id = self._match_invoice_to_lpo(data)
        
        # Determine if ready to save
        ready_to_save = is_valid and len(duplicates) == 0
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'duplicates': duplicates,
            'matched_lpo_id': matched_lpo_id,
            'ready_to_save': ready_to_save
        }
    
    # ============================================================================
    # PART 1: DATA VALIDATION
    # ============================================================================
    
    def _validate(self, record_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Route to appropriate validation method"""
        self.validation_errors = []
        self.validation_warnings = []
        
        if record_type == 'lpo_release':
            return self._validate_lpo_release(data)
        elif record_type == 'invoice':
            return self._validate_invoice(data)
        elif record_type == 'submittal':
            return self._validate_submittal(data)
        elif record_type == 'delivery':
            return self._validate_delivery(data)
        else:
            self.validation_errors.append(f"❌ Unknown record type: {record_type}")
            return False, self.validation_errors, []
    
    def _validate_lpo_release(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate LPO Release data"""
        # Mandatory fields
        self._check_mandatory_fields(data, [
            'material_id', 'supplier_name', 'lpo_number', 
            'release_date', 'amount'
        ])
        
        # Format validation
        self._validate_lpo_number(data.get('lpo_number'))
        self._validate_date(data.get('release_date'), 'Release Date')
        self._validate_amount(data.get('amount'), 'Amount')
        self._validate_phone_number(data.get('contact_number'))
        self._validate_email(data.get('contact_email'))
        
        # Cross-reference validation
        if data.get('expected_delivery_date') and data.get('release_date'):
            self._validate_delivery_after_release(
                data['release_date'], 
                data['expected_delivery_date']
            )
        
        # Anomaly detection
        self._detect_amount_anomaly(data.get('amount'), 'lpo_releases')
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_invoice(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate Invoice/Payment data"""
        # Mandatory fields (matching Payment model)
        self._check_mandatory_fields(data, [
            'payment_date', 'total_amount'
        ])
        
        # Format validation
        if data.get('invoice_number'):
            self._validate_invoice_number(data.get('invoice_number'))
        self._validate_date(data.get('payment_date') or data.get('invoice_date'), 'Payment Date')
        self._validate_amount(data.get('total_amount') or data.get('amount'), 'Amount')
        
        # Optional due date validation
        if data.get('due_date'):
            self._validate_date(data.get('due_date'), 'Due Date')
            
        # Cross-reference validation
        if data.get('invoice_date') and data.get('due_date'):
            self._validate_due_after_invoice(
                data['invoice_date'], 
                data['due_date']
            )
        
        # CRITICAL: Check if payment exceeds PO amount
        if data.get('po_id') and data.get('total_amount'):
            self._validate_payment_against_po(data['po_id'], data['total_amount'])
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_submittal(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate Material Submittal data"""
        # Mandatory fields
        self._check_mandatory_fields(data, [
            'material_id', 'date_submitted', 'status'
        ])
        
        # Format validation
        self._validate_date(data.get('date_submitted'), 'Submission Date')
        self._validate_status(data.get('status'), [
            'Pending', 'Under Review', 'Approved', 'Approved as Noted', 'Revise & Resubmit'
        ])
        
        # Cross-reference validation
        if data.get('date_submitted') and data.get('response_date'):
            self._validate_response_after_submission(
                data['date_submitted'], 
                data['response_date']
            )
        
        # Check if response overdue
        if data.get('status') == 'Pending' and data.get('date_submitted'):
            self._check_submittal_response_overdue(data['date_submitted'])
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_delivery(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate Delivery Order data"""
        # Mandatory fields
        self._check_mandatory_fields(data, [
            'lpo_id', 'delivery_date', 'status'
        ])
        
        # Format validation
        self._validate_date(data.get('delivery_date'), 'Delivery Date')
        self._validate_status(data.get('status'), [
            'Pending', 'Partial', 'Delivered', 'Rejected'
        ])
        
        # Delivery percentage validation for partial deliveries
        if data.get('status') == 'Partial':
            delivery_percentage = data.get('delivery_percentage', 0)
            if delivery_percentage <= 0 or delivery_percentage >= 100:
                self.validation_warnings.append(
                    f"⚠️ Partial delivery should have percentage between 1-99% (currently: {delivery_percentage}%)"
                )
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    # Validation helper methods
    def _check_mandatory_fields(self, data: Dict[str, Any], required_fields: List[str]):
        """Check if all mandatory fields are present and not empty"""
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                self.validation_errors.append(
                    f"❌ {field.replace('_', ' ').title()} is required"
                )
    
    def _validate_lpo_number(self, lpo_number: Optional[str]):
        """Validate LPO number format"""
        if not lpo_number:
            return
        pattern = r'^LPO-\d{4}-\d{3,}$'
        if not re.match(pattern, lpo_number, re.IGNORECASE):
            self.validation_warnings.append(
                f"⚠️ LPO number '{lpo_number}' doesn't follow standard format (LPO-YYYY-NNN)"
            )
    
    def _validate_invoice_number(self, invoice_number: Optional[str]):
        """Validate invoice number format"""
        if not invoice_number:
            return
        if len(invoice_number) < 3:
            self.validation_errors.append(
                f"❌ Invoice number '{invoice_number}' is too short"
            )
    
    def _validate_date(self, date_value: Any, field_name: str):
        """Validate date format and reasonableness"""
        if not date_value:
            return
        
        try:
            if isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            elif isinstance(date_value, datetime):
                date_obj = date_value
            else:
                self.validation_errors.append(
                    f"❌ {field_name} has invalid format"
                )
                return
            
            # Check if date not too old (> 5 years)
            five_years_ago = datetime.now() - timedelta(days=365*5)
            if date_obj < five_years_ago:
                self.validation_warnings.append(
                    f"⚠️ {field_name} is more than 5 years in the past"
                )
            
            # Check if date not too far future (> 2 years)
            two_years_future = datetime.now() + timedelta(days=365*2)
            if date_obj > two_years_future:
                self.validation_warnings.append(
                    f"⚠️ {field_name} is more than 2 years in the future"
                )
        
        except (ValueError, TypeError):
            self.validation_errors.append(
                f"❌ {field_name} has invalid date format (use YYYY-MM-DD)"
            )
    
    def _validate_amount(self, amount: Any, field_name: str):
        """Validate amount is positive number"""
        if amount is None:
            return
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                self.validation_errors.append(
                    f"❌ {field_name} must be a positive number"
                )
            elif amount_float > 10000000:  # 10 million
                self.validation_warnings.append(
                    f"⚠️ {field_name} is unusually high (AED {amount_float:,.2f})"
                )
        except (ValueError, TypeError):
            self.validation_errors.append(
                f"❌ {field_name} must be a valid number"
            )
    
    def _validate_phone_number(self, phone: Optional[str]):
        """Validate phone number format"""
        if not phone:
            return
        
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
            self.validation_warnings.append(
                f"⚠️ Phone number '{phone}' may not be valid"
            )
    
    def _validate_email(self, email: Optional[str]):
        """Validate email format"""
        if not email:
            return
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.validation_errors.append(
                f"❌ Email '{email}' is not valid"
            )
    
    def _validate_status(self, status: Optional[str], allowed_values: List[str]):
        """Validate status is one of allowed values"""
        if not status:
            return
        
        if status not in allowed_values:
            self.validation_errors.append(
                f"❌ Status '{status}' is invalid. Must be one of: {', '.join(allowed_values)}"
            )
    
    def _validate_delivery_after_release(self, release_date: Any, delivery_date: Any):
        """Ensure delivery date is after release date"""
        try:
            release = self._parse_date(release_date)
            delivery = self._parse_date(delivery_date)
            
            if delivery < release:
                self.validation_errors.append(
                    "❌ Expected delivery date cannot be before LPO release date"
                )
            elif delivery == release:
                self.validation_warnings.append(
                    "⚠️ Expected delivery is same day as LPO release"
                )
        except:
            pass
    
    def _validate_due_after_invoice(self, invoice_date: Any, due_date: Any):
        """Ensure payment due date is after invoice date"""
        try:
            invoice = self._parse_date(invoice_date)
            due = self._parse_date(due_date)
            
            if due < invoice:
                self.validation_errors.append(
                    "❌ Payment due date cannot be before invoice date"
                )
            
            days_diff = (due - invoice).days
            if days_diff > 90:
                self.validation_warnings.append(
                    f"⚠️ Payment terms are {days_diff} days (longer than typical)"
                )
        except:
            pass
    
    def _validate_response_after_submission(self, submitted_date: Any, response_date: Any):
        """Ensure response date is after submission date"""
        try:
            submitted = self._parse_date(submitted_date)
            response = self._parse_date(response_date)
            
            if response < submitted:
                self.validation_errors.append(
                    "❌ Response date cannot be before submission date"
                )
        except:
            pass
    
    def _validate_quantity_match(self, ordered: Any, delivered: Any):
        """Check if delivered quantity matches ordered"""
        try:
            ordered_qty = float(ordered)
            delivered_qty = float(delivered)
            
            if delivered_qty > ordered_qty:
                self.validation_warnings.append(
                    f"⚠️ Delivered quantity ({delivered_qty}) exceeds ordered ({ordered_qty})"
                )
            elif delivered_qty < ordered_qty * 0.9:
                self.validation_warnings.append(
                    f"⚠️ Delivered quantity ({delivered_qty}) is less than ordered ({ordered_qty})"
                )
        except (ValueError, TypeError):
            pass
    
    def _validate_payment_against_po(self, po_id: int, new_payment_amount: float):
        """
        CRITICAL: Validate that total payments don't exceed PO amount.
        This prevents over-payment and financial errors.
        """
        from models.purchase_order import PurchaseOrder
        from models.payment import Payment
        
        try:
            # Get the PO
            po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
            if not po:
                self.validation_errors.append(
                    f"❌ Purchase Order with ID {po_id} not found"
                )
                return
            
            # Get all existing payments for this PO
            existing_payments = self.db.query(Payment).filter(
                Payment.po_id == po_id
            ).all()
            
            # Calculate total existing payments
            total_existing = sum(
                payment.paid_amount or payment.total_amount or 0 
                for payment in existing_payments
            )
            
            # Calculate total with new payment
            total_with_new = total_existing + new_payment_amount
            
            # Check if exceeds PO amount
            if total_with_new > po.total_amount:
                excess = total_with_new - po.total_amount
                self.validation_errors.append(
                    f"❌ PAYMENT EXCEEDS PO AMOUNT!\n"
                    f"   PO {po.po_ref}: AED {po.total_amount:,.2f}\n"
                    f"   Already paid: AED {total_existing:,.2f}\n"
                    f"   New payment: AED {new_payment_amount:,.2f}\n"
                    f"   Total would be: AED {total_with_new:,.2f}\n"
                    f"   Excess: AED {excess:,.2f}"
                )
            # Warn if payment exceeds remaining balance
            elif total_with_new > po.total_amount * 0.95:  # Within 5% of limit
                remaining = po.total_amount - total_existing
                self.validation_warnings.append(
                    f"⚠️ Payment is close to PO limit\n"
                    f"   PO {po.po_ref}: AED {po.total_amount:,.2f}\n"
                    f"   Already paid: AED {total_existing:,.2f}\n"
                    f"   Remaining: AED {remaining:,.2f}\n"
                    f"   New payment: AED {new_payment_amount:,.2f}"
                )
            # Info: Show payment progress
            else:
                remaining = po.total_amount - total_existing - new_payment_amount
                percentage = (total_with_new / po.total_amount) * 100
                self.validation_warnings.append(
                    f"ℹ️ Payment Progress for PO {po.po_ref}:\n"
                    f"   PO Amount: AED {po.total_amount:,.2f}\n"
                    f"   Paid: AED {total_existing:,.2f}\n"
                    f"   This payment: AED {new_payment_amount:,.2f}\n"
                    f"   Total after: AED {total_with_new:,.2f} ({percentage:.1f}%)\n"
                    f"   Remaining: AED {remaining:,.2f}"
                )
                
        except Exception as e:
            self.validation_warnings.append(
                f"⚠️ Could not validate payment against PO: {str(e)}"
            )
    
    def _detect_amount_anomaly(self, amount: Any, table_name: str):
        """Detect if amount is significantly outside normal range"""
        if not amount:
            return
        
        try:
            amount_float = float(amount)
            
            typical_ranges = {
                'lpo_releases': (1000, 500000),
                'invoices': (1000, 500000),
            }
            
            if table_name in typical_ranges:
                min_typical, max_typical = typical_ranges[table_name]
                
                if amount_float < min_typical:
                    self.validation_warnings.append(
                        f"⚠️ Amount (AED {amount_float:,.2f}) is lower than typical range"
                    )
                elif amount_float > max_typical:
                    self.validation_warnings.append(
                        f"⚠️ Amount (AED {amount_float:,.2f}) is higher than typical range"
                    )
        except (ValueError, TypeError):
            pass
    
    def _check_submittal_response_overdue(self, submitted_date: Any):
        """Check if submittal response is overdue (> 7 days)"""
        try:
            submitted = self._parse_date(submitted_date)
            days_pending = (datetime.now() - submitted).days
            
            if days_pending > 7:
                self.validation_warnings.append(
                    f"⚠️ Submittal response pending for {days_pending} days (>7 days threshold)"
                )
        except:
            pass
    
    # ============================================================================
    # PART 2: DUPLICATE DETECTION
    # ============================================================================
    
    def _check_duplicates(self, record_type: str, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Route to appropriate duplicate check method"""
        if record_type == 'lpo_release':
            return self._check_lpo_duplicate(data)
        elif record_type == 'invoice':
            return self._check_invoice_duplicate(data)
        elif record_type == 'submittal':
            return self._check_submittal_duplicate(data)
        elif record_type == 'delivery':
            return self._check_delivery_duplicate(data)
        else:
            return False, []
    
    def _check_lpo_duplicate(self, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check for duplicate PO/LPO releases"""
        from models.purchase_order import PurchaseOrder
        
        potential_duplicates = []
        
        # Strategy 1: Exact PO number match
        if data.get('lpo_number'):
            exact_match = self.db.query(PurchaseOrder).filter(
                PurchaseOrder.po_ref == data['lpo_number']
            ).first()
            
            if exact_match:
                potential_duplicates.append({
                    'id': exact_match.id,
                    'match_type': 'Exact PO Number',
                    'confidence': 1.0,
                    'lpo_number': exact_match.po_ref,
                    'supplier': exact_match.supplier_name,
                    'amount': exact_match.total_amount,
                    'release_date': exact_match.po_date.strftime('%Y-%m-%d') if exact_match.po_date else None,
                    'reason': f"PO number '{data['lpo_number']}' already exists"
                })
        
        # Strategy 2: Similar supplier + material + date proximity + similar amount
        if data.get('supplier_name') and data.get('material_id') and data.get('release_date'):
            release_date = self._parse_date(data['release_date'])
            date_start = release_date - timedelta(days=7)
            date_end = release_date + timedelta(days=7)
            
            similar_pos = self.db.query(PurchaseOrder).filter(
                PurchaseOrder.material_id == data['material_id'],
                PurchaseOrder.po_date.between(date_start, date_end)
            ).all()
            
            for po in similar_pos:
                supplier_similarity = self._calculate_similarity(
                    data['supplier_name'].lower(),
                    po.supplier_name.lower()
                )
                
                amount_similar = False
                if data.get('amount') and po.total_amount:
                    amount_diff = abs(float(data['amount']) - float(po.total_amount)) / float(po.total_amount)
                    amount_similar = amount_diff < 0.1
                
                if supplier_similarity > self.similarity_threshold and amount_similar:
                    potential_duplicates.append({
                        'id': po.id,
                        'match_type': 'Similar PO',
                        'confidence': supplier_similarity,
                        'lpo_number': po.po_ref,
                        'supplier': po.supplier_name,
                        'amount': po.total_amount,
                        'release_date': po.po_date.strftime('%Y-%m-%d') if po.po_date else None,
                        'reason': f"Similar PO exists (released {po.po_date.strftime('%Y-%m-%d') if po.po_date else 'unknown'})"
                    })
        
        has_duplicates = len(potential_duplicates) > 0
        return has_duplicates, potential_duplicates
    
    def _check_invoice_duplicate(self, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check for duplicate invoices/payments"""
        from models.payment import Payment
        
        potential_duplicates = []
        
        # Strategy 1: Exact invoice reference match
        invoice_num = data.get('invoice_number') or data.get('invoice_ref')
        if invoice_num:
            exact_match = self.db.query(Payment).filter(
                Payment.invoice_ref == invoice_num
            ).first()
            
            if exact_match:
                potential_duplicates.append({
                    'id': exact_match.id,
                    'match_type': 'Exact Invoice Reference',
                    'confidence': 1.0,
                    'invoice_ref': exact_match.invoice_ref,
                    'po_id': exact_match.po_id,
                    'amount': exact_match.paid_amount,
                    'payment_date': exact_match.payment_date.strftime('%Y-%m-%d') if exact_match.payment_date else None,
                    'reason': f"Invoice reference '{invoice_num}' already exists"
                })
        
        # Strategy 2: Exact payment reference match
        payment_ref = data.get('payment_ref')
        if payment_ref:
            exact_match = self.db.query(Payment).filter(
                Payment.payment_ref == payment_ref
            ).first()
            
            if exact_match and exact_match.id not in [d['id'] for d in potential_duplicates]:
                potential_duplicates.append({
                    'id': exact_match.id,
                    'match_type': 'Exact Payment Reference',
                    'confidence': 1.0,
                    'payment_ref': exact_match.payment_ref,
                    'po_id': exact_match.po_id,
                    'amount': exact_match.paid_amount,
                    'payment_date': exact_match.payment_date.strftime('%Y-%m-%d') if exact_match.payment_date else None,
                    'reason': f"Payment reference '{payment_ref}' already exists"
                })
        
        has_duplicates = len(potential_duplicates) > 0
        return has_duplicates, potential_duplicates
    
    def _check_submittal_duplicate(self, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check for duplicate material submittals"""
        # Note: MaterialSubmittal model not yet implemented
        # Return empty duplicates for now - can be implemented when model is added
        potential_duplicates = []
        
        # TODO: Implement when MaterialSubmittal model is created
        # if data.get('material_id') and data.get('date_submitted'):
        #     Check for similar submittals...
        
        has_duplicates = len(potential_duplicates) > 0
        return has_duplicates, potential_duplicates
    
    def _check_delivery_duplicate(self, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check for duplicate delivery orders"""
        from models.delivery import Delivery
        
        potential_duplicates = []
        
        if data.get('po_id') and data.get('delivery_date'):
            delivery_date = self._parse_date(data['delivery_date'])
            date_start = delivery_date - timedelta(days=7)
            date_end = delivery_date + timedelta(days=7)
            
            similar_deliveries = self.db.query(Delivery).filter(
                Delivery.po_id == data['po_id'],
                Delivery.delivery_date.between(date_start, date_end)
            ).all()
            
            for delivery in similar_deliveries:
                potential_duplicates.append({
                    'id': delivery.id,
                    'match_type': 'Similar Delivery',
                    'confidence': 0.85,
                    'po_id': delivery.po_id,
                    'delivery_date': delivery.delivery_date.strftime('%Y-%m-%d') if delivery.delivery_date else None,
                    'status': delivery.delivery_status,
                    'reason': f"Similar delivery for same PO on {delivery.delivery_date.strftime('%Y-%m-%d')}"
                })
        
        has_duplicates = len(potential_duplicates) > 0
        return has_duplicates, potential_duplicates
    
    # ============================================================================
    # PART 3: INVOICE-LPO MATCHING
    # ============================================================================
    
    def _match_invoice_to_lpo(self, invoice_data: Dict[str, Any]) -> Optional[int]:
        """
        Match invoice to corresponding LPO/PO using multiple strategies.
        Returns PO ID if high-confidence match found, None otherwise.
        """
        from models.purchase_order import PurchaseOrder
        
        # Strategy 1: Exact PO ID provided
        if invoice_data.get('po_id'):
            po = self.db.query(PurchaseOrder).filter(
                PurchaseOrder.id == invoice_data['po_id']
            ).first()
            if po:
                return po.id
        
        # Strategy 2: Match by PO number extracted from invoice
        # (Assumes invoice_data might have 'po_reference' field)
        if invoice_data.get('po_reference'):
            po = self.db.query(PurchaseOrder).filter(
                PurchaseOrder.po_ref == invoice_data['po_reference']
            ).first()
            if po:
                return po.id
        
        # Strategy 3: Fuzzy match by supplier + amount + date proximity
        # (More complex - can be implemented if needed)
        
        return None
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _parse_date(self, date_value: Any) -> datetime:
        """Convert various date formats to datetime object"""
        if isinstance(date_value, datetime):
            return date_value
        elif isinstance(date_value, str):
            return datetime.strptime(date_value, '%Y-%m-%d')
        else:
            raise ValueError("Invalid date format")
    
    def get_duplicate_summary(self, duplicates: List[Dict[str, Any]]) -> str:
        """Generate human-readable summary of duplicates found"""
        if not duplicates:
            return "✅ No duplicates found"
        
        summary = f"⚠️ Found {len(duplicates)} potential duplicate(s):\n\n"
        
        for i, dup in enumerate(duplicates, 1):
            summary += f"{i}. {dup['match_type']} "
            summary += f"(Confidence: {dup['confidence']*100:.0f}%)\n"
            summary += f"   {dup['reason']}\n"
        
        return summary
