/**
 * SMB File Server Browser - Enterprise JavaScript
 * Handles all file operations with office SMB server
 */

// Global state
let currentPath = '';
let currentView = 'grid';
let allFiles = [];
let allFolders = [];
let selectedFiles = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('📁 File Server Browser initialized');
    loadBrowse('');
});

/**
 * Test SMB server connection
 */
async function testConnection() {
    try {
        showToast('Testing connection...', 'info');
        
        const response = await fetch('/api/smb/test-connection');
        const data = await response.json();
        
        if (data.success) {
            showConnectionStatus(true, data);
            showToast(`✅ Connected to ${data.server}`, 'success');
        } else {
            showConnectionStatus(false, data);
            showToast(`❌ Connection failed: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Connection test failed:', error);
        showToast('Connection test failed', 'error');
    }
}

/**
 * Show connection status banner
 */
function showConnectionStatus(success, data) {
    const banner = document.getElementById('connection-status');
    banner.classList.remove('hidden');
    
    if (success) {
        banner.className = 'mb-4 p-4 rounded-lg bg-green-50 border border-green-200';
        banner.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-semibold text-green-800">✅ Connected to SMB Server</p>
                    <p class="text-sm text-green-700 mt-1">
                        Server: ${data.server} | Share: ${data.share} | Folders: ${data.folders_count}
                    </p>
                </div>
                <button onclick="this.parentElement.parentElement.classList.add('hidden')" 
                        class="text-green-600 hover:text-green-800">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else {
        banner.className = 'mb-4 p-4 rounded-lg bg-red-50 border border-red-200';
        banner.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-semibold text-red-800">❌ SMB Connection Failed</p>
                    <p class="text-sm text-red-700 mt-1">${data.error || 'Check server configuration'}</p>
                </div>
                <button onclick="this.parentElement.parentElement.classList.add('hidden')" 
                        class="text-red-600 hover:text-red-800">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
}

/**
 * Load and browse folder content
 */
async function loadBrowse(path) {
    try {
        currentPath = path;
        updateBreadcrumb(path);
        
        // Show loading
        document.getElementById('files-container').innerHTML = `
            <div class="text-center text-gray-400 py-8">
                <i class="fas fa-spinner fa-spin text-3xl"></i>
                <p class="mt-3">Loading...</p>
            </div>
        `;
        
        const response = await fetch(`/api/smb/browse?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.success) {
            allFolders = data.folders || [];
            allFiles = data.files || [];
            
            renderFolders(allFolders);
            renderFiles(allFiles);
            updateStats();
            
            // Load folder tree
            loadFolderTree();
        } else {
            showToast('Failed to load files: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Browse failed:', error);
        showToast('Failed to load files', 'error');
    }
}

/**
 * Update breadcrumb navigation
 */
function updateBreadcrumb(path) {
    const trail = document.getElementById('breadcrumb-trail');
    
    if (!path) {
        trail.innerHTML = '';
        return;
    }
    
    const parts = path.split('/').filter(p => p);
    let html = '';
    let cumulative = '';
    
    parts.forEach((part, index) => {
        cumulative += (cumulative ? '/' : '') + part;
        const pathCopy = cumulative; // Capture for closure
        
        html += `
            <span class="text-gray-400">/</span>
            <button onclick="navigateToPath('${pathCopy}')" 
                    class="text-pkp-green hover:text-pkp-gold transition font-medium">
                ${part}
            </button>
        `;
    });
    
    trail.innerHTML = html;
}

/**
 * Navigate to specific path
 */
function navigateToPath(path) {
    loadBrowse(path);
}

/**
 * Render folders
 */
function renderFolders(folders) {
    const container = document.getElementById('folders-grid');
    
    if (folders.length === 0) {
        document.getElementById('folders-section').classList.add('hidden');
        return;
    }
    
    document.getElementById('folders-section').classList.remove('hidden');
    
    container.innerHTML = folders.map(folder => `
        <div class="folder-item bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4 cursor-pointer hover:shadow-lg transition"
             onclick="navigateToPath('${currentPath ? currentPath + '/' + folder : folder}')">
            <div class="flex flex-col items-center">
                <i class="fas fa-folder text-yellow-500 text-4xl mb-2"></i>
                <span class="text-sm font-medium text-gray-700 text-center truncate w-full" title="${folder}">
                    ${folder}
                </span>
            </div>
        </div>
    `).join('');
}

/**
 * Render files based on current view
 */
function renderFiles(files) {
    const container = document.getElementById('files-container');
    
    if (files.length === 0) {
        container.innerHTML = `
            <div class="text-center text-gray-400 py-8">
                <i class="fas fa-folder-open text-5xl mb-3"></i>
                <p class="text-lg">No files in this folder</p>
                <p class="text-sm mt-2">Upload files to get started</p>
            </div>
        `;
        return;
    }
    
    if (currentView === 'grid') {
        renderGridView(files, container);
    } else {
        renderListView(files, container);
    }
}

/**
 * Render grid view
 */
function renderGridView(files, container) {
    container.innerHTML = `
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            ${files.map(file => `
                <div class="file-item bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
                    <div class="flex flex-col items-center">
                        <div class="file-icon ${getFileIconClass(file.extension)} mb-3">
                            <i class="fas ${getFileIcon(file.extension)}"></i>
                        </div>
                        <span class="text-sm font-medium text-gray-700 text-center truncate w-full mb-2" title="${file.name}">
                            ${file.name}
                        </span>
                        <span class="text-xs text-gray-500">${file.size_readable}</span>
                        <span class="text-xs text-gray-400">${file.modified_readable}</span>
                        
                        <div class="flex space-x-2 mt-3">
                            <button onclick="downloadFile('${currentPath}', '${file.name}')" 
                                    class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition"
                                    title="Download">
                                <i class="fas fa-download"></i>
                            </button>
                            ${canPreview(file.extension) ? `
                                <button onclick="previewFile('${currentPath}', '${file.name}', '${file.extension}')" 
                                        class="px-3 py-1 bg-purple-500 hover:bg-purple-600 text-white rounded text-xs transition"
                                        title="Preview">
                                    <i class="fas fa-eye"></i>
                                </button>
                            ` : ''}
                            <button onclick="deleteFile('${currentPath}', '${file.name}')" 
                                    class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-xs transition"
                                    title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Render list view
 */
function renderListView(files, container) {
    container.innerHTML = `
        <div class="space-y-2">
            ${files.map(file => `
                <div class="file-item bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition flex items-center justify-between">
                    <div class="flex items-center space-x-4 flex-1">
                        <div class="file-icon ${getFileIconClass(file.extension)}">
                            <i class="fas ${getFileIcon(file.extension)}"></i>
                        </div>
                        <div class="flex-1">
                            <p class="font-medium text-gray-700">${file.name}</p>
                            <p class="text-xs text-gray-500">${file.size_readable} • ${file.modified_readable}</p>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="downloadFile('${currentPath}', '${file.name}')" 
                                class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded transition"
                                title="Download">
                            <i class="fas fa-download mr-2"></i> Download
                        </button>
                        ${canPreview(file.extension) ? `
                            <button onclick="previewFile('${currentPath}', '${file.name}', '${file.extension}')" 
                                    class="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded transition"
                                    title="Preview">
                                <i class="fas fa-eye mr-2"></i> Preview
                            </button>
                        ` : ''}
                        <button onclick="deleteFile('${currentPath}', '${file.name}')" 
                                class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition"
                                title="Delete">
                            <i class="fas fa-trash mr-2"></i> Delete
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Get file icon based on extension
 */
function getFileIcon(extension) {
    const icons = {
        '.pdf': 'fa-file-pdf',
        '.doc': 'fa-file-word',
        '.docx': 'fa-file-word',
        '.xls': 'fa-file-excel',
        '.xlsx': 'fa-file-excel',
        '.ppt': 'fa-file-powerpoint',
        '.pptx': 'fa-file-powerpoint',
        '.jpg': 'fa-file-image',
        '.jpeg': 'fa-file-image',
        '.png': 'fa-file-image',
        '.gif': 'fa-file-image',
        '.zip': 'fa-file-archive',
        '.rar': 'fa-file-archive',
        '.txt': 'fa-file-alt',
        '.csv': 'fa-file-csv'
    };
    
    return icons[extension] || 'fa-file';
}

/**
 * Get file icon color class
 */
function getFileIconClass(extension) {
    if (['.pdf'].includes(extension)) return 'pdf';
    if (['.doc', '.docx'].includes(extension)) return 'doc';
    if (['.xls', '.xlsx'].includes(extension)) return 'xls';
    if (['.jpg', '.jpeg', '.png', '.gif'].includes(extension)) return 'img';
    return 'default';
}

/**
 * Check if file can be previewed
 */
function canPreview(extension) {
    return ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt'].includes(extension);
}

/**
 * Set view mode (grid or list)
 */
function setView(view) {
    currentView = view;
    
    // Update button styles
    const gridBtn = document.getElementById('btn-grid-view');
    const listBtn = document.getElementById('btn-list-view');
    
    if (view === 'grid') {
        gridBtn.className = 'px-3 py-1.5 bg-pkp-green text-white rounded transition';
        listBtn.className = 'px-3 py-1.5 bg-gray-200 text-gray-700 rounded transition';
    } else {
        gridBtn.className = 'px-3 py-1.5 bg-gray-200 text-gray-700 rounded transition';
        listBtn.className = 'px-3 py-1.5 bg-pkp-green text-white rounded transition';
    }
    
    renderFiles(allFiles);
}

/**
 * Filter files by search term
 */
function filterFiles() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    if (!searchTerm) {
        renderFiles(allFiles);
        return;
    }
    
    const filtered = allFiles.filter(file => 
        file.name.toLowerCase().includes(searchTerm)
    );
    
    renderFiles(filtered);
}

/**
 * Refresh current folder
 */
function refreshFiles() {
    loadBrowse(currentPath);
    showToast('Refreshed', 'success');
}

/**
 * Update stats display
 */
function updateStats() {
    document.getElementById('stats-files').textContent = allFiles.length;
    document.getElementById('stats-folders').textContent = allFolders.length;
    
    const totalSize = allFiles.reduce((sum, file) => sum + file.size, 0);
    document.getElementById('stats-size').textContent = formatBytes(totalSize);
}

/**
 * Load folder tree
 */
async function loadFolderTree() {
    try {
        const response = await fetch(`/api/smb/structure?path=&max_depth=2`);
        const data = await response.json();
        
        if (data.success) {
            renderFolderTree(data.structure);
        }
    } catch (error) {
        console.error('Failed to load folder tree:', error);
    }
}

/**
 * Render folder tree
 */
function renderFolderTree(structure) {
    const container = document.getElementById('folder-tree');
    
    if (Object.keys(structure).length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500">No folders</p>';
        return;
    }
    
    function renderNode(name, node, path) {
        const hasChildren = Object.keys(node.subfolders).length > 0;
        const fullPath = path ? `${path}/${name}` : name;
        
        return `
            <div class="folder-node">
                <div class="flex items-center space-x-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer text-sm"
                     onclick="navigateToPath('${fullPath}')">
                    <i class="fas fa-folder text-yellow-500"></i>
                    <span class="flex-1 truncate">${name}</span>
                    ${hasChildren ? '<i class="fas fa-chevron-right text-xs text-gray-400"></i>' : ''}
                </div>
                ${hasChildren ? `
                    <div class="ml-4 border-l border-gray-200 pl-2">
                        ${Object.entries(node.subfolders).map(([childName, childNode]) => 
                            renderNode(childName, childNode, fullPath)
                        ).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    container.innerHTML = Object.entries(structure).map(([name, node]) => 
        renderNode(name, node, '')
    ).join('');
}

// ============================================================================
// Upload Functions
// ============================================================================

function showUploadModal() {
    document.getElementById('upload-modal').classList.remove('hidden');
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    selectedFiles = [];
    document.getElementById('selected-files').classList.add('hidden');
    document.getElementById('upload-progress').classList.add('hidden');
    document.getElementById('file-input').value = '';
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-zone').classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-zone').classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-zone').classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function handleFiles(files) {
    selectedFiles = files;
    displaySelectedFiles();
    document.getElementById('upload-btn').disabled = false;
}

function displaySelectedFiles() {
    const container = document.getElementById('files-list');
    document.getElementById('selected-files').classList.remove('hidden');
    document.getElementById('file-count').textContent = selectedFiles.length;
    
    container.innerHTML = selectedFiles.map((file, index) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center space-x-3">
                <i class="fas ${getFileIcon(getExtension(file.name))} text-xl text-gray-600"></i>
                <div>
                    <p class="font-medium text-sm">${file.name}</p>
                    <p class="text-xs text-gray-500">${formatBytes(file.size)}</p>
                </div>
            </div>
            <button onclick="removeFile(${index})" class="text-red-500 hover:text-red-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    
    if (selectedFiles.length === 0) {
        document.getElementById('selected-files').classList.add('hidden');
        document.getElementById('upload-btn').disabled = true;
    } else {
        displaySelectedFiles();
    }
}

async function uploadFiles() {
    if (selectedFiles.length === 0) return;
    
    const progressBar = document.getElementById('upload-bar');
    const progressText = document.getElementById('upload-percentage');
    const progressContainer = document.getElementById('upload-progress');
    
    progressContainer.classList.remove('hidden');
    document.getElementById('upload-btn').disabled = true;
    
    let uploaded = 0;
    
    for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', currentPath);
        
        try {
            const response = await fetch('/api/smb/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                uploaded++;
                const progress = Math.round((uploaded / selectedFiles.length) * 100);
                progressBar.style.width = progress + '%';
                progressText.textContent = progress + '%';
            } else {
                showToast(`Failed to upload ${file.name}: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            showToast(`Failed to upload ${file.name}`, 'error');
        }
    }
    
    showToast(`Successfully uploaded ${uploaded} file(s)`, 'success');
    closeUploadModal();
    refreshFiles();
}

// ============================================================================
// Folder Functions
// ============================================================================

function showCreateFolderModal() {
    document.getElementById('folder-modal').classList.remove('hidden');
    document.getElementById('folder-name-input').focus();
}

function closeFolderModal() {
    document.getElementById('folder-modal').classList.add('hidden');
    document.getElementById('folder-name-input').value = '';
}

async function createFolder() {
    const folderName = document.getElementById('folder-name-input').value.trim();
    
    if (!folderName) {
        showToast('Please enter a folder name', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/smb/create-folder', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                path: currentPath,
                folder_name: folderName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Folder created successfully', 'success');
            closeFolderModal();
            refreshFiles();
        } else {
            showToast('Failed to create folder: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Create folder failed:', error);
        showToast('Failed to create folder', 'error');
    }
}

// ============================================================================
// File Operations
// ============================================================================

async function downloadFile(path, filename) {
    try {
        showToast('Downloading...', 'info');
        
        const url = `/api/smb/download?path=${encodeURIComponent(path)}&filename=${encodeURIComponent(filename)}`;
        window.open(url, '_blank');
        
        showToast('Download started', 'success');
    } catch (error) {
        console.error('Download failed:', error);
        showToast('Download failed', 'error');
    }
}

async function deleteFile(path, filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/smb/delete', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path, filename })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('File deleted successfully', 'success');
            refreshFiles();
        } else {
            showToast('Failed to delete file: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Delete failed:', error);
        showToast('Failed to delete file', 'error');
    }
}

function previewFile(path, filename, extension) {
    // For now, just download - will implement preview in next iteration
    downloadFile(path, filename);
}

function closePreviewModal() {
    document.getElementById('preview-modal').classList.add('hidden');
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 10) / 10 + ' ' + sizes[i];
}

function getExtension(filename) {
    return '.' + filename.split('.').pop().toLowerCase();
}

function showToast(message, type = 'info') {
    // Use existing toast system from base.html
    if (window.showNotification) {
        window.showNotification(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}
