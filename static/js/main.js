// Main JavaScript for Material Delivery Dashboard

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
