// Chat Interface JavaScript

$(document).ready(function() {
    const chatBtn = $('#chat-btn');
    const chatPanel = $('#chat-panel');
    const closeChat = $('#close-chat');
    const chatForm = $('#chat-form');
    const chatInput = $('#chat-input');
    const chatMessages = $('#chat-messages');
    
    // Toggle chat panel
    chatBtn.on('click', function() {
        chatPanel.toggleClass('hidden');
        if (!chatPanel.hasClass('hidden')) {
            chatInput.focus();
        }
    });
    
    closeChat.on('click', function() {
        chatPanel.addClass('hidden');
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
            }
        });
    });
    
    function addMessage(text, sender, data = null) {
        const isUser = sender === 'user';
        const messageClass = isUser ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-200 text-gray-800';
        const alignment = isUser ? 'justify-end' : 'justify-start';
        
        let messageHtml = `
            <div class="flex ${alignment}">
                <div class="${messageClass} rounded-lg px-4 py-2 max-w-[80%] break-words">
                    ${escapeHtml(text)}
                </div>
            </div>
        `;
        
        // Add data table if available
        if (!isUser && data && typeof data === 'object') {
            if (Array.isArray(data) && data.length > 0) {
                messageHtml += formatDataTable(data);
            } else if (Object.keys(data).length > 0) {
                messageHtml += formatDataObject(data);
            }
        }
        
        chatMessages.append(messageHtml);
        scrollToBottom();
    }
    
    function formatDataTable(dataArray) {
        let html = '<div class="mt-2 bg-white rounded-lg p-3 text-sm max-w-full overflow-x-auto">';
        html += '<table class="min-w-full text-left">';
        
        // Headers
        const keys = Object.keys(dataArray[0]);
        html += '<thead class="border-b"><tr>';
        keys.forEach(key => {
            html += `<th class="px-2 py-1 font-semibold text-gray-700">${escapeHtml(key)}</th>`;
        });
        html += '</tr></thead>';
        
        // Rows
        html += '<tbody>';
        dataArray.forEach(row => {
            html += '<tr class="border-b">';
            keys.forEach(key => {
                html += `<td class="px-2 py-1 text-gray-600">${escapeHtml(String(row[key] || 'N/A'))}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table></div>';
        
        return html;
    }
    
    function formatDataObject(dataObj) {
        let html = '<div class="mt-2 bg-white rounded-lg p-3 text-sm">';
        html += '<dl class="space-y-1">';
        
        for (const [key, value] of Object.entries(dataObj)) {
            html += `
                <div class="flex justify-between">
                    <dt class="font-semibold text-gray-700">${escapeHtml(key)}:</dt>
                    <dd class="text-gray-600">${escapeHtml(String(value))}</dd>
                </div>
            `;
        }
        
        html += '</dl></div>';
        return html;
    }
    
    function addTypingIndicator() {
        const indicator = `
            <div id="typing-indicator" class="flex justify-start">
                <div class="bg-gray-200 rounded-lg px-4 py-2">
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
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
    
    // Sample queries for quick access
    window.askQuestion = function(question) {
        chatInput.val(question);
        chatPanel.removeClass('hidden');
        chatForm.submit();
    };
});
