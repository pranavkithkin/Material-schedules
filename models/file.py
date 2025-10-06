"""
File Model
Stores uploaded document metadata and processing status
"""
from datetime import datetime
from models import db

class File(db.Model):
    """Model for uploaded files (POs, Invoices, Delivery Notes)"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'purchase_order', 'invoice', 'delivery_note', 'other'
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100))
    
    # Processing status
    processing_status = db.Column(db.String(50), default='uploaded')  # 'uploaded', 'processing', 'completed', 'failed'
    extracted_data = db.Column(db.JSON)  # AI-extracted data from document
    extraction_confidence = db.Column(db.Float)  # Overall confidence score (0-100)
    error_message = db.Column(db.Text)  # Error details if processing failed
    
    # Relationships
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=True)
    
    # Metadata
    uploaded_by = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships (back references)
    material = db.relationship('Material', backref='files')
    purchase_order = db.relationship('PurchaseOrder', backref='po_files', overlaps='files,po_parent')
    payment = db.relationship('Payment', backref='files')
    delivery = db.relationship('Delivery', backref='files')
    
    def __repr__(self):
        return f'<File {self.filename} ({self.file_type})>'
    
    def to_dict(self):
        """Convert file record to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'processing_status': self.processing_status,
            'extracted_data': self.extracted_data,
            'extraction_confidence': self.extraction_confidence,
            'error_message': self.error_message,
            'material_id': self.material_id,
            'purchase_order_id': self.purchase_order_id,
            'payment_id': self.payment_id,
            'delivery_id': self.delivery_id,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_url(self):
        """Get URL to download the file"""
        return f'/uploads/{self.filename}'
    
    @staticmethod
    def get_pending_processing():
        """Get all files awaiting AI processing"""
        return File.query.filter_by(processing_status='uploaded').order_by(File.uploaded_at.asc()).all()
    
    @staticmethod
    def get_by_type(file_type):
        """Get all files of a specific type"""
        return File.query.filter_by(file_type=file_type).order_by(File.uploaded_at.desc()).all()
    
    @staticmethod
    def get_by_entity(entity_type, entity_id):
        """Get files associated with a specific entity (material, PO, etc.)"""
        filters = {
            'material': {'material_id': entity_id},
            'purchase_order': {'purchase_order_id': entity_id},
            'payment': {'payment_id': entity_id},
            'delivery': {'delivery_id': entity_id}
        }
        
        if entity_type not in filters:
            return []
        
        return File.query.filter_by(**filters[entity_type]).order_by(File.uploaded_at.desc()).all()
