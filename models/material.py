from datetime import datetime
from models import db

class Material(db.Model):
    """Material model for tracking construction materials"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Approval Status
    approval_status = db.Column(db.String(50), default='Pending')  # Approved, Approved as Noted, Pending, Under Review, Revise & Resubmit
    approval_date = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    # References
    submittal_ref = db.Column(db.String(100))
    specification_ref = db.Column(db.String(100))
    
    # Tracking
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(50))
    
    # Audit Trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='Manual')  # 'Manual' or 'AI'
    updated_by = db.Column(db.String(100), default='Manual')
    
    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', backref='material', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'material_type': self.material_type,
            'description': self.description,
            'approval_status': self.approval_status,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'approval_notes': self.approval_notes,
            'submittal_ref': self.submittal_ref,
            'specification_ref': self.specification_ref,
            'quantity': self.quantity,
            'unit': self.unit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    def __repr__(self):
        return f'<Material {self.material_type}>'
