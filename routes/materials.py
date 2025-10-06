from flask import Blueprint, request, jsonify
from models import db
from models.material import Material
from config import Config
from datetime import datetime

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('', methods=['GET'])
def get_materials():
    """Get all materials"""
    try:
        materials = Material.query.all()
        return jsonify([material.to_dict() for material in materials])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/<int:id>', methods=['GET'])
def get_material(id):
    """Get a specific material"""
    try:
        material = Material.query.get_or_404(id)
        return jsonify(material.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@materials_bp.route('', methods=['POST'])
def create_material():
    """Create a new material"""
    try:
        data = request.get_json()
        
        material = Material(
            material_type=data.get('material_type'),
            description=data.get('description'),
            approval_status=data.get('approval_status', 'Pending'),
            approval_notes=data.get('approval_notes'),
            submittal_ref=data.get('submittal_ref'),
            specification_ref=data.get('specification_ref'),
            revision_number=data.get('revision_number', 0),
            previous_submittal_id=data.get('previous_submittal_id'),
            document_path=data.get('document_path'),
            created_by=data.get('created_by', 'Manual')
        )
        
        if data.get('approval_date'):
            material.approval_date = datetime.fromisoformat(data['approval_date'])
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({
            'message': 'Material created successfully',
            'material': material.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/<int:id>', methods=['PUT'])
def update_material(id):
    """Update a material"""
    try:
        material = Material.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'material_type' in data:
            material.material_type = data['material_type']
        if 'description' in data:
            material.description = data['description']
        if 'approval_status' in data:
            material.approval_status = data['approval_status']
        if 'approval_notes' in data:
            material.approval_notes = data['approval_notes']
        if 'submittal_ref' in data:
            material.submittal_ref = data['submittal_ref']
        if 'specification_ref' in data:
            material.specification_ref = data['specification_ref']
        if 'revision_number' in data:
            material.revision_number = data['revision_number']
        if 'previous_submittal_id' in data:
            material.previous_submittal_id = data['previous_submittal_id']
        if 'document_path' in data:
            material.document_path = data['document_path']
        if 'approval_date' in data:
            material.approval_date = datetime.fromisoformat(data['approval_date']) if data['approval_date'] else None
        
        material.updated_by = data.get('updated_by', 'Manual')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Material updated successfully',
            'material': material.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/<int:id>', methods=['DELETE'])
def delete_material(id):
    """Delete a material"""
    try:
        material = Material.query.get_or_404(id)
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'message': 'Material deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@materials_bp.route('/types', methods=['GET'])
def get_material_types():
    """Get list of all material types"""
    return jsonify(Config.MATERIAL_TYPES)

@materials_bp.route('/statuses', methods=['GET'])
def get_approval_statuses():
    """Get list of approval statuses"""
    return jsonify(Config.APPROVAL_STATUSES)
