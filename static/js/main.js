// Main JavaScript for Material Delivery Dashboard

// Sidebar Drawer Toggle (Works on all screen sizes)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar-menu');
    const overlay = document.getElementById('sidebar-overlay');
    const btn = document.getElementById('sidebar-toggle-btn');
    
    if (sidebar.classList.contains('translate-x-full')) {
        // Open sidebar
        sidebar.classList.remove('translate-x-full');
        sidebar.classList.add('translate-x-0');
        overlay.classList.remove('hidden');
        // Animate overlay fade in
        setTimeout(() => {
            overlay.classList.add('opacity-100');
        }, 10);
        // Disable body scroll
        document.body.style.overflow = 'hidden';
    } else {
        // Close sidebar
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('translate-x-full');
        overlay.classList.remove('opacity-100');
        setTimeout(() => {
            overlay.classList.add('hidden');
        }, 300);
        // Re-enable body scroll
        document.body.style.overflow = '';
    }
}

// Close sidebar when pressing Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const sidebar = document.getElementById('sidebar-menu');
        if (sidebar && !sidebar.classList.contains('translate-x-full')) {
            toggleSidebar();
        }
    }
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuBtn = document.getElementById('mobile-menu-btn');
    
    if (mobileMenu && menuBtn && !mobileMenu.classList.contains('hidden')) {
        if (!mobileMenu.contains(event.target) && !menuBtn.contains(event.target)) {
            toggleMobileMenu();
        }
    }
});

