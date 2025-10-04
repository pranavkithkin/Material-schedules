"""
API Authentication Module
Provides decorators and utilities for securing API endpoints
"""

from functools import wraps
from flask import request, jsonify, current_app
import secrets

def require_api_key(f):
    """
    Decorator to require API key authentication for endpoints.
    
    Usage:
        @app.route('/api/protected')
        @require_api_key
        def protected_endpoint():
            return jsonify({'message': 'Success'})
    
    API key should be sent in request headers as:
        X-API-Key: your_api_key_here
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from headers
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'API key must be provided in X-API-Key header'
            }), 401
        
        # Get expected API key from config
        expected_key = current_app.config.get('N8N_API_KEY')
        
        if not expected_key:
            return jsonify({
                'error': 'Server configuration error',
                'message': 'API key not configured on server'
            }), 500
        
        # Verify API key
        if api_key != expected_key:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid'
            }), 403
        
        # API key is valid, proceed with the request
        return f(*args, **kwargs)
    
    return decorated_function


def generate_api_key():
    """
    Generate a secure random API key.
    
    Returns:
        str: A URL-safe 32-byte random token
    
    Usage:
        >>> from routes.auth import generate_api_key
        >>> api_key = generate_api_key()
        >>> print(f"New API Key: {api_key}")
    """
    return secrets.token_urlsafe(32)


def validate_api_key(api_key):
    """
    Validate an API key without using a decorator.
    
    Args:
        api_key (str): The API key to validate
    
    Returns:
        tuple: (is_valid, error_message)
    
    Usage:
        is_valid, error = validate_api_key(request.headers.get('X-API-Key'))
        if not is_valid:
            return jsonify({'error': error}), 401
    """
    if not api_key:
        return False, "Missing API key"
    
    from flask import current_app
    expected_key = current_app.config.get('N8N_API_KEY')
    
    if not expected_key:
        return False, "API key not configured on server"
    
    if api_key != expected_key:
        return False, "Invalid API key"
    
    return True, None
