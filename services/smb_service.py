"""
SMB File Server Service
Handles connections and operations with office SMB/CIFS file server
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
import logging

try:
    from smb.SMBConnection import SMBConnection
    from smb.smb_structs import OperationFailure
    SMB_AVAILABLE = True
except ImportError:
    SMB_AVAILABLE = False
    print("⚠️  pysmb not installed. Install with: pip install pysmb")

logger = logging.getLogger(__name__)


class SMBService:
    """Service for managing SMB file server operations"""
    
    def __init__(self):
        """Initialize SMB service with environment configuration"""
        self.server_ip = os.getenv('SMB_SERVER_IP', '192.168.1.100')
        self.server_name = os.getenv('SMB_SERVER_NAME', 'FILE-SERVER')
        self.share_name = os.getenv('SMB_SHARE_NAME', 'Projects')
        self.username = os.getenv('SMB_USERNAME', 'admin')
        self.password = os.getenv('SMB_PASSWORD', '')
        self.domain = os.getenv('SMB_DOMAIN', 'WORKGROUP')
        self.client_name = os.getenv('SMB_CLIENT_NAME', 'PKP-Dashboard')
        
        # Base path for PKP projects on SMB server
        self.base_path = os.getenv('SMB_BASE_PATH', 'PKP_Projects')
        
        self.conn = None
        self.is_connected = False
    
    def connect(self):
        """Establish connection to SMB server"""
        if not SMB_AVAILABLE:
            raise Exception("pysmb library not installed. Run: pip install pysmb")
        
        try:
            # Create SMB connection
            self.conn = SMBConnection(
                username=self.username,
                password=self.password,
                my_name=self.client_name,
                remote_name=self.server_name,
                domain=self.domain,
                use_ntlm_v2=True,
                is_direct_tcp=True
            )
            
            # Connect to server (port 445 for direct TCP)
            self.is_connected = self.conn.connect(self.server_ip, 445)
            
            if not self.is_connected:
                raise Exception("Failed to connect to SMB server")
            
            logger.info(f"✅ Connected to SMB server: {self.server_name} ({self.server_ip})")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMB connection failed: {str(e)}")
            self.is_connected = False
            raise Exception(f"SMB connection failed: {str(e)}")
    
    def disconnect(self):
        """Close SMB connection"""
        if self.conn and self.is_connected:
            self.conn.close()
            self.is_connected = False
            logger.info("Disconnected from SMB server")
    
    def list_folders(self, path=''):
        """
        List folders in the specified path
        
        Args:
            path: Relative path from base_path (e.g., 'Villa_Projects/Villa_123')
        
        Returns:
            List of folder names
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{path}" if path else self.base_path
            
            # List directory contents
            file_list = self.conn.listPath(self.share_name, full_path)
            
            # Filter only directories (exclude . and ..)
            folders = [
                f.filename for f in file_list 
                if f.isDirectory and f.filename not in ['.', '..']
            ]
            
            return sorted(folders)
            
        except Exception as e:
            logger.error(f"Failed to list folders: {str(e)}")
            raise Exception(f"Failed to list folders: {str(e)}")
    
    def list_files(self, path=''):
        """
        List files in the specified path with metadata
        
        Args:
            path: Relative path from base_path
        
        Returns:
            List of dicts with file information
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{path}" if path else self.base_path
            
            # List directory contents
            file_list = self.conn.listPath(self.share_name, full_path)
            
            # Filter only files and get metadata
            files = []
            for f in file_list:
                if not f.isDirectory and f.filename not in ['.', '..']:
                    files.append({
                        'name': f.filename,
                        'size': f.file_size,
                        'size_readable': self._format_size(f.file_size),
                        'modified': datetime.fromtimestamp(f.last_write_time).isoformat(),
                        'modified_readable': datetime.fromtimestamp(f.last_write_time).strftime('%Y-%m-%d %H:%M'),
                        'extension': Path(f.filename).suffix.lower(),
                        'path': f"{path}/{f.filename}" if path else f.filename
                    })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise Exception(f"Failed to list files: {str(e)}")
    
    def upload_file(self, local_file_path, remote_path, filename):
        """
        Upload file to SMB server
        
        Args:
            local_file_path: Path to local file
            remote_path: Remote folder path (relative to base_path)
            filename: Name to save file as
        
        Returns:
            Dict with upload status
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{remote_path}/{filename}" if remote_path else f"{self.base_path}/{filename}"
            
            # Read local file
            with open(local_file_path, 'rb') as local_file:
                # Upload to SMB server
                bytes_uploaded = self.conn.storeFile(
                    self.share_name,
                    full_path,
                    local_file
                )
            
            logger.info(f"✅ Uploaded {bytes_uploaded} bytes to {full_path}")
            
            return {
                'success': True,
                'filename': filename,
                'path': remote_path,
                'bytes_uploaded': bytes_uploaded,
                'size_readable': self._format_size(bytes_uploaded)
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def download_file(self, remote_path, filename):
        """
        Download file from SMB server
        
        Args:
            remote_path: Remote folder path (relative to base_path)
            filename: Name of file to download
        
        Returns:
            Path to temporary downloaded file
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{remote_path}/{filename}" if remote_path else f"{self.base_path}/{filename}"
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix)
            
            # Download from SMB server
            with open(temp_file.name, 'wb') as local_file:
                self.conn.retrieveFile(
                    self.share_name,
                    full_path,
                    local_file
                )
            
            logger.info(f"✅ Downloaded {filename} to {temp_file.name}")
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise Exception(f"Failed to download file: {str(e)}")
    
    def delete_file(self, remote_path, filename):
        """
        Delete file from SMB server
        
        Args:
            remote_path: Remote folder path (relative to base_path)
            filename: Name of file to delete
        
        Returns:
            Dict with deletion status
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{remote_path}/{filename}" if remote_path else f"{self.base_path}/{filename}"
            
            # Delete file
            self.conn.deleteFiles(self.share_name, full_path)
            
            logger.info(f"✅ Deleted {full_path}")
            
            return {
                'success': True,
                'filename': filename,
                'path': remote_path
            }
            
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def create_folder(self, path, folder_name):
        """
        Create new folder on SMB server
        
        Args:
            path: Parent folder path (relative to base_path)
            folder_name: Name of new folder
        
        Returns:
            Dict with creation status
        """
        if not self.is_connected:
            self.connect()
        
        try:
            full_path = f"{self.base_path}/{path}/{folder_name}" if path else f"{self.base_path}/{folder_name}"
            
            # Create directory
            self.conn.createDirectory(self.share_name, full_path)
            
            logger.info(f"✅ Created folder {full_path}")
            
            return {
                'success': True,
                'folder_name': folder_name,
                'path': path
            }
            
        except Exception as e:
            logger.error(f"Failed to create folder: {str(e)}")
            raise Exception(f"Failed to create folder: {str(e)}")
    
    def get_folder_structure(self, path='', max_depth=3, current_depth=0):
        """
        Get hierarchical folder structure
        
        Args:
            path: Starting path
            max_depth: Maximum depth to traverse
            current_depth: Current recursion depth
        
        Returns:
            Nested dict representing folder structure
        """
        if not self.is_connected:
            self.connect()
        
        if current_depth >= max_depth:
            return {}
        
        try:
            folders = self.list_folders(path)
            structure = {}
            
            for folder in folders:
                folder_path = f"{path}/{folder}" if path else folder
                structure[folder] = {
                    'path': folder_path,
                    'subfolders': self.get_folder_structure(folder_path, max_depth, current_depth + 1)
                }
            
            return structure
            
        except Exception as e:
            logger.error(f"Failed to get folder structure: {str(e)}")
            return {}
    
    @staticmethod
    def _format_size(bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    def test_connection(self):
        """Test SMB connection and return server info"""
        try:
            self.connect()
            
            # Try to list shares
            shares = self.conn.listShares()
            share_names = [s.name for s in shares if not s.name.endswith('$')]
            
            # Try to access configured share
            folders = self.list_folders('')
            
            return {
                'success': True,
                'server': f"{self.server_name} ({self.server_ip})",
                'share': self.share_name,
                'base_path': self.base_path,
                'available_shares': share_names,
                'folders_count': len(folders),
                'message': 'SMB connection successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'SMB connection failed'
            }
        finally:
            self.disconnect()


# Global instance
smb_service = SMBService()