// Close mobile menu when window is resized to desktop size
window.addEventListener('resize', function() {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuBtn = document.getElementById('mobile-menu-btn');
    
    if (window.innerWidth >= 1024 && mobileMenu && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        const icon = menuBtn.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
});

// Global functions
function showLoading() {
    $('#loading-overlay').removeClass('hidden');
}

function hideLoading() {
    $('#loading-overlay').addClass('hidden');
}

function showToast(message, type = 'success') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const toast = $(`
        <div class="fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
            ${message}
        </div>
    `);
    
    $('body').append(toast);
    
    setTimeout(() => {
        toast.fadeOut(400, function() {
            $(this).remove();
        });
    }, 3000);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatCurrency(amount, currency = 'AED') {
    return `${currency} ${parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

// Check for pending AI suggestions
function checkAISuggestions() {
    $.ajax({
        url: '/api/ai-suggestions/pending',
        method: 'GET',
        success: function(data) {
            if (data.length > 0) {
                $('#ai-badge').removeClass('hidden').text(data.length);
            } else {
                $('#ai-badge').addClass('hidden');
            }
        }
    });
}

// Initialize common features
$(document).ready(function() {
    // Check AI suggestions on page load
    checkAISuggestions();
    
    // Check periodically
    setInterval(checkAISuggestions, 60000); // Every minute
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    $('nav a').each(function() {
        const href = $(this).attr('href');
        if (currentPath === href || (currentPath.startsWith(href) && href !== '/')) {
            $(this).addClass('font-bold border-b-2 border-white');
        }
    });

    // Check AI status immediately on page load
    checkGlobalAIStatus();
    
    // Check AI status every 30 seconds
    setInterval(checkGlobalAIStatus, 30000);
});

// Export for use in other scripts
window.dashboardUtils = {
    showLoading,
    hideLoading,
    showToast,
    formatDate,
    formatCurrency,
    checkAISuggestions
};

// Sprint 2: Global AI Status Badge System
window.aiStatusBadge = {
    show: function(title, message, type = 'processing') {
        const badge = $('#ai-status-badge');
        const icon = $('#ai-status-icon');
        const statusTitle = $('#ai-status-title');
        const statusMessage = $('#ai-status-message');
        
        // Set icon and colors based on type
        const configs = {
            processing: {
                icon: 'fa-robot fa-spin',
                color: 'text-blue-500',
                border: 'border-blue-300'
            },
            uploading: {
                icon: 'fa-cloud-upload-alt fa-bounce',
                color: 'text-blue-500',
                border: 'border-blue-300'
            },
            analyzing: {
                icon: 'fa-brain fa-pulse',
                color: 'text-purple-500',
                border: 'border-purple-300'
            },
            validating: {
                icon: 'fa-check-double fa-fade',
                color: 'text-yellow-500',
                border: 'border-yellow-300'
            },
            success: {
                icon: 'fa-check-circle',
                color: 'text-green-500',
                border: 'border-green-300'
            },
            error: {
                icon: 'fa-exclamation-circle',
                color: 'text-red-500',
                border: 'border-red-300'
            },
            warning: {
                icon: 'fa-exclamation-triangle',
                color: 'text-orange-500',
                border: 'border-orange-300'
            }
        };
        
        const config = configs[type] || configs.processing;
        
        icon.removeClass().addClass(`fas ${config.icon} ${config.color}`);
        badge.removeClass('border-blue-300 border-purple-300 border-yellow-300 border-green-300 border-red-300 border-orange-300')
             .addClass(config.border);
        statusTitle.text(title);
        statusMessage.html(message);
        
        badge.removeClass('hidden');
    },
    
    updateProgress: function(percentage, details = '') {
        $('#ai-status-progress').removeClass('hidden');
        $('#ai-progress-bar').css('width', `${percentage}%`);
        
        if (details) {
            $('#ai-status-details').removeClass('hidden').text(details);
        }
    },
    
    hideProgress: function() {
        $('#ai-status-progress').addClass('hidden');
        $('#ai-status-details').addClass('hidden');
    },
    
    hide: function() {
        $('#ai-status-badge').addClass('hidden');
    },
    
    autoClose: function(delay = 3000) {
        setTimeout(() => {
            this.hide();
        }, delay);
    }
};

function closeAIStatus() {
    window.aiStatusBadge.hide();
}

// Global AI Status Checker (works on all pages)
function checkGlobalAIStatus() {
    $.ajax({
        url: '/api/dashboard/n8n-status',
        method: 'GET',
        timeout: 5000,
        success: function(data) {
            updateGlobalAIIndicator(data);
        },
        error: function() {
            // If check fails, show offline
            updateGlobalAIIndicator({
                n8n_live: false,
                ai_features_available: false,
                mode: 'manual',
                details: { message: 'Unable to check status' }
            });
        }
    });
}

function updateGlobalAIIndicator(status) {
    const light = $('#global-status-light');
    const ring = $('#global-status-ring');
    const text = $('#global-status-text');
    const icon = $('#global-status-icon');
    
    // Tooltip elements
    const tooltipMessage = $('#tooltip-message');
    const tooltipIcon = $('#tooltip-icon');
    const tooltipN8n = $('#tooltip-n8n');
    const tooltipAIAPI = $('#tooltip-ai-api');
    
    if (status.ai_features_available) {
        // GREEN - AI Features Online
        light.removeClass('bg-gray-400 bg-red-500 bg-yellow-500')
             .addClass('bg-green-500');
        ring.removeClass('bg-gray-400 bg-red-500 bg-yellow-500')
            .addClass('bg-green-500 animate-ping');
        text.text('Online').removeClass('text-white text-opacity-70').addClass('text-white');
        icon.removeClass('text-gray-400 text-red-400 text-yellow-400').addClass('text-white');
        
        // Update tooltip
        tooltipMessage.text('✓ All AI-powered automation features are operational');
        tooltipIcon.removeClass('text-red-500 text-yellow-500 text-gray-500')
                   .addClass('text-green-500');
        tooltipN8n.text('Online ✓').removeClass('text-red-600 text-yellow-600 text-gray-600')
                  .addClass('text-green-600');
        tooltipAIAPI.text('Configured ✓')
                    .removeClass('text-red-600 text-yellow-600 text-gray-600')
                    .addClass('text-green-600');
        
    } else if (status.n8n_live && !status.ai_features_available) {
        // YELLOW - n8n online but AI not configured
        light.removeClass('bg-gray-400 bg-red-500 bg-green-500')
             .addClass('bg-yellow-500');
        ring.removeClass('bg-gray-400 bg-red-500 bg-green-500 animate-ping')
            .addClass('bg-yellow-500');
        text.text('Partial').removeClass('text-white text-opacity-70').addClass('text-white');
        icon.removeClass('text-gray-400 text-red-400 text-green-400').addClass('text-yellow-300');
        
        // Update tooltip
        tooltipMessage.text('⚠ Automation workflows online, AI API needs configuration');
        tooltipIcon.removeClass('text-green-500 text-red-500 text-gray-500')
                   .addClass('text-yellow-500');
        tooltipN8n.text('Online ✓').removeClass('text-red-600 text-green-600 text-gray-600')
                  .addClass('text-yellow-600');
        tooltipAIAPI.text('Not configured')
                    .removeClass('text-red-600 text-green-600 text-gray-600')
                    .addClass('text-yellow-600');
        
    } else {
        // RED - Manual Mode (n8n offline or not configured)
        light.removeClass('bg-gray-400 bg-green-500 bg-yellow-500')
             .addClass('bg-red-500');
        ring.removeClass('bg-gray-400 bg-green-500 bg-yellow-500 animate-ping')
            .addClass('bg-red-500');
        text.text('Offline').removeClass('text-white text-opacity-70').addClass('text-white');
        icon.removeClass('text-gray-400 text-yellow-300 text-green-400').addClass('text-red-400');
        
        // Update tooltip
        tooltipMessage.text('✗ AI automation unavailable - Manual mode only');
        tooltipIcon.removeClass('text-green-500 text-yellow-500 text-gray-500')
                   .addClass('text-red-500');
        tooltipN8n.text('Offline ✗').removeClass('text-green-600 text-yellow-600 text-gray-600')
                  .addClass('text-red-600');
        tooltipAIAPI.text('N/A')
                    .removeClass('text-green-600 text-yellow-600 text-gray-600')
                    .addClass('text-red-600');
    }
}
