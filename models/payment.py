from datetime import datetime
from models import db

class Payment(db.Model):
    """Payment model for tracking payments against POs"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    
    # Payment Structure
    payment_structure = db.Column(db.String(50), default='Single Payment')  # Single Payment, Advance + Balance
    
    # Payment Details
    payment_type = db.Column(db.String(50))  # Advance, Balance, Full, Partial
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0)
    payment_percentage = db.Column(db.Float, default=0)
    payment_date = db.Column(db.DateTime)
    
    # Payment Terms (from PO)
    payment_terms = db.Column(db.Text)  # Copied from PO for reference
    
    # Additional Details
    payment_ref = db.Column(db.String(100))
    invoice_ref = db.Column(db.String(100))
    payment_method = db.Column(db.String(100))  # Bank Transfer, Check, etc.
    currency = db.Column(db.String(10), default='AED')
    
    # Status
    payment_status = db.Column(db.String(50), default='Pending')  # Pending, Completed, Full, Partial
    
    # Notes
    notes = db.Column(db.Text)
    
    # Document Storage
    invoice_path = db.Column(db.String(500))
    receipt_path = db.Column(db.String(500))
    
    # Audit Trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='Manual')
    updated_by = db.Column(db.String(100), default='Manual')
    
    def calculate_percentage(self):
        """Calculate payment percentage"""
        if self.total_amount > 0:
            self.payment_percentage = (self.paid_amount / self.total_amount) * 100
        else:
            self.payment_percentage = 0
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'po_id': self.po_id,
            'po_ref': self.purchase_order.po_ref if self.purchase_order else None,
            'payment_structure': self.payment_structure,
            'payment_type': self.payment_type,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'payment_percentage': self.payment_percentage,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_ref': self.payment_ref,
            'invoice_ref': self.invoice_ref,
            'payment_method': self.payment_method,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'payment_terms': self.payment_terms,
            'notes': self.notes,
            'invoice_path': self.invoice_path,
            'receipt_path': self.receipt_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    def __repr__(self):
        return f'<Payment {self.payment_ref}>'
