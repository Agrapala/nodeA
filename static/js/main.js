/**
 * NodeA Federated Learning Web Interface - Main JavaScript
 * Handles all interactive features and API communications
 */

// Global variables
let autoRefreshIntervals = {};
let currentTimeInterval;

// Initialize the application
$(document).ready(function() {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 Initializing NodeA Web Interface');
    
    // Start current time updater
    updateCurrentTime();
    currentTimeInterval = setInterval(updateCurrentTime, 1000);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize auto-refresh for dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        startAutoRefresh('dashboard', 5000);
    }
    
    // Initialize file upload drag and drop
    initializeFileUpload();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    console.log('✅ NodeA Web Interface initialized');
}

// Time and Status Updates
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString();
    $('#current-time').text(timeString);
}

function updateStatusIndicator() {
    $.get('/api/system_info')
        .done(function(data) {
            const indicator = $('#status-indicator');
            const statusText = $('#status-text');
            
            if (data.pocl_server_status === 'Connected') {
                indicator.removeClass('text-danger').addClass('text-success');
                statusText.text('Connected');
            } else {
                indicator.removeClass('text-success').addClass('text-danger');
                statusText.text('Disconnected');
            }
        })
        .fail(function() {
            $('#status-indicator').removeClass('text-success').addClass('text-danger');
            $('#status-text').text('Error');
        });
}

// Auto-refresh Management
function startAutoRefresh(type, interval) {
    if (autoRefreshIntervals[type]) {
        clearInterval(autoRefreshIntervals[type]);
    }
    
    autoRefreshIntervals[type] = setInterval(function() {
        switch(type) {
            case 'dashboard':
                updateDashboard();
                break;
            case 'training':
                updateTrainingStatus();
                break;
            case 'transfer':
                updateTransferStatus();
                break;
            case 'logs':
                refreshAllLogs();
                break;
        }
    }, interval);
}

function stopAutoRefresh(type) {
    if (autoRefreshIntervals[type]) {
        clearInterval(autoRefreshIntervals[type]);
        delete autoRefreshIntervals[type];
    }
}

// Dashboard Functions
function updateDashboard() {
    $.get('/api/system_info')
        .done(function(data) {
            updateDashboardCards(data);
        })
        .fail(function() {
            console.error('Failed to update dashboard');
        });
}

function updateDashboardCards(data) {
    // Update status cards
    $('#pocl-status').text(data.pocl_server_status);
    $('#training-status').text(capitalizeFirst(data.training_status));
    $('#receiver-status').text(capitalizeFirst(data.receiver_status));
    
    // Update status indicator
    updateStatusIndicator();
    
    // Update model files table if present
    if ($('#model-files-table').length) {
        updateModelFilesTable(data.model_files);
    }
}

