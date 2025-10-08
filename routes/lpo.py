"""
LPO Routes
API endpoints for LPO management
"""
from flask import Blueprint, request, jsonify, send_file, render_template
from models import db
from models.lpo import LPO
from services.lpo_service import LPOService
from services.lpo_pdf_generator import LPOPDFGenerator
from datetime import datetime
import os

# Create blueprint
lpo_bp = Blueprint('lpo', __name__, url_prefix='/api/lpo')


@lpo_bp.route('/create', methods=['POST'])
def create_lpo():
    """
    Create a new LPO
    
    POST /api/lpo/create
    Body: {
        "project_name": "Al Barsha Villa",
        "supplier_name": "ABC Trading LLC",
        "column_structure": ["MAKE", "CODE", "DESCRIPTION", "UNIT", "QTY", "RATE"],
        "items": [
            {
                "make": "Samsung",
                "code": "LED-100",
                "description": "LED Light 10W",
                "unit": "Nos",
                "quantity": 50,
                "rate": 25.00
            }
        ],
        ... other fields
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['project_name', 'supplier_name', 'column_structure', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not data['items']:
            return jsonify({'error': 'At least one item is required'}), 400
        
        # Create LPO
        created_by = request.args.get('user', 'system')
        lpo = LPOService.create_lpo(data, created_by=created_by)
        
        return jsonify({
            'success': True,
            'message': f'LPO {lpo.lpo_number} created successfully',
            'lpo': lpo.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>', methods=['GET'])
def get_lpo(lpo_id):
    """
    Get LPO by ID
    
    GET /api/lpo/123
    """
    try:
        lpo = LPOService.get_lpo(lpo_id)
        if not lpo:
            return jsonify({'error': 'LPO not found'}), 404
        
        return jsonify({
            'success': True,
            'lpo': lpo.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/number/<lpo_number>', methods=['GET'])
def get_lpo_by_number(lpo_number):
    """
    Get LPO by number
    
    GET /api/lpo/number/LPO/PKP/2025/0001
    """
    try:
        lpo = LPOService.get_lpo_by_number(lpo_number)
        if not lpo:
            return jsonify({'error': 'LPO not found'}), 404
        
        return jsonify({
            'success': True,
            'lpo': lpo.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/list', methods=['GET'])
def list_lpos():
    """
    List LPOs with optional filters
    
    GET /api/lpo/list?status=draft&page=1&per_page=20
    """
    try:
        # Get query parameters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('supplier_name'):
            filters['supplier_name'] = request.args.get('supplier_name')
        if request.args.get('project_name'):
            filters['project_name'] = request.args.get('project_name')
        if request.args.get('from_date'):
            filters['from_date'] = datetime.strptime(request.args.get('from_date'), '%Y-%m-%d').date()
        if request.args.get('to_date'):
            filters['to_date'] = datetime.strptime(request.args.get('to_date'), '%Y-%m-%d').date()
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Get paginated results
        pagination = LPOService.list_lpos(filters, page, per_page)
        
        return jsonify({
            'success': True,
            'lpos': [lpo.to_dict() for lpo in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>', methods=['PUT'])
def update_lpo(lpo_id):
    """
    Update an existing LPO
    
    PUT /api/lpo/123
    Body: { ... fields to update ... }
    """
    try:
        data = request.json
        updated_by = request.args.get('user', 'system')
        
        lpo = LPOService.update_lpo(lpo_id, data, updated_by=updated_by)
        
        return jsonify({
            'success': True,
            'message': f'LPO {lpo.lpo_number} updated successfully',
            'lpo': lpo.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>/status', methods=['PATCH'])
def change_status(lpo_id):
    """
    Change LPO status
    
    PATCH /api/lpo/123/status
    Body: {
        "status": "issued",
        "notes": "LPO issued to supplier"
    }
    """
    try:
        data = request.json
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        performed_by = request.args.get('user', 'system')
        notes = data.get('notes')
        
        lpo = LPOService.change_status(lpo_id, data['status'], performed_by, notes)
        
        return jsonify({
            'success': True,
            'message': f'LPO {lpo.lpo_number} status changed to {lpo.status}',
            'lpo': lpo.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>', methods=['DELETE'])
def delete_lpo(lpo_id):
    """
    Delete (cancel) an LPO
    
    DELETE /api/lpo/123
    """
    try:
        performed_by = request.args.get('user', 'system')
        lpo = LPOService.delete_lpo(lpo_id, performed_by)
        
        return jsonify({
            'success': True,
            'message': f'LPO {lpo.lpo_number} cancelled successfully'
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>/pdf', methods=['GET'])
def generate_pdf(lpo_id):
    """
    Generate and download LPO PDF
    
    GET /api/lpo/123/pdf
    """
    try:
        lpo = LPOService.get_lpo(lpo_id)
        if not lpo:
            return jsonify({'error': 'LPO not found'}), 404
        
        # Generate PDF
        pdf_bytes = LPOPDFGenerator.generate_pdf(lpo)
        
        # Get filename
        filename = LPOPDFGenerator.get_pdf_filename(lpo)
        
        # Return PDF file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>/pdf/preview', methods=['GET'])
def preview_pdf(lpo_id):
    """
    Preview LPO PDF in browser
    
    GET /api/lpo/123/pdf/preview
    """
    try:
        lpo = LPOService.get_lpo(lpo_id)
        if not lpo:
            return jsonify({'error': 'LPO not found'}), 404
        
        # Generate PDF
        pdf_bytes = LPOPDFGenerator.generate_pdf(lpo)
        
        # Return PDF for inline viewing
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=False
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/<int:lpo_id>/history', methods=['GET'])
def get_history(lpo_id):
    """
    Get LPO history/audit trail
    
    GET /api/lpo/123/history
    """
    try:
        lpo = LPOService.get_lpo(lpo_id)
        if not lpo:
            return jsonify({'error': 'LPO not found'}), 404
        
        history = [
            {
                'id': h.id,
                'action': h.action,
                'old_status': h.old_status,
                'new_status': h.new_status,
                'changes': h.changes,
                'notes': h.notes,
                'performed_by': h.performed_by,
                'performed_at': h.performed_at.isoformat() if h.performed_at else None
            }
            for h in lpo.history
        ]
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lpo_bp.route('/generate-number', methods=['GET'])
def generate_number():
    """
    Generate next LPO number
    
    GET /api/lpo/generate-number?year=2025
    """
    try:
        year = request.args.get('year', type=int)
        lpo_number = LPOService.generate_lpo_number(year)
        
        return jsonify({
            'success': True,
            'lpo_number': lpo_number
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Import io for BytesIO
import io
