"""
Local Purchase Order (LPO) Model
Handles LPO generation with dynamic column structure for different supplier types
"""
from datetime import datetime
from . import db


class LPO(db.Model):
    """Local Purchase Order model with dynamic column structure"""
    __tablename__ = 'lpos'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # LPO Identification
    lpo_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # Format: LPO/PKP/YYYY/NNNN (e.g., LPO/PKP/2025/0001)
    
    revision = db.Column(db.String(10), default='00')
    status = db.Column(db.String(20), default='draft')
    # Status: draft, issued, acknowledged, completed, cancelled
    
    # Dates
    lpo_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quotation_date = db.Column(db.Date)
    delivery_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    issued_at = db.Column(db.DateTime)  # When status changed to 'issued'
    
    # Project Information
    project_name = db.Column(db.String(200), nullable=False)
    project_location = db.Column(db.String(200))
    consultant = db.Column(db.String(200))
    
    # Supplier Information
    supplier_name = db.Column(db.String(200), nullable=False, index=True)
    supplier_address = db.Column(db.Text)
    supplier_trn = db.Column(db.String(50))  # Tax Registration Number
    supplier_tel = db.Column(db.String(50))
    supplier_fax = db.Column(db.String(50))
    contact_person = db.Column(db.String(100))
    contact_number = db.Column(db.String(50))
    
    # Reference Information
    quotation_ref = db.Column(db.String(100))
    quotation_pdf_path = db.Column(db.String(500))  # Path to uploaded quote PDF
    
    # Dynamic Items Structure
    column_structure = db.Column(db.JSON, nullable=False)
    # Example: ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # or: ["BRAND", "MODEL", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # or: ["CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"]
    # Adapts to whatever columns the supplier quote has
    
    items = db.Column(db.JSON, nullable=False)
    # List of items, each with keys matching column_structure
    # Example: [
    #     {
    #         "number": 1,
    #         "make": "Samsung",
    #         "code": "LED-100",
    #         "description": "LED Light 10W",
    #         "unit": "Nos",
    #         "quantity": 50,
    #         "unit_price": 25.00,
    #         "vat_amount": 1.25,
    #         "total_amount": 1250.00
    #     }
    # ]
    
    # Financial Information
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    vat_percentage = db.Column(db.Numeric(5, 2), default=5.00)  # UAE VAT 5%
    vat_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    grand_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    
    # Terms and Conditions
    payment_terms = db.Column(db.Text)
    delivery_terms = db.Column(db.Text)
    warranty_terms = db.Column(db.Text)
    other_terms = db.Column(db.Text)
    
    # Additional Notes
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)  # Not shown on PDF
    
    # Link to PO (if created from LPO)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    purchase_order = db.relationship('PurchaseOrder', backref='lpo', foreign_keys=[purchase_order_id])
    
    # Audit Trail
    created_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    
    # AI Extraction Metadata
    extraction_method = db.Column(db.String(50))  # 'manual', 'ai_extracted', 'template'
    extraction_confidence = db.Column(db.Numeric(5, 2))  # 0-100 confidence score
    extraction_notes = db.Column(db.Text)  # Any issues during extraction
    
    def __repr__(self):
        return f'<LPO {self.lpo_number} - {self.supplier_name}>'
    
    def to_dict(self):
        """Convert LPO to dictionary for JSON response"""
        return {
            'id': self.id,
            'lpo_number': self.lpo_number,
            'revision': self.revision,
            'status': self.status,
            'lpo_date': self.lpo_date.isoformat() if self.lpo_date else None,
            'quotation_date': self.quotation_date.isoformat() if self.quotation_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'project_name': self.project_name,
            'project_location': self.project_location,
            'consultant': self.consultant,
            'supplier_name': self.supplier_name,
            'supplier_address': self.supplier_address,
            'supplier_trn': self.supplier_trn,
            'supplier_tel': self.supplier_tel,
            'supplier_fax': self.supplier_fax,
            'contact_person': self.contact_person,
            'contact_number': self.contact_number,
            'quotation_ref': self.quotation_ref,
            'column_structure': self.column_structure,
            'items': self.items,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'vat_percentage': float(self.vat_percentage) if self.vat_percentage else 5.0,
            'vat_amount': float(self.vat_amount) if self.vat_amount else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'payment_terms': self.payment_terms,
            'delivery_terms': self.delivery_terms,
            'warranty_terms': self.warranty_terms,
            'other_terms': self.other_terms,
            'notes': self.notes,
            'extraction_method': self.extraction_method,
            'extraction_confidence': float(self.extraction_confidence) if self.extraction_confidence else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
        }
    
    @property
    def item_count(self):
        """Get number of items in LPO"""
        return len(self.items) if self.items else 0
    
    @property
    def total_amount(self):
        """Calculate total amount (subtotal + VAT)"""
        return float(self.subtotal or 0) + float(self.vat_amount or 0)
    
    @property
    def is_editable(self):
        """Check if LPO can be edited"""
        return self.status in ['draft', 'rejected']
    
    @property
    def can_be_issued(self):
        """Check if LPO can be issued"""
        return self.status == 'draft' and self.item_count > 0


class LPOHistory(db.Model):
    """Audit trail for LPO changes"""
    __tablename__ = 'lpo_history'
    
    id = db.Column(db.Integer, primary_key=True)
    lpo_id = db.Column(db.Integer, db.ForeignKey('lpos.id'), nullable=False)
    
    action = db.Column(db.String(50), nullable=False)
    # Actions: created, updated, issued, acknowledged, cancelled, revised
    
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    
    changes = db.Column(db.JSON)  # Dict of field changes
    notes = db.Column(db.Text)
    
    performed_by = db.Column(db.String(100))
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    lpo = db.relationship('LPO', backref='history')
    
    def __repr__(self):
        return f'<LPOHistory {self.action} - LPO {self.lpo_id}>'
