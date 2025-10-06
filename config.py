import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///delivery_dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI APIs
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # n8n Integration
    N8N_API_KEY = os.getenv('N8N_API_KEY')
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook')
    N8N_BASE_URL = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
    N8N_TO_FLASK_API_KEY = os.getenv('N8N_TO_FLASK_API_KEY')
    
    # Email Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    
    # AI Confidence Thresholds
    AI_AUTO_UPDATE_THRESHOLD = int(os.getenv('AI_AUTO_UPDATE_THRESHOLD', 90))
    AI_REVIEW_THRESHOLD = int(os.getenv('AI_REVIEW_THRESHOLD', 60))
    
    # File Upload
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10485760))  # 10MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,xlsx,xls,doc,docx').split(','))
    
    # Application Settings
    CURRENCY = os.getenv('CURRENCY', 'AED')
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Dubai')
    
    # Material Types (35 items)
    MATERIAL_TYPES = [
        "PVC Conduits & Accessories",
        "Light Fittings (Internal & External)",
        "Light Fittings (Decorative Light fittings)",
        "Cable Gland & Accessories",
        "Earthing & LPS System",
        "GI Conduit & Accessories",
        "Cables & Wires",
        "Wiring Accessories",
        "DB",
        "GRMS",
        "Fire Alarm system",
        "Emergency Lighting system",
        "Structured Cabling System & cctv -low current system",
        "Isolator",
        "VRF System",
        "ERV Unit",
        "GI Duct",
        "Duct Heater",
        "Dampers",
        "Air Outlets",
        "Duct Insulation (Thermal)",
        "Duct Insulation (Thermal)(Alternative)",
        "Duct Insulation (Acoustic)",
        "Sealent. Adhesives,Coating & Vapour Barrier",
        "Flexible Duct",
        "Aluminum Tape",
        "Flexible Duct Connector",
        "Fire Fighting system",
        "Fire Extinguisher",
        "PPR pipe and fittings",
        "Condensation drainpipe",
        "PEX pipe and fittings",
        "Valves",
        "Sanitary wares",
        "Solar Water heater system"
    ]
    
    # Approval Status Options
    APPROVAL_STATUSES = [
        "Approved",
        "Approved as Noted",
        "Pending",
        "Under Review",
        "Revise & Resubmit"
    ]
    
    # PO Status Options
    PO_STATUSES = [
        "Not Released",
        "Released",
        "Cancelled"
    ]
    
    # Delivery Status Options
    DELIVERY_STATUSES = [
        "Pending",
        "In Transit",
        "Partial Delivery",
        "Completed",
        "Delayed"
    ]
    
    # Payment Structure Options
    PAYMENT_STRUCTURES = [
        "Single Payment",
        "Advance + Balance"
    ]
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
