"""
File Upload Routes
Handle document upload, download, and management
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from models import db
from models.file import File
from models.material import Material
from models.purchase_order import PurchaseOrder
from models.payment import Payment
from models.delivery import Delivery

uploads_bp = Blueprint('uploads', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_path():
    """Get organized upload path by year/month"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    path = os.path.join(UPLOAD_FOLDER, year, month)
    os.makedirs(path, exist_ok=True)
    return path, f"{year}/{month}"

def get_file_type_from_mime(mime_type):
    """Determine file type category from MIME type"""
    if 'pdf' in mime_type.lower():
        return 'pdf'
    elif any(x in mime_type.lower() for x in ['image', 'png', 'jpg', 'jpeg']):
        return 'image'
    elif any(x in mime_type.lower() for x in ['word', 'document', 'doc']):
        return 'document'
    elif any(x in mime_type.lower() for x in ['excel', 'spreadsheet', 'xls']):
        return 'spreadsheet'
    return 'other'

@uploads_bp.route('/uploads')
def uploads_page():
    """Upload management page"""
    files = File.query.order_by(File.uploaded_at.desc()).all()
    
    # Get statistics
    stats = {
        'total_files': len(files),
        'pending_processing': len([f for f in files if f.processing_status == 'uploaded']),
        'completed': len([f for f in files if f.processing_status == 'completed']),
        'failed': len([f for f in files if f.processing_status == 'failed']),
        'total_size_mb': sum(f.file_size for f in files) / (1024 * 1024)
    }
    
    return render_template('uploads.html', files=files, stats=stats)

