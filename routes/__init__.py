from flask import Blueprint

# Import all blueprints
from .dashboard import dashboard_bp
from .materials import materials_bp
from .purchase_orders import purchase_orders_bp
from .payments import payments_bp
from .deliveries import deliveries_bp
from .ai_suggestions import ai_suggestions_bp
from .chat import chat_bp
from .agents import agents_bp

__all__ = [
    'dashboard_bp',
    'materials_bp',
    'purchase_orders_bp',
    'payments_bp',
    'deliveries_bp',
    'ai_suggestions_bp',
    'chat_bp',
    'agents_bp'
]
