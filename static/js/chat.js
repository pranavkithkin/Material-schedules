// Chat Interface JavaScript

// Global variable to store attached file
let chatAttachedFile = null;

$(document).ready(function() {
    const chatFloatBtn = $('#chat-float-btn');
    const chatModal = $('#chat-modal');
    const chatForm = $('#chat-form');
    const chatInput = $('#chat-input');
    const chatMessages = $('#chat-messages');
    
    // Toggle chat modal
    chatFloatBtn.on('click', function() {
        chatModal.removeClass('hidden');
        chatInput.focus();
    });
    
    // Close chat modal
    window.closeChatModal = function() {
        chatModal.addClass('hidden');
        removeChatAttachment(); // Clear any attached files when closing
    };
    
    // Close on background click
    chatModal.on('click', function(e) {
        if (e.target === this) {
            closeChatModal();
        }
    });
    
    // Handle chat form submission
    chatForm.on('submit', function(e) {
        e.preventDefault();
        
        const query = chatInput.val().trim();
        
        // Check if there's a file attached
        if (chatAttachedFile) {
            handleDocumentUpload(query);
        } else {
            // Regular text query
            if (!query) return;
            
            // Add user message to chat
            addMessage(query, 'user');
            
            // Clear input
            chatInput.val('');
            
            // Show typing indicator
            addTypingIndicator();
            
            // Send query to server
            $.ajax({
                url: '/api/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ query: query }),
                success: function(response) {
                    removeTypingIndicator();
                    addMessage(response.answer, 'ai', response.data);
                },
                error: function(err) {
                    removeTypingIndicator();
                    addMessage('Sorry, I encountered an error processing your request.', 'ai');
                    console.error('Chat error:', err);
                }
            });
        }
    });
    
    // Handle suggested queries
    window.sendSuggestedQuery = function(query) {
        chatInput.val(query);
        chatForm.submit();
    };
    
    function handleDocumentUpload(userMessage) {
        const docType = $('#chat-doc-type').val();
        const fileName = chatAttachedFile.name;
        
        // Display user message with document info
        const messageText = userMessage || `Processing ${docType.replace('_', ' ')} document...`;
        addDocumentMessage(fileName, messageText, 'user');
        
        // Clear input and attachment
        chatInput.val('');
        
        // Show typing indicator
        addTypingIndicator();
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', chatAttachedFile);
        formData.append('doc_type', docType);
        formData.append('user_message', userMessage);
        
        // Upload file and process
        $.ajax({
            url: '/api/chat/upload',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                removeTypingIndicator();
                
                if (response.success) {
                    // Show success message with extracted data
                    const resultMessage = response.message || 'Document processed successfully!';
                    addMessage(resultMessage, 'ai', response.data);
                    
                    // Show processing details
                    if (response.details) {
                        addMessage(response.details, 'ai');
                    }
                } else {
                    addMessage(response.message || 'Failed to process document.', 'ai');
                }
                
                // Clear attachment
                removeChatAttachment();
            },
            error: function(err) {
                removeTypingIndicator();
                removeChatAttachment();
                
                let errorMsg = 'Sorry, I encountered an error processing your document.';
                if (err.responseJSON && err.responseJSON.message) {
                    errorMsg = err.responseJSON.message;
                }
                addMessage(errorMsg, 'ai');
                console.error('Document upload error:', err);
            }
        });
    }
    
    function addMessage(text, sender, data = null) {
        const isUser = sender === 'user';
        
        let messageHtml = '';
        
        if (isUser) {
            // User message (right aligned)
            messageHtml = `
                <div class="flex items-start space-x-3 justify-end animate-fade-in">
                    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl rounded-tr-none p-4 shadow-sm max-w-[80%]">
                        <p class="text-sm">${escapeHtml(text)}</p>
                    </div>
                    <div class="bg-gray-300 text-gray-600 p-2 rounded-full flex-shrink-0">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            `;
        } else {
            // AI message (left aligned)
            messageHtml = `
                <div class="flex items-start space-x-3 animate-fade-in">
                    <div class="bg-blue-600 text-white p-2 rounded-full flex-shrink-0">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="bg-white rounded-2xl rounded-tl-none p-4 shadow-sm max-w-[80%]">
                        <p class="text-gray-800 text-sm">${escapeHtml(text)}</p>
                        ${data ? formatData(data) : ''}
                    </div>
                </div>
            `;
        }
        
        chatMessages.append(messageHtml);
        scrollToBottom();
    }
    
    function addDocumentMessage(fileName, userMessage, sender) {
        const messageHtml = `
            <div class="flex items-start space-x-3 justify-end animate-fade-in">
                <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl rounded-tr-none p-4 shadow-sm max-w-[80%]">
                    <div class="flex items-center space-x-2 mb-2">
                        <i class="fas fa-file-alt text-lg"></i>
                        <p class="text-xs font-semibold">${escapeHtml(fileName)}</p>
                    </div>
                    <p class="text-sm">${escapeHtml(userMessage)}</p>
                </div>
                <div class="bg-gray-300 text-gray-600 p-2 rounded-full flex-shrink-0">
                    <i class="fas fa-user"></i>
                </div>
            </div>
        `;
        chatMessages.append(messageHtml);
        scrollToBottom();
    }
    
    function formatData(data) {
        if (Array.isArray(data) && data.length > 0) {
            return formatDataTable(data);
        } else if (typeof data === 'object' && Object.keys(data).length > 0) {
            return formatDataObject(data);
        }
        return '';
    }
    
    function formatDataTable(dataArray) {
        let html = '<div class="mt-3 bg-gray-50 rounded-lg p-3 text-xs max-w-full overflow-x-auto border border-gray-200">';
        html += '<table class="min-w-full text-left">';
        
        // Headers
        const keys = Object.keys(dataArray[0]);
        html += '<thead class="border-b border-gray-300"><tr>';
        keys.forEach(key => {
            html += `<th class="px-2 py-2 font-semibold text-gray-700 capitalize">${escapeHtml(key.replace(/_/g, ' '))}</th>`;
        });
        html += '</tr></thead>';
        
        // Rows (limit to 5 for display)
        html += '<tbody>';
        dataArray.slice(0, 5).forEach((row, idx) => {
            html += `<tr class="${idx < dataArray.length - 1 ? 'border-b border-gray-200' : ''}">`;
            keys.forEach(key => {
                let value = row[key] || 'N/A';
                // Format based on key name
                if (key.includes('amount') || key.includes('value')) {
                    value = typeof value === 'number' ? `AED ${value.toLocaleString()}` : value;
                }
                html += `<td class="px-2 py-2 text-gray-600">${escapeHtml(String(value))}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        
        if (dataArray.length > 5) {
            html += `<p class="text-gray-500 text-center mt-2">... and ${dataArray.length - 5} more</p>`;
        }
        
        html += '</div>';
        return html;
    }
    
    function formatDataObject(dataObj) {
        let html = '<div class="mt-3 bg-gray-50 rounded-lg p-3 text-xs border border-gray-200">';
        html += '<dl class="space-y-2">';
        
        for (const [key, value] of Object.entries(dataObj)) {
            let displayValue = value;
            
            // Format numbers
            if (typeof value === 'number') {
                if (key.includes('amount') || key.includes('value')) {
                    displayValue = `AED ${value.toLocaleString()}`;
                } else if (key.includes('percentage') || key.includes('rate')) {
                    displayValue = `${value}%`;
                } else {
                    displayValue = value.toLocaleString();
                }
            }
            
            // Format nested objects
            if (typeof value === 'object' && !Array.isArray(value)) {
                displayValue = '<div class="mt-1 pl-3 border-l-2 border-blue-300">';
                for (const [subKey, subValue] of Object.entries(value)) {
                    displayValue += `<div class="flex justify-between py-1"><span class="text-gray-600">${escapeHtml(subKey)}:</span><span class="font-semibold text-gray-800">${escapeHtml(String(subValue))}</span></div>`;
                }
                displayValue += '</div>';
            }
            
            html += `
                <div class="flex justify-between items-start">
                    <dt class="font-semibold text-gray-700 capitalize">${escapeHtml(key.replace(/_/g, ' '))}:</dt>
                    <dd class="text-gray-800 font-medium ml-2">${typeof displayValue === 'string' ? displayValue : escapeHtml(String(displayValue))}</dd>
                </div>
            `;
        }
        
        html += '</dl></div>';
        return html;
    }
    
    function addTypingIndicator() {
        const indicator = `
            <div id="typing-indicator" class="flex items-start space-x-3 animate-fade-in">
                <div class="bg-blue-600 text-white p-2 rounded-full flex-shrink-0">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="bg-white rounded-2xl rounded-tl-none p-4 shadow-sm">
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.append(indicator);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        $('#typing-indicator').remove();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop(chatMessages[0].scrollHeight);
    }
    
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
});

// File handling functions
window.handleChatFileSelect = function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF, PNG, or JPG file.');
        return;
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        alert('File size must be less than 10MB.');
        return;
    }
    
    // Store the file
    chatAttachedFile = file;
    
    // Show preview
    showFilePreview(file);
};

function showFilePreview(file) {
    const preview = $('#chat-file-preview');
    const fileName = $('#preview-file-name');
    const fileSize = $('#preview-file-size');
    const fileIcon = $('#preview-file-icon');
    
    // Update file info
    fileName.text(file.name);
    fileSize.text(formatFileSize(file.size));
    
    // Update icon based on file type
    if (file.type === 'application/pdf') {
        fileIcon.removeClass().addClass('fas fa-file-pdf');
    } else if (file.type.startsWith('image/')) {
        fileIcon.removeClass().addClass('fas fa-file-image');
    } else {
        fileIcon.removeClass().addClass('fas fa-file');
    }
    
    // Show preview
    preview.removeClass('hidden');
    
    // Update placeholder text
    $('#chat-input').attr('placeholder', 'Add a message about this document (optional)...');
}

window.removeChatAttachment = function() {
    chatAttachedFile = null;
    $('#chat-file-preview').addClass('hidden');
    $('#chat-file-input').val('');
    $('#chat-input').attr('placeholder', 'Type your question or attach a document...');
};

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Add fade-in animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .animate-fade-in {
        animation: fade-in 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// ==========================================
// Chat Modal Functions
// ==========================================

// Open Chat Modal
function openChatModal() {
    document.getElementById('chat-modal').classList.remove('hidden');
    document.getElementById('chat-input').focus();
}

// Close chat modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const chatModal = document.getElementById('chat-modal');
        if (!chatModal.classList.contains('hidden')) {
            closeChatModal();
        }
    }
});