@uploads_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get metadata from form
        file_type = request.form.get('file_type', 'other')
        entity_type = request.form.get('entity_type')  # 'material', 'purchase_order', etc.
        entity_id = request.form.get('entity_id')
        uploaded_by = request.form.get('uploaded_by', 'Unknown')
        
        # Secure the filename and create unique name
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"
        
        # Get organized upload path
        upload_path, relative_path = get_upload_path()
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create database record
        new_file = File(
            filename=filename,
            original_filename=original_filename,
            file_path=os.path.join(relative_path, filename),
            file_type=file_type,
            file_size=file_size,
            mime_type=file.content_type,
            uploaded_by=uploaded_by,
            processing_status='uploaded'
        )
        
        # Link to entity if provided
        if entity_type and entity_id:
            try:
                entity_id = int(entity_id)
                if entity_type == 'material':
                    new_file.material_id = entity_id
                elif entity_type == 'purchase_order':
                    new_file.purchase_order_id = entity_id
                elif entity_type == 'payment':
                    new_file.payment_id = entity_id
                elif entity_type == 'delivery':
                    new_file.delivery_id = entity_id
            except ValueError:
                pass  # Invalid entity_id, skip linking
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file': new_file.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/api/files')
def get_files():
    """Get all files with optional filtering"""
    try:
        # Get query parameters
        file_type = request.args.get('file_type')
        status = request.args.get('status')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        
        # Build query
        query = File.query
        
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        if status:
            query = query.filter_by(processing_status=status)
        
        if entity_type and entity_id:
            try:
                entity_id = int(entity_id)
                if entity_type == 'material':
                    query = query.filter_by(material_id=entity_id)
                elif entity_type == 'purchase_order':
                    query = query.filter_by(purchase_order_id=entity_id)
                elif entity_type == 'payment':
                    query = query.filter_by(payment_id=entity_id)
                elif entity_type == 'delivery':
                    query = query.filter_by(delivery_id=entity_id)
            except ValueError:
                pass
        
        files = query.order_by(File.uploaded_at.desc()).all()
        
        return jsonify({
            'success': True,
            'files': [f.to_dict() for f in files]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/api/files/<int:file_id>')
def get_file(file_id):
    """Get a specific file's metadata"""
    try:
        file = File.query.get_or_404(file_id)
        return jsonify({
            'success': True,
            'file': file.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    try:
        file = File.query.get_or_404(file_id)
        
        # Delete physical file
        full_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/uploads/<path:filename>')
def download_file(filename):
    """Download/serve an uploaded file"""
    try:
        # Security: prevent directory traversal
        filename = secure_filename(filename)
        
        # Find file in database
        file = File.query.filter_by(filename=filename).first_or_404()
        
        # Build full path
        full_path = os.path.join(UPLOAD_FOLDER, file.file_path)
        
        if not os.path.exists(full_path):
            abort(404)
        
        return send_file(
            full_path,
            mimetype=file.mime_type,
            as_attachment=False,  # Display in browser if possible
            download_name=file.original_filename
        )
        
    except Exception as e:
        abort(404)

@uploads_bp.route('/api/files/<int:file_id>/update-status', methods=['PUT'])
def update_file_status(file_id):
    """Update file processing status (for n8n webhooks)"""
    try:
        file = File.query.get_or_404(file_id)
        data = request.json
        
        if 'processing_status' in data:
            file.processing_status = data['processing_status']
        
        if 'extracted_data' in data:
            file.extracted_data = data['extracted_data']
        
        if 'extraction_confidence' in data:
            file.extraction_confidence = data['extraction_confidence']
        
        if 'error_message' in data:
            file.error_message = data['error_message']
        
        if file.processing_status in ['completed', 'failed']:
            file.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File status updated',
            'file': file.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/api/deliveries/<int:delivery_id>/upload-document', methods=['POST'])
def upload_delivery_document(delivery_id):
    """
    Sprint 2: Upload delivery order document and trigger n8n extraction workflow
    This endpoint handles PDF upload and sends it to n8n for Claude API processing
    """
    try:
        # Get the delivery record
        delivery = Delivery.query.get_or_404(delivery_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type (PDF only for delivery orders)
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed for delivery orders'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"delivery_{delivery_id}_{timestamp}_{filename}"
        
        # Get organized upload path
        upload_path, relative_path = get_upload_path()
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create File record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=os.path.join(relative_path, filename),
            file_size=file_size,
            file_type='pdf',
            mime_type='application/pdf',
            delivery_id=delivery_id,  # Link directly to delivery
            processing_status='pending',
            uploaded_by=request.form.get('uploaded_by', 'Manual')
        )
        
        db.session.add(file_record)
        
        # Update delivery record
        delivery.delivery_note_path = file_record.file_path
        delivery.extraction_status = 'pending'
        delivery.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Trigger n8n workflow for document extraction (works for ALL document types)
        try:
            import requests
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk')
            n8n_api_key = os.getenv('N8N_API_KEY', '')
            
            # Build full file URL for n8n to download
            file_url = f"http://localhost:5001/uploads/{filename}"
            
            # Generic webhook payload that works for ALL document types
            webhook_payload = {
                'file_id': file_record.id,
                'file_url': file_url,
                'file_path': file_record.file_path,
                # Include all possible ID fields - n8n will use the right one
                'delivery_id': delivery_id,
                'po_id': delivery.po_id if delivery.purchase_order else None,
                'po_ref': delivery.purchase_order.po_ref if delivery.purchase_order else None,
                'document_context': 'delivery'  # Hint for n8n, but it will auto-detect
            }
            
            # Trigger n8n document intelligence workflow (generic endpoint)
            response = requests.post(
                f"{n8n_webhook_url}/webhook/extract-document",  # Generic endpoint for all document types
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {n8n_api_key}'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ n8n document intelligence triggered for delivery {delivery_id}")
            else:
                print(f"⚠️ n8n workflow trigger failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not trigger n8n workflow: {str(e)}")
            # Don't fail the upload if n8n is unavailable
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully. AI extraction in progress...',
            'delivery_id': delivery_id,
            'file_id': file_record.id,
            'file_path': file_record.file_path,
            'extraction_status': 'pending',
            'n8n_triggered': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/api/purchase-orders/<int:po_id>/upload-document', methods=['POST'])
def upload_po_document(po_id):
    """
    Upload Purchase Order document and trigger n8n extraction workflow
    """
    try:
        # Get the PO record
        po = PurchaseOrder.query.get_or_404(po_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type (PDF only)
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"po_{po_id}_{timestamp}_{filename}"
        
        # Get organized upload path
        upload_path, relative_path = get_upload_path()
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create File record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=os.path.join(relative_path, filename),
            file_size=file_size,
            file_type='pdf',
            mime_type='application/pdf',
            purchase_order_id=po_id,  # Link directly to PO
            processing_status='pending',
            uploaded_by=request.form.get('uploaded_by', 'Manual')
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        # Trigger n8n workflow
        try:
            import requests
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk')
            n8n_api_key = os.getenv('N8N_API_KEY', '')
            
            file_url = f"http://localhost:5001/uploads/{filename}"
            
            webhook_payload = {
                'file_id': file_record.id,
                'file_url': file_url,
                'file_path': file_record.file_path,
                'po_id': po_id,
                'po_ref': po.po_ref,
                'material_id': po.material_id,
                'document_context': 'purchase_order'
            }
            
            response = requests.post(
                f"{n8n_webhook_url}/webhook/extract-document",
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {n8n_api_key}'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ n8n document intelligence triggered for PO {po_id}")
            else:
                print(f"⚠️ n8n workflow trigger failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not trigger n8n workflow: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'PO document uploaded. AI extraction in progress...',
            'po_id': po_id,
            'file_id': file_record.id,
            'file_path': file_record.file_path,
            'extraction_status': 'pending',
            'n8n_triggered': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/api/payments/<int:payment_id>/upload-document', methods=['POST'])
def upload_payment_document(payment_id):
    """
    Upload Invoice/Payment document and trigger n8n extraction workflow
    """
    try:
        # Get the payment record
        payment = Payment.query.get_or_404(payment_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type (PDF only)
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"invoice_{payment_id}_{timestamp}_{filename}"
        
        # Get organized upload path
        upload_path, relative_path = get_upload_path()
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create File record
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_path=os.path.join(relative_path, filename),
            file_size=file_size,
            file_type='pdf',
            mime_type='application/pdf',
            payment_id=payment_id,  # Link directly to payment
            processing_status='pending',
            uploaded_by=request.form.get('uploaded_by', 'Manual')
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        # Trigger n8n workflow
        try:
            import requests
            n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://n8n1.trart.uk')
            n8n_api_key = os.getenv('N8N_API_KEY', '')
            
            file_url = f"http://localhost:5001/uploads/{filename}"
            
            webhook_payload = {
                'file_id': file_record.id,
                'file_url': file_url,
                'file_path': file_record.file_path,
                'payment_id': payment_id,
                'po_id': payment.po_id,
                'po_ref': payment.purchase_order.po_ref if payment.purchase_order else None,
                'document_context': 'invoice'
            }
            
            response = requests.post(
                f"{n8n_webhook_url}/webhook/extract-document",
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {n8n_api_key}'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ n8n document intelligence triggered for payment {payment_id}")
            else:
                print(f"⚠️ n8n workflow trigger failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not trigger n8n workflow: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Invoice uploaded. AI extraction in progress...',
            'payment_id': payment_id,
            'file_id': file_record.id,
            'file_path': file_record.file_path,
            'extraction_status': 'pending',
            'n8n_triggered': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
