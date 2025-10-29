#!/usr/bin/env python3
"""
Vercel-compatible API entry point
This is a simplified version for Vercel deployment
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import hashlib

app = Flask(__name__)
app.secret_key = 'nodeA_secret_key_2024'

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'  # Vercel only allows writing to /tmp
ALLOWED_EXTENSIONS = {'h5', 'json', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size for Vercel

# Global variables for managing processes
training_status = "idle"
receiver_status = "stopped"
training_logs = []
receiver_logs = []

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"Error: {e}"

def check_pocl_server_status():
    """Check if PoCL server is reachable"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("100.64.0.1", 8888))  # Update with actual PoCL IP
        sock.close()
        return result == 0
    except Exception:
        return False

def get_system_info():
    """Get system information"""
    info = {
        "node_id": "nodeA",
        "timestamp": datetime.now().isoformat(),
        "pocl_server_status": "Connected" if check_pocl_server_status() else "Disconnected",
        "training_status": training_status,
        "receiver_status": receiver_status,
        "deployment": "Vercel",
        "limitations": [
            "No file system access (except /tmp)",
            "No subprocess execution",
            "No persistent storage",
            "Limited to 10MB uploads"
        ]
    }
    
    # Check for model files in /tmp (Vercel's writable directory)
    model_files = []
    tmp_dir = '/tmp'
    if os.path.exists(tmp_dir):
        for filename in os.listdir(tmp_dir):
            if filename.endswith('.h5'):
                filepath = os.path.join(tmp_dir, filename)
                file_info = {
                    "name": filename,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    "hash": get_file_hash(filepath)
                }
                model_files.append(file_info)
    
    info["model_files"] = model_files
    
    return info

@app.route('/')
def index():
    """Main dashboard"""
    system_info = get_system_info()
    return render_template('index.html', info=system_info)

@app.route('/training')
def training():
    """Training management page"""
    system_info = get_system_info()
    return render_template('training.html', info=system_info)

@app.route('/models')
def models():
    """Model management page"""
    system_info = get_system_info()
    return render_template('models.html', info=system_info)

@app.route('/transfer')
def transfer():
    """File transfer management page"""
    system_info = get_system_info()
    return render_template('transfer.html', info=system_info)

@app.route('/logs')
def logs():
    """Logs viewing page"""
    return render_template('logs.html', training_logs=training_logs, receiver_logs=receiver_logs)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Endpoints

@app.route('/api/start_training', methods=['POST'])
def start_training():
    """Start training process - Vercel compatible version"""
    global training_status
    
    if training_status == "running":
        return jsonify({"success": False, "message": "Training already running"})
    
    # In Vercel, we can't run subprocess, so we simulate
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
    
    # In Vercel, we can't run subprocess, so we simulate
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
    try:
        # In Vercel, we can't actually send files, so we simulate
        return jsonify({"success": True, "message": "Model send simulated (Vercel limitation - use local deployment for actual transfer)"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error sending model: {str(e)}"})

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
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create upload directory in /tmp
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        return jsonify({"success": True, "message": f"File {filename} uploaded successfully to /tmp"})
    
    return jsonify({"success": False, "message": "Invalid file type"})

@app.route('/api/download_model/<filename>')
def download_model(filename):
    """Download model file"""
    filepath = os.path.join('/tmp', filename)
    if os.path.exists(filepath):
        from flask import send_file
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "File not found"})

@app.route('/api/delete_model/<filename>', methods=['DELETE'])
def delete_model(filename):
    """Delete model file"""
    try:
        filepath = os.path.join('/tmp', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"success": True, "message": f"File {filename} deleted"})
        else:
            return jsonify({"success": False, "message": "File not found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting file: {str(e)}"})

@app.route('/api/test_connection')
def test_connection():
    """Test connection to PoCL server"""
    is_connected = check_pocl_server_status()
    return jsonify({
        "success": True,
        "connected": is_connected,
        "message": "Connected to PoCL server" if is_connected else "Cannot connect to PoCL server"
    })

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    """Clear logs"""
    global training_logs, receiver_logs
    log_type = request.json.get('type', 'all')
    
    if log_type == 'training' or log_type == 'all':
        training_logs.clear()
    if log_type == 'receiver' or log_type == 'all':
        receiver_logs.clear()
    
    return jsonify({"success": True, "message": "Logs cleared"})

# This is the main entry point for Vercel
def handler(request):
    return app(request)
