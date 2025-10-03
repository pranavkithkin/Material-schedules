from datetime import datetime
from models import db
import json

class AISuggestion(db.Model):
    """AI Suggestion model for tracking AI-extracted data waiting for approval"""
    __tablename__ = 'ai_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Target Information
    target_table = db.Column(db.String(50), nullable=False)  # materials, purchase_orders, payments, deliveries
    target_id = db.Column(db.Integer)  # ID of existing record (null for new records)
    action_type = db.Column(db.String(20), nullable=False)  # create, update
    
    # AI Information
    ai_model = db.Column(db.String(50))  # claude-3, gpt-4, etc.
    confidence_score = db.Column(db.Float, nullable=False)  # 0-100
    extraction_source = db.Column(db.String(200))  # email, pdf, manual input
    source_document_path = db.Column(db.String(500))
    
    # Suggested Data (stored as JSON)
    suggested_data = db.Column(db.Text, nullable=False)  # JSON string
    current_data = db.Column(db.Text)  # JSON string of current values (for updates)
    
    # AI Reasoning
    ai_reasoning = db.Column(db.Text)  # Why AI made this suggestion
    missing_fields = db.Column(db.Text)  # JSON array of fields AI couldn't extract
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, auto_applied
    
    # Human Review
    reviewed_by = db.Column(db.String(100))
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)
    
    # Audit Trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_suggested_data(self):
        """Parse suggested data from JSON"""
        try:
            return json.loads(self.suggested_data) if self.suggested_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_suggested_data(self, data):
        """Set suggested data as JSON"""
        self.suggested_data = json.dumps(data)
    
    def get_current_data(self):
        """Parse current data from JSON"""
        try:
            return json.loads(self.current_data) if self.current_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_current_data(self, data):
        """Set current data as JSON"""
        self.current_data = json.dumps(data)
    
    def get_missing_fields(self):
        """Parse missing fields from JSON"""
        try:
            return json.loads(self.missing_fields) if self.missing_fields else []
        except json.JSONDecodeError:
            return []
    
    def set_missing_fields(self, fields):
        """Set missing fields as JSON"""
        self.missing_fields = json.dumps(fields)
    
    def should_auto_apply(self, threshold=90):
        """Check if suggestion should be auto-applied based on confidence"""
        return self.confidence_score >= threshold
    
    def get_confidence_level(self):
        """Get human-readable confidence level"""
        if self.confidence_score >= 90:
            return 'High'
        elif self.confidence_score >= 60:
            return 'Medium'
        else:
            return 'Low'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'target_table': self.target_table,
            'target_id': self.target_id,
            'action_type': self.action_type,
            'ai_model': self.ai_model,
            'confidence_score': self.confidence_score,
            'confidence_level': self.get_confidence_level(),
            'extraction_source': self.extraction_source,
            'source_document_path': self.source_document_path,
            'suggested_data': self.get_suggested_data(),
            'current_data': self.get_current_data(),
            'ai_reasoning': self.ai_reasoning,
            'missing_fields': self.get_missing_fields(),
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AISuggestion {self.id} - {self.target_table} ({self.confidence_score}%)>'
