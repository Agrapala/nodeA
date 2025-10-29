#!/usr/bin/env python3
"""
Vercel-compatible API entry point
Simplified version for Vercel deployment
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

# Create Flask app
app = Flask(__name__)
app.secret_key = 'nodeA_secret_key_2024'

# Global variables
training_status = "idle"
receiver_status = "stopped"
training_logs = []
receiver_logs = []

def get_system_info():
    """Get system information"""
    info = {
        "node_id": "nodeA",
        "timestamp": datetime.now().isoformat(),
        "pocl_server_status": "Disconnected",
        "training_status": training_status,
        "receiver_status": receiver_status,
        "deployment": "Vercel",
        "limitations": [
            "No file system access (except /tmp)",
            "No subprocess execution", 
            "No persistent storage",
            "Limited to 10MB uploads"
        ],
        "model_files": []
    }
    return info

@app.route('/')
def index():
    """Main dashboard - serve HTML page"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'simple.html'), 'r') as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        # Fallback to JSON if HTML file not found
        system_info = get_system_info()
        return jsonify({
            "message": "NodeA Web Interface - Vercel Deployment",
            "status": "running",
            "info": system_info,
            "note": "This is a simplified version for Vercel. Full functionality requires local deployment.",
            "error": f"HTML template not found: {str(e)}"
        })

@app.route('/training')
def training():
    """Training management page"""
    return jsonify({
        "page": "training",
        "status": training_status,
        "message": "Training management (simulated on Vercel)"
    })

@app.route('/models')
def models():
    """Model management page"""
    return jsonify({
        "page": "models", 
        "message": "Model management (simulated on Vercel)"
    })

@app.route('/transfer')
def transfer():
    """File transfer management page"""
    return jsonify({
        "page": "transfer",
        "message": "File transfer management (simulated on Vercel)"
    })

@app.route('/logs')
def logs():
    """Logs viewing page"""
    return jsonify({
        "page": "logs",
        "training_logs": training_logs,
        "receiver_logs": receiver_logs
    })

@app.route('/settings')
def settings():
    """Settings page"""
    return jsonify({
        "page": "settings",
        "message": "Settings page (simulated on Vercel)"
    })

# API Endpoints

@app.route('/api/start_training', methods=['POST'])
def start_training():
    """Start training process - Vercel compatible version"""
    global training_status
    
    if training_status == "running":
        return jsonify({"success": False, "message": "Training already running"})
    
    training_status = "running"
    training_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training started (simulated)")
    training_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Note: Actual training requires local deployment")
    
    return jsonify({"success": True, "message": "Training started (simulated - Vercel limitation)"})

@app.route('/api/stop_training', methods=['POST'])
def stop_training():
    """Stop training process"""
    global training_status
    
    if training_status == "running":
        training_status = "stopped"
        training_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training stopped")
        return jsonify({"success": True, "message": "Training stopped"})
    else:
        return jsonify({"success": False, "message": "No training process running"})

@app.route('/api/start_receiver', methods=['POST'])
def start_receiver():
    """Start global model receiver - Vercel compatible version"""
    global receiver_status
    
    if receiver_status == "running":
        return jsonify({"success": False, "message": "Receiver already running"})
    
    receiver_status = "running"
    receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Receiver started (simulated)")
    receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Note: Actual receiver requires local deployment")
    
    return jsonify({"success": True, "message": "Global model receiver started (simulated - Vercel limitation)"})

@app.route('/api/stop_receiver', methods=['POST'])
def stop_receiver():
    """Stop global model receiver"""
    global receiver_status
    
    if receiver_status == "running":
        receiver_status = "stopped"
        receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Receiver stopped")
        return jsonify({"success": True, "message": "Receiver stopped"})
    else:
        return jsonify({"success": False, "message": "No receiver process running"})

@app.route('/api/send_model', methods=['POST'])
def send_model():
    """Send model to PoCL server - Vercel compatible version"""
    return jsonify({"success": True, "message": "Model send simulated (Vercel limitation - use local deployment for actual transfer)"})

@app.route('/api/system_info')
def api_system_info():
    """Get system information API"""
    return jsonify(get_system_info())

@app.route('/api/upload_model', methods=['POST'])
def upload_model():
    """Upload model file - Vercel compatible version"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"})
    
    # Simulate file upload
    return jsonify({"success": True, "message": f"File {file.filename} upload simulated (Vercel limitation)"})

@app.route('/api/test_connection')
def test_connection():
    """Test connection to PoCL server"""
    return jsonify({
        "success": True,
        "connected": False,
        "message": "Connection test simulated (Vercel limitation)"
    })

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    """Clear logs"""
    global training_logs, receiver_logs
    
    try:
        data = request.get_json() or {}
        log_type = data.get('type', 'all')
        
        if log_type == 'training' or log_type == 'all':
            training_logs.clear()
        if log_type == 'receiver' or log_type == 'all':
            receiver_logs.clear()
        
        return jsonify({"success": True, "message": "Logs cleared"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error clearing logs: {str(e)}"})

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "deployment": "Vercel"
    })

# This is the main entry point for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)