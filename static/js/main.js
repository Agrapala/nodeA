// Main JavaScript for NodeA Web Interface

// Global variables
let receiverStatus = '{{ info.receiver_status }}';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('NodeA Web Interface loaded');
    
    // Update receiver status if on transfer page
    if (document.getElementById('receiverStatusBadge')) {
        updateReceiverStatus();
    }
    
    // Auto-refresh system info every 30 seconds
    if (window.location.pathname === '/') {
        setInterval(refreshSystemInfo, 30000);
    }
});

// Update receiver status display
function updateReceiverStatus() {
    const statusBadge = document.getElementById('receiverStatusBadge');
    const startBtn = document.getElementById('startReceiverBtn');
    const stopBtn = document.getElementById('stopReceiverBtn');
    
    if (statusBadge) {
        if (receiverStatus === 'running') {
            statusBadge.textContent = 'running';
            statusBadge.className = 'badge bg-success';
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
        } else {
            statusBadge.textContent = 'stopped';
            statusBadge.className = 'badge bg-secondary';
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
        }
    }
}

// Refresh system information
function refreshSystemInfo() {
    fetch('/api/system_info')
        .then(response => response.json())
        .then(data => {
            // Update receiver status
            if (data.receiver_status !== receiverStatus) {
                receiverStatus = data.receiver_status;
                updateReceiverStatus();
            }
            
            // Update model files count if element exists
            const modelCountElement = document.querySelector('.card-text');
            if (modelCountElement && data.model_files) {
                modelCountElement.textContent = data.model_files.length + ' files';
            }
        })
        .catch(error => {
            console.error('Error refreshing system info:', error);
        });
}

// Show loading state for buttons
function showLoading(button, text = 'Loading...') {
    const originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> ${text}`;
    button.disabled = true;
    
    return function hideLoading() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                     type === 'success' ? 'alert-success' : 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Download file
function downloadFile(filename) {
    window.open(`/api/download_model/${filename}`, '_blank');
}

// Confirm action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Handle API errors
function handleApiError(error, defaultMessage = 'An error occurred') {
    console.error('API Error:', error);
    const message = error.message || defaultMessage;
    showNotification(message, 'error');
}

// Export functions for use in templates
window.NodeA = {
    showLoading,
    showNotification,
    formatFileSize,
    formatTimestamp,
    copyToClipboard,
    downloadFile,
    confirmAction,
    handleApiError
};
