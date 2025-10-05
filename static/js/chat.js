// Chat Interface JavaScript

$(document).ready(function() {
    const chatFloatBtn = $('#chat-float-btn');
    const chatModal = $('#chat-modal');
    const chatForm = $('#chat-form');
    const chatInput = $('#chat-input');
    const chatMessages = $('#chat-messages');
    
    // New simplified chat interface
    const chatInterface = $('#chat-interface');
    const chatToggleBtn = $('#chat-toggle-btn');
    
    // Toggle chat modal
    chatFloatBtn.on('click', function() {
        chatModal.removeClass('hidden');
        chatInput.focus();
    });
    
    // Close chat modal
    window.closeChatModal = function() {
        chatModal.addClass('hidden');
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
    });
    
    // Handle suggested queries
    window.sendSuggestedQuery = function(query) {
        chatInput.val(query);
        chatForm.submit();
    };
    
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

// Toggle simplified chat interface
window.toggleChat = function() {
    const chatInterface = $('#chat-interface');
    const chatToggleBtn = $('#chat-toggle-btn');
    
    if (chatInterface.hasClass('hidden')) {
        chatInterface.removeClass('hidden');
        chatToggleBtn.find('i').removeClass('fa-comments').addClass('fa-times');
        $('#chat-input').focus();
    } else {
        chatInterface.addClass('hidden');
        chatToggleBtn.find('i').removeClass('fa-times').addClass('fa-comments');
    }
};

// Send chat message from simplified interface
window.sendChatMessage = function() {
    const input = $('#chat-interface #chat-input');
    const query = input.val().trim();
    
    if (!query) return;
    
    // Add user message
    addSimplifiedMessage(query, 'user');
    input.val('');
    
    // Show typing
    addSimplifiedTyping();
    
    // Send to server
    $.ajax({
        url: '/api/chat',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ query: query }),
        success: function(response) {
            removeSimplifiedTyping();
            addSimplifiedMessage(response.answer, 'ai', response.data);
        },
        error: function(err) {
            removeSimplifiedTyping();
            addSimplifiedMessage('Sorry, I encountered an error.', 'ai');
            console.error('Chat error:', err);
        }
    });
};

// Quick query helper
window.quickQuery = function(query) {
    $('#chat-interface #chat-input').val(query);
    sendChatMessage();
};

// Add message to simplified interface
function addSimplifiedMessage(text, sender, data = null) {
    const chatMessages = $('#chat-interface #chat-messages');
    const isUser = sender === 'user';
    
    let html = '';
    if (isUser) {
        html = `
            <div class="flex items-start space-x-2 justify-end">
                <div class="bg-gradient-to-r from-pkp-green to-pkp-gold text-white rounded-lg p-3 shadow-sm max-w-[280px]">
                    <p class="text-sm">${escapeHtml(text)}</p>
                </div>
                <div class="bg-gray-300 text-gray-600 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-user text-sm"></i>
                </div>
            </div>
        `;
    } else {
        html = `
            <div class="flex items-start space-x-2">
                <div class="bg-pkp-green text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-sm"></i>
                </div>
                <div class="bg-white rounded-lg p-3 shadow-sm max-w-[280px]">
                    <p class="text-sm text-gray-800">${escapeHtml(text)}</p>
                    ${data ? formatSimplifiedData(data) : ''}
                </div>
            </div>
        `;
    }
    
    chatMessages.append(html);
    chatMessages.scrollTop(chatMessages[0].scrollHeight);
}

function addSimplifiedTyping() {
    const chatMessages = $('#chat-interface #chat-messages');
    const indicator = `
        <div id="simple-typing" class="flex items-start space-x-2">
            <div class="bg-pkp-green text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-sm"></i>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-pkp-green rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-pkp-green rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-pkp-green rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
            </div>
        </div>
    `;
    chatMessages.append(indicator);
    chatMessages.scrollTop(chatMessages[0].scrollHeight);
}

function removeSimplifiedTyping() {
    $('#simple-typing').remove();
}

function formatSimplifiedData(data) {
    if (Array.isArray(data) && data.length > 0) {
        let html = '<div class="mt-2 text-xs space-y-1">';
        data.slice(0, 3).forEach(item => {
            html += `<div class="bg-gray-50 p-2 rounded border border-gray-200">`;
            for (const [key, value] of Object.entries(item)) {
                html += `<div><span class="text-gray-600">${escapeHtml(key)}:</span> <span class="font-semibold">${escapeHtml(String(value))}</span></div>`;
            }
            html += '</div>';
        });
        if (data.length > 3) {
            html += `<p class="text-gray-500 text-center">+${data.length - 3} more</p>`;
        }
        html += '</div>';
        return html;
    } else if (typeof data === 'object' && Object.keys(data).length > 0) {
        let html = '<div class="mt-2 text-xs bg-gray-50 p-2 rounded border border-gray-200">';
        for (const [key, value] of Object.entries(data)) {
            html += `<div class="flex justify-between"><span class="text-gray-600">${escapeHtml(key)}:</span> <span class="font-semibold">${escapeHtml(String(value))}</span></div>`;
        }
        html += '</div>';
        return html;
    }
    return '';
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
