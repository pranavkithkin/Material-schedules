from flask import Flask, render_template, jsonify
from flask_cors import CORS
from config import Config
from models import db
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes import (
        dashboard_bp,
        materials_bp,
        purchase_orders_bp,
        payments_bp,
        deliveries_bp,
        ai_suggestions_bp,
        chat_bp,
        agents_bp,
        analytics_bp
    )
    from routes.uploads import uploads_bp
    from routes.n8n_webhooks import n8n_bp
    from routes.lpo import lpo_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(materials_bp, url_prefix='/api/materials')
    app.register_blueprint(purchase_orders_bp, url_prefix='/api/purchase_orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(deliveries_bp, url_prefix='/api/deliveries')
    app.register_blueprint(ai_suggestions_bp, url_prefix='/api/ai_suggestions')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(analytics_bp)  # No url_prefix, it's defined in the blueprint
    app.register_blueprint(uploads_bp)
    app.register_blueprint(n8n_bp, url_prefix='/api/n8n')
    app.register_blueprint(lpo_bp)  # Already has url_prefix='/api/lpo' in blueprint
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
