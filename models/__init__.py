from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Import all models
from .material import Material
from .purchase_order import PurchaseOrder
from .payment import Payment
from .delivery import Delivery
from .ai_suggestion import AISuggestion