function updateModelFilesTable(modelFiles) {
    const tbody = $('#model-files-table tbody');
    
    if (!modelFiles || modelFiles.length === 0) {
        tbody.html('<tr><td colspan="5" class="text-center text-muted">No model files found</td></tr>');
        return;
    }
    
    let html = '';
    modelFiles.forEach(function(file) {
        html += `
            <tr>
                <td><i class="fas fa-file-code me-2"></i>${file.name}</td>
                <td>${formatFileSize(file.size)}</td>
                <td>${formatDateTime(file.modified)}</td>
                <td><code class="small">${file.hash.substring(0, 16)}...</code></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="downloadModel('${file.name}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteModel('${file.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.html(html);
}

// Training Functions
function updateTrainingStatus() {
    $.get('/api/system_info')
        .done(function(data) {
            updateTrainingUI(data.training_status);
        });
}

function updateTrainingUI(status) {
    const statusDisplay = $('#training-status-display');
    const startBtn = $('#start-training-btn');
    const stopBtn = $('#stop-training-btn');
    
    if (statusDisplay.length) {
        statusDisplay.text(capitalizeFirst(status));
    }
    
    if (startBtn.length && stopBtn.length) {
        if (status === 'running') {
            startBtn.prop('disabled', true);
            stopBtn.prop('disabled', false);
        } else {
            startBtn.prop('disabled', false);
            stopBtn.prop('disabled', true);
        }
    }
}

// Transfer Functions
function updateTransferStatus() {
    $.get('/api/system_info')
        .done(function(data) {
            updateTransferUI(data);
        });
}

function updateTransferUI(data) {
    $('#connection-status').text(data.pocl_server_status);
    $('#receiver-status').text(capitalizeFirst(data.receiver_status));
    
    // Update receiver button states
    const startBtn = $('#start-receiver-btn');
    const stopBtn = $('#stop-receiver-btn');
    const toggleBtn = $('#receiver-toggle-btn');
    
    if (data.receiver_status === 'running') {
        if (startBtn.length) startBtn.prop('disabled', true);
        if (stopBtn.length) stopBtn.prop('disabled', false);
        if (toggleBtn.length) {
            toggleBtn.html('<i class="fas fa-stop me-2"></i>Stop Receiver');
            toggleBtn.removeClass('btn-outline-success').addClass('btn-outline-danger');
        }
    } else {
        if (startBtn.length) startBtn.prop('disabled', false);
        if (stopBtn.length) stopBtn.prop('disabled', true);
        if (toggleBtn.length) {
            toggleBtn.html('<i class="fas fa-play me-2"></i>Start Receiver');
            toggleBtn.removeClass('btn-outline-danger').addClass('btn-outline-success');
        }
    }
}

// File Upload Functions
function initializeFileUpload() {
    // Drag and drop functionality
    $(document).on('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
    });
    
    $(document).on('dragenter', function(e) {
        e.preventDefault();
        e.stopPropagation();
    });
    
    $(document).on('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

function handleFileUpload(file) {
    if (!file) return;
    
    const allowedTypes = ['application/octet-stream', 'application/json'];
    const allowedExtensions = ['.h5', '.json'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showAlert('warning', 'Please upload .h5 or .json files only');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showAlert('info', `Uploading ${file.name}...`);
    
    $.ajax({
        url: '/api/upload_model',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            if (data.success) {
                showAlert('success', data.message);
                if (typeof refreshModels === 'function') {
                    refreshModels();
                }
            } else {
                showAlert('danger', data.message);
            }
        },
        error: function() {
            showAlert('danger', 'Upload failed');
        }
    });
}

// Log Functions
function refreshAllLogs() {
    refreshLogs('training');
    refreshLogs('receiver');
    refreshLogs('system');
}

function refreshLogs(type) {
    const contentId = type + '-logs-content';
    const $content = $('#' + contentId);
    
    if (!$content.length) return;
    
    $content.html(`
        <div class="text-center text-muted">
            <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
            <p>Refreshing logs...</p>
        </div>
    `);
    
    // Simulate log refresh (in real implementation, fetch from server)
    setTimeout(function() {
        $content.html(`
            <div class="text-center text-muted">
                <i class="fas fa-list fa-2x mb-2"></i>
                <p>No ${type} logs available</p>
            </div>
        `);
    }, 1000);
}

// Utility Functions
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
}

function showAlert(type, message, duration = 5000) {
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container-fluid').prepend(alertHtml);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(function() {
            $(`#${alertId}`).alert('close');
        }, duration);
    }
}

function showConfirm(title, message, callback) {
    if (confirm(`${title}\n\n${message}`)) {
        callback();
    }
}

function showLoading(element, text = 'Loading...') {
    const $element = $(element);
    $element.prop('disabled', true);
    $element.data('original-text', $element.html());
    $element.html(`<i class="fas fa-spinner fa-spin me-2"></i>${text}`);
}

function hideLoading(element) {
    const $element = $(element);
    $element.prop('disabled', false);
    $element.html($element.data('original-text'));
}

// API Functions
function makeApiCall(url, method = 'GET', data = null) {
    return $.ajax({
        url: url,
        method: method,
        data: data,
        contentType: 'application/json',
        dataType: 'json'
    });
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    $(document).keydown(function(e) {
        // Ctrl/Cmd + R: Refresh current page
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 82) {
            e.preventDefault();
            location.reload();
        }
        
        // Ctrl/Cmd + T: Test connection
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 84) {
            e.preventDefault();
            if (typeof testConnection === 'function') {
                testConnection();
            }
        }
        
        // Ctrl/Cmd + S: Start training
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 83) {
            e.preventDefault();
            if (typeof startTraining === 'function') {
                startTraining();
            }
        }
    });
}

// Tooltip Initialization
function initializeTooltips() {
    $('[data-bs-toggle="tooltip"]').tooltip();
}

// Model Management Functions
function downloadModel(filename) {
    window.open(`/api/download_model/${filename}`, '_blank');
}

