from datetime import datetime
from models import db

class Delivery(db.Model):
    """Delivery model for tracking material deliveries"""
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    
    # Delivery Details
    expected_delivery_date = db.Column(db.DateTime)
    actual_delivery_date = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(50), default='Pending')  # Pending, In Transit, Partial Delivery, Completed, Delayed
    
    # Quantity Details
    ordered_quantity = db.Column(db.Float)
    delivered_quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(50))
    
    # Tracking Information
    tracking_number = db.Column(db.String(100))
    carrier = db.Column(db.String(200))
    
    # Location
    delivery_location = db.Column(db.String(500))
    received_by = db.Column(db.String(100))
    
    # Delay Information
    is_delayed = db.Column(db.Boolean, default=False)
    delay_reason = db.Column(db.Text)
    delay_days = db.Column(db.Integer, default=0)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Document Storage
    delivery_note_path = db.Column(db.String(500))
    
    # Audit Trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), default='Manual')
    updated_by = db.Column(db.String(100), default='Manual')
    
    def check_delay(self):
        """Check if delivery is delayed and calculate delay days"""
        if self.expected_delivery_date:
            today = datetime.utcnow()
            if self.actual_delivery_date:
                # Delivery completed - check if it was late
                if self.actual_delivery_date > self.expected_delivery_date:
                    self.is_delayed = True
                    self.delay_days = (self.actual_delivery_date - self.expected_delivery_date).days
                    self.delivery_status = 'Delayed'
            else:
                # Delivery not completed yet - check if overdue
                if today > self.expected_delivery_date and self.delivery_status not in ['Completed']:
                    self.is_delayed = True
                    self.delay_days = (today - self.expected_delivery_date).days
                    self.delivery_status = 'Delayed'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'po_id': self.po_id,
            'po_ref': self.purchase_order.po_ref if self.purchase_order else None,
            'material_type': self.purchase_order.material.material_type if self.purchase_order and self.purchase_order.material else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'delivery_status': self.delivery_status,
            'ordered_quantity': self.ordered_quantity,
            'delivered_quantity': self.delivered_quantity,
            'unit': self.unit,
            'tracking_number': self.tracking_number,
            'carrier': self.carrier,
            'delivery_location': self.delivery_location,
            'received_by': self.received_by,
            'is_delayed': self.is_delayed,
            'delay_reason': self.delay_reason,
            'delay_days': self.delay_days,
            'notes': self.notes,
            'delivery_note_path': self.delivery_note_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    def __repr__(self):
        return f'<Delivery {self.id} - PO: {self.po_id}>'
