from datetime import datetime
from models import db

class PurchaseOrder(db.Model):
    """Purchase Order model for tracking POs"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    
    # PO Details
    quote_ref = db.Column(db.String(100))
    po_ref = db.Column(db.String(100), unique=True, nullable=False)
    po_date = db.Column(db.DateTime)
    expected_delivery_date = db.Column(db.DateTime)  # Expected delivery date from PO
    supplier_name = db.Column(db.String(200), nullable=False)
    supplier_contact = db.Column(db.String(200))
    supplier_email = db.Column(db.String(200))
    
    # Financial Details
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='AED')
    
    # Status
    po_status = db.Column(db.String(50), default='Not Released')  # Not Released, Released, Cancelled
    
    # Additional Details
    payment_terms = db.Column(db.Text)
    delivery_terms = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Document Storage
    document_path = db.Column(db.String(500))
    
    # Audit Trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='Manual')
    updated_by = db.Column(db.String(100), default='Manual')
    
    # Relationships (material relationship is created by backref in Material model)
    payments = db.relationship('Payment', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('File', backref='po_parent', lazy=True, cascade='all, delete-orphan', foreign_keys='File.purchase_order_id')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'material_id': self.material_id,
            'material': {'id': self.material.id, 'material_type': self.material.material_type} if self.material else None,
            'quote_ref': self.quote_ref,
            'po_ref': self.po_ref,
            'po_number': self.po_ref,  # Alias for template compatibility
            'issue_date': self.po_date.isoformat() if self.po_date else None,
            'po_date': self.po_date.isoformat() if self.po_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'supplier_name': self.supplier_name,
            'supplier_contact': self.supplier_contact,
            'supplier_email': self.supplier_email,
            'total_amount': self.total_amount,
            'po_amount': self.total_amount,  # Alias for template compatibility
            'currency': self.currency,
            'po_status': self.po_status,
            'payment_terms': self.payment_terms,
            'delivery_terms': self.delivery_terms,
            'notes': self.notes,
            'document_path': self.document_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_ref}>'
