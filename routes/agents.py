"""
AGENTS API - Endpoints for AI/Data Processing Agents
Sprint 1: Data Processing Agent endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import db
from services.data_processing_agent import DataProcessingAgent
import os

agents_bp = Blueprint('agents', __name__)


# ============================================================================
# SECURITY DECORATOR
# ============================================================================

def require_api_key(f):
    """Require valid API key for agent endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        # Check if API key matches (for n8n or internal calls)
        expected_key = os.getenv('N8N_TO_FLASK_API_KEY')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'X-API-Key header is required'
            }), 401
        
        if api_key != expected_key:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AGENT 1: DATA PROCESSING AGENT
# ============================================================================

@agents_bp.route('/validate-and-check', methods=['POST'])
@require_api_key
def validate_and_check():
    """
    🎯 MAIN ENDPOINT: Validate data + check duplicates + match invoice to LPO
    
    Called by:
    - Form submissions (before save)
    - n8n workflows (after AI extraction)
    - Manual data entry pages
    
    Request Body:
    {
        "record_type": "lpo_release" | "invoice" | "submittal" | "delivery",
        "data": {
            // Record fields to validate
            "lpo_number": "LPO-2024-001",
            "material_name": "Cement",
            ...
        },
        "check_duplicates": true,  // Optional, default true
        "match_invoice_to_lpo": false  // Optional, default false (invoices only)
    }
    
    Response:
    {
        "success": true,
        "is_valid": true,
        "errors": [],
        "warnings": ["⚠️ Amount is 20% higher than average for this supplier"],
        "duplicates": [],
        "matched_lpo_id": null,
        "confidence_score": null,
        "ready_to_save": true,
        "processing_time_ms": 45
    }
    
    Token Usage: ZERO - Pure Python logic!
    """
    import time
    start_time = time.time()
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'message': 'Request body must be valid JSON'
            }), 400
        
        # Validate required fields
        if 'record_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing record_type',
                'message': 'record_type is required (lpo_release, invoice, submittal, delivery)'
            }), 400
        
        if 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing data',
                'message': 'data object is required'
            }), 400
        
        record_type = data['record_type']
        record_data = data['data']
        check_duplicates = data.get('check_duplicates', True)
        match_invoice_to_lpo = data.get('match_invoice_to_lpo', False)
        
        # Validate record_type
        valid_types = ['lpo_release', 'invoice', 'submittal', 'delivery']
        if record_type not in valid_types:
            return jsonify({
                'success': False,
                'error': 'Invalid record_type',
                'message': f'record_type must be one of: {", ".join(valid_types)}'
            }), 400
        
        # Initialize agent
        agent = DataProcessingAgent(db.session)
        
        # Process data
        result = agent.process_data(
            record_type=record_type,
            data=record_data,
            check_duplicates=check_duplicates,
            match_invoice_to_lpo=match_invoice_to_lpo
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Add metadata
        response = {
            'success': True,
            **result,
            'processing_time_ms': processing_time_ms,
            'token_usage': 0,  # ZERO tokens - pure Python!
            'agent': 'Data Processing Agent v1.0'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'message': str(e),
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }), 500


@agents_bp.route('/validate-and-check/test', methods=['GET'])
def test_endpoint():
    """
    Test endpoint to verify agent is working
    No API key required for testing
    """
    return jsonify({
        'status': 'online',
        'agent': 'Data Processing Agent',
        'version': '1.0',
        'capabilities': [
            'Data validation (all record types)',
            'Duplicate detection (fuzzy + exact matching)',
            'Invoice-LPO matching (multi-strategy)',
            'Real-time anomaly detection',
            'Zero token usage (pure Python)'
        ],
        'supported_record_types': [
            'lpo_release',
            'invoice',
            'submittal',
            'delivery'
        ],
        'endpoints': {
            'validate': '/api/agents/validate-and-check (POST, requires API key)',
            'test': '/api/agents/validate-and-check/test (GET, public)'
        }
    }), 200


# ============================================================================
# BATCH PROCESSING (Optional - for future use)
# ============================================================================

@agents_bp.route('/validate-and-check/batch', methods=['POST'])
@require_api_key
def validate_and_check_batch():
    """
    Batch validation for multiple records at once
    Useful for bulk imports or AI-extracted documents
    
    Request Body:
    {
        "records": [
            {
                "record_type": "lpo_release",
                "data": {...}
            },
            {
                "record_type": "invoice",
                "data": {...}
            }
        ],
        "check_duplicates": true,
        "stop_on_error": false  // Continue processing even if one fails
    }
    
    Response:
    {
        "success": true,
        "results": [
            {"index": 0, "is_valid": true, ...},
            {"index": 1, "is_valid": false, ...}
        ],
        "summary": {
            "total": 2,
            "valid": 1,
            "invalid": 1,
            "duplicates_found": 0
        }
    }
    """
    import time
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'records' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing records',
                'message': 'records array is required'
            }), 400
        
        records = data['records']
        check_duplicates = data.get('check_duplicates', True)
        stop_on_error = data.get('stop_on_error', False)
        
        if not isinstance(records, list):
            return jsonify({
                'success': False,
                'error': 'Invalid records format',
                'message': 'records must be an array'
            }), 400
        
        # Initialize agent
        agent = DataProcessingAgent(db.session)
        
        # Process each record
        results = []
        summary = {
            'total': len(records),
            'valid': 0,
            'invalid': 0,
            'duplicates_found': 0
        }
        
        for idx, record in enumerate(records):
            try:
                if 'record_type' not in record or 'data' not in record:
                    results.append({
                        'index': idx,
                        'success': False,
                        'error': 'Missing record_type or data'
                    })
                    summary['invalid'] += 1
                    if stop_on_error:
                        break
                    continue
                
                result = agent.process_data(
                    record_type=record['record_type'],
                    data=record['data'],
                    check_duplicates=check_duplicates,
                    match_invoice_to_lpo=record.get('match_invoice_to_lpo', False)
                )
                
                results.append({
                    'index': idx,
                    'success': True,
                    **result
                })
                
                if result['is_valid']:
                    summary['valid'] += 1
                else:
                    summary['invalid'] += 1
                
                if result.get('duplicates'):
                    summary['duplicates_found'] += len(result['duplicates'])
                
            except Exception as e:
                results.append({
                    'index': idx,
                    'success': False,
                    'error': str(e)
                })
                summary['invalid'] += 1
                if stop_on_error:
                    break
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary,
            'processing_time_ms': processing_time_ms,
            'avg_time_per_record_ms': processing_time_ms // len(records) if records else 0
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Batch validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Batch processing failed',
            'message': str(e)
        }), 500
