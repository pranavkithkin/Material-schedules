"""
Conversation Model
Tracks multi-turn chat conversations with context
"""

from models import db
from datetime import datetime
import json

class Conversation(db.Model):
    """Model for tracking chat conversations"""
    __tablename__ = 'conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(100), nullable=True)  # Optional user tracking
    
    # Conversation state
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    intent = db.Column(db.String(50), nullable=True)  # add_po, query_data, update_info
    context_data = db.Column(db.JSON, default=dict)  # Stores partial data being collected
    
    # Messages in this conversation
    messages = db.relationship('ConversationMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Conversation {self.conversation_id}: {self.intent}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'status': self.status,
            'intent': self.intent,
            'context_data': self.context_data,
            'message_count': self.messages.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def get_messages(self, limit=50):
        """Get conversation messages"""
        return self.messages.order_by(ConversationMessage.created_at.asc()).limit(limit).all()
    
    def add_message(self, role, content, extra_data=None):
        """Add a message to the conversation"""
        message = ConversationMessage(
            conversation_id=self.id,
            role=role,
            content=content,
            extra_data=extra_data or {}
        )
        db.session.add(message)
        self.updated_at = datetime.utcnow()
        return message
    
    def update_context(self, key, value):
        """Update context data"""
        if self.context_data is None:
            self.context_data = {}
        self.context_data[key] = value
        db.session.add(self)
    
    def complete(self):
        """Mark conversation as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.add(self)


class ConversationMessage(db.Model):
    """Individual messages in a conversation"""
    __tablename__ = 'conversation_message'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False, index=True)
    
    # Message details
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    extra_data = db.Column(db.JSON, default=dict)  # Extra data: extracted_entities, confidence, etc.
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Message {self.id}: {self.role}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