function deleteModel(filename) {
    showConfirm(
        'Delete Model',
        `Are you sure you want to delete ${filename}?`,
        function() {
            $.ajax({
                url: `/api/delete_model/${filename}`,
                type: 'DELETE',
                success: function(data) {
                    if (data.success) {
                        showAlert('success', data.message);
                        if (typeof refreshModels === 'function') {
                            refreshModels();
                        } else {
                            location.reload();
                        }
                    } else {
                        showAlert('danger', data.message);
                    }
                },
                error: function() {
                    showAlert('danger', 'Failed to delete model');
                }
            });
        }
    );
}

function sendModel(filename) {
    showLoading('#send-model-btn', 'Sending...');
    
    $.post('/api/send_model')
        .done(function(data) {
            hideLoading('#send-model-btn');
            if (data.success) {
                showAlert('success', data.message);
            } else {
                showAlert('danger', data.message);
            }
        })
        .fail(function() {
            hideLoading('#send-model-btn');
            showAlert('danger', 'Failed to send model');
        });
}

// Connection Functions
function testConnection() {
    showLoading('#test-connection-btn', 'Testing...');
    
    $.get('/api/test_connection')
        .done(function(data) {
            hideLoading('#test-connection-btn');
            if (data.success) {
                showAlert(data.connected ? 'success' : 'warning', data.message);
            } else {
                showAlert('danger', 'Connection test failed');
            }
        })
        .fail(function() {
            hideLoading('#test-connection-btn');
            showAlert('danger', 'Connection test failed');
        });
}

// Training Functions
function startTraining() {
    showLoading('#start-training-btn', 'Starting...');
    
    $.post('/api/start_training')
        .done(function(data) {
            hideLoading('#start-training-btn');
            if (data.success) {
                showAlert('success', data.message);
                if (typeof updateTrainingStatus === 'function') {
                    updateTrainingStatus();
                }
            } else {
                showAlert('danger', data.message);
            }
        })
        .fail(function() {
            hideLoading('#start-training-btn');
            showAlert('danger', 'Failed to start training');
        });
}

function stopTraining() {
    showLoading('#stop-training-btn', 'Stopping...');
    
    $.post('/api/stop_training')
        .done(function(data) {
            hideLoading('#stop-training-btn');
            if (data.success) {
                showAlert('warning', data.message);
                if (typeof updateTrainingStatus === 'function') {
                    updateTrainingStatus();
                }
            } else {
                showAlert('danger', data.message);
            }
        })
        .fail(function() {
            hideLoading('#stop-training-btn');
            showAlert('danger', 'Failed to stop training');
        });
}

// Receiver Functions
function startReceiver() {
    showLoading('#start-receiver-btn', 'Starting...');
    
    $.post('/api/start_receiver')
        .done(function(data) {
            hideLoading('#start-receiver-btn');
            if (data.success) {
                showAlert('success', data.message);
                if (typeof updateTransferStatus === 'function') {
                    updateTransferStatus();
                }
            } else {
                showAlert('danger', data.message);
            }
        })
        .fail(function() {
            hideLoading('#start-receiver-btn');
            showAlert('danger', 'Failed to start receiver');
        });
}

function stopReceiver() {
    showLoading('#stop-receiver-btn', 'Stopping...');
    
    $.post('/api/stop_receiver')
        .done(function(data) {
            hideLoading('#stop-receiver-btn');
            if (data.success) {
                showAlert('warning', data.message);
                if (typeof updateTransferStatus === 'function') {
                    updateTransferStatus();
                }
            } else {
                showAlert('danger', data.message);
            }
        })
        .fail(function() {
            hideLoading('#stop-receiver-btn');
            showAlert('danger', 'Failed to stop receiver');
        });
}

// Cleanup on page unload
$(window).on('beforeunload', function() {
    // Clear all intervals
    Object.values(autoRefreshIntervals).forEach(function(interval) {
        clearInterval(interval);
    });
    
    if (currentTimeInterval) {
        clearInterval(currentTimeInterval);
    }
});

// Export functions for global access
window.NodeA = {
    showAlert: showAlert,
    showConfirm: showConfirm,
    showLoading: showLoading,
    hideLoading: hideLoading,
    formatFileSize: formatFileSize,
    formatDateTime: formatDateTime,
    makeApiCall: makeApiCall,
    startAutoRefresh: startAutoRefresh,
    stopAutoRefresh: stopAutoRefresh
};
