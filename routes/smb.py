"""
SMB File Server Routes
API endpoints for SMB file operations
"""

from flask import Blueprint, request, jsonify, send_file
from services.smb_service import smb_service
import os
import tempfile
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

smb_bp = Blueprint('smb', __name__)


@smb_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Test SMB server connection"""
    try:
        result = smb_service.test_connection()
        return jsonify(result), 200 if result['success'] else 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@smb_bp.route('/folders', methods=['GET'])
def list_folders():
    """
    List folders in specified path
    Query params: path (optional)
    """
    try:
        path = request.args.get('path', '')
        folders = smb_service.list_folders(path)
        
        return jsonify({
            'success': True,
            'path': path,
            'folders': folders,
            'count': len(folders)
        })
    except Exception as e:
        logger.error(f"Failed to list folders: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()


@smb_bp.route('/files', methods=['GET'])
def list_files():
    """
    List files in specified path
    Query params: path (optional)
    """
    try:
        path = request.args.get('path', '')
        files = smb_service.list_files(path)
        
        return jsonify({
            'success': True,
            'path': path,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()


@smb_bp.route('/structure', methods=['GET'])
def get_structure():
    """
    Get hierarchical folder structure
    Query params: path (optional), max_depth (optional, default 3)
    """
    try:
        path = request.args.get('path', '')
        max_depth = int(request.args.get('max_depth', 3))
        
        structure = smb_service.get_folder_structure(path, max_depth)
        
        return jsonify({
            'success': True,
            'path': path,
            'structure': structure
        })
    except Exception as e:
        logger.error(f"Failed to get structure: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()


@smb_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload file to SMB server
    Form data: file, path (folder path), project_name (optional)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Get path and project name
        path = request.form.get('path', '')
        project_name = request.form.get('project_name', '')
        
        # If project name provided, append to path
        if project_name:
            path = f"{path}/{project_name}" if path else project_name
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            # Upload to SMB server
            result = smb_service.upload_file(temp_file.name, path, filename)
            
            return jsonify({
                'success': True,
                'message': f'File uploaded successfully to {path}',
                **result
            })
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            smb_service.disconnect()
    
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@smb_bp.route('/download', methods=['GET'])
def download_file():
    """
    Download file from SMB server
    Query params: path, filename
    """
    try:
        path = request.args.get('path', '')
        filename = request.args.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        # Download file to temp location
        temp_file_path = smb_service.download_file(path, filename)
        
        # Send file to client
        response = send_file(
            temp_file_path,
            as_attachment=True,
            download_name=filename
        )
        
        # Clean up temp file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(temp_file_path)
            except:
                pass
            smb_service.disconnect()
        
        return response
    
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        smb_service.disconnect()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@smb_bp.route('/delete', methods=['DELETE'])
def delete_file():
    """
    Delete file from SMB server
    JSON body: path, filename
    """
    try:
        data = request.get_json()
        path = data.get('path', '')
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        result = smb_service.delete_file(path, filename)
        
        return jsonify({
            'success': True,
            'message': f'File deleted successfully',
            **result
        })
    
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()


@smb_bp.route('/create-folder', methods=['POST'])
def create_folder():
    """
    Create new folder on SMB server
    JSON body: path (parent path), folder_name
    """
    try:
        data = request.get_json()
        path = data.get('path', '')
        folder_name = data.get('folder_name')
        
        if not folder_name:
            return jsonify({
                'success': False,
                'error': 'Folder name is required'
            }), 400
        
        result = smb_service.create_folder(path, folder_name)
        
        return jsonify({
            'success': True,
            'message': f'Folder created successfully',
            **result
        })
    
    except Exception as e:
        logger.error(f"Failed to create folder: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()


@smb_bp.route('/browse', methods=['GET'])
def browse():
    """
    Browse both folders and files in one request
    Query params: path (optional)
    """
    try:
        path = request.args.get('path', '')
        
        folders = smb_service.list_folders(path)
        files = smb_service.list_files(path)
        
        return jsonify({
            'success': True,
            'path': path,
            'folders': folders,
            'files': files,
            'folders_count': len(folders),
            'files_count': len(files)
        })
    
    except Exception as e:
        logger.error(f"Failed to browse: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        smb_service.disconnect()
