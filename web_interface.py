#!/usr/bin/env python3
"""
NodeA Web Interface
Comprehensive web interface for managing NodeA federated learning operations
"""

import os
import json
import threading
import time
import subprocess
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import hashlib

app = Flask(__name__)
app.secret_key = 'nodeA_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'h5', 'json', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global variables for managing processes
training_process = None
receiver_process = None
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
        "receiver_status": receiver_status
    }
    
    # Check for model files
    model_files = []
    for filename in ['model_best.h5', 'model_final.h5', 'global_latest.h5']:
        if os.path.exists(filename):
            file_info = {
                "name": filename,
                "size": os.path.getsize(filename),
                "modified": datetime.fromtimestamp(os.path.getmtime(filename)).isoformat(),
                "hash": get_file_hash(filename)
            }
            model_files.append(file_info)
    
    info["model_files"] = model_files
    
    # Check for metadata
    if os.path.exists("metadata.json"):
        try:
            with open("metadata.json", "r") as f:
                metadata = json.load(f)
            info["metadata"] = metadata
        except:
            info["metadata"] = None
    
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
    """Start training process"""
    global training_process, training_status
    
    if training_status == "running":
        return jsonify({"success": False, "message": "Training already running"})
    
    try:
        training_process = subprocess.Popen(
            ["python", "train.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        training_status = "running"
        
        # Start thread to monitor training output
        def monitor_training():
            global training_status, training_logs
            for line in iter(training_process.stdout.readline, ''):
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}] {line.strip()}"
                    training_logs.append(log_entry)
                    if len(training_logs) > 1000:  # Keep only last 1000 lines
                        training_logs = training_logs[-1000:]
            
            training_process.wait()
            training_status = "completed" if training_process.returncode == 0 else "failed"
        
        monitor_thread = threading.Thread(target=monitor_training)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return jsonify({"success": True, "message": "Training started successfully"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error starting training: {str(e)}"})

@app.route('/api/stop_training', methods=['POST'])
def stop_training():
    """Stop training process"""
    global training_process, training_status
    
    if training_process and training_process.poll() is None:
        training_process.terminate()
        training_status = "stopped"
        return jsonify({"success": True, "message": "Training stopped"})
    else:
        return jsonify({"success": False, "message": "No training process running"})

@app.route('/api/start_receiver', methods=['POST'])
def start_receiver():
    """Start global model receiver"""
    global receiver_process, receiver_status
    
    if receiver_status == "running":
        return jsonify({"success": False, "message": "Receiver already running"})
    
    try:
        receiver_process = subprocess.Popen(
            ["python", "global_model_receiver.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        receiver_status = "running"
        
        # Start thread to monitor receiver output
        def monitor_receiver():
            global receiver_status, receiver_logs
            for line in iter(receiver_process.stdout.readline, ''):
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}] {line.strip()}"
                    receiver_logs.append(log_entry)
                    if len(receiver_logs) > 1000:  # Keep only last 1000 lines
                        receiver_logs = receiver_logs[-1000:]
            
            receiver_process.wait()
            receiver_status = "stopped"
        
        monitor_thread = threading.Thread(target=monitor_receiver)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return jsonify({"success": True, "message": "Global model receiver started"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error starting receiver: {str(e)}"})

@app.route('/api/stop_receiver', methods=['POST'])
def stop_receiver():
    """Stop global model receiver"""
    global receiver_process, receiver_status
    
    if receiver_process and receiver_process.poll() is None:
        receiver_process.terminate()
        receiver_status = "stopped"
        return jsonify({"success": True, "message": "Receiver stopped"})
    else:
        return jsonify({"success": False, "message": "No receiver process running"})

@app.route('/api/send_model', methods=['POST'])
def send_model():
    """Send model to PoCL server"""
    try:
        from file_transfer_client import FileTransferClient
        
        client = FileTransferClient("100.64.0.1", 8888)  # Update with actual PoCL IP
        
        if client.send_model_and_metadata():
            return jsonify({"success": True, "message": "Model sent successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to send model"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error sending model: {str(e)}"})

@app.route('/api/system_info')
def api_system_info():
    """Get system information API"""
    return jsonify(get_system_info())

@app.route('/api/upload_model', methods=['POST'])
def upload_model():
    """Upload model file"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # If it's a model file, copy to main directory
        if filename.endswith('.h5'):
            import shutil
            shutil.copy2(filepath, filename)
        
        return jsonify({"success": True, "message": f"File {filename} uploaded successfully"})
    
    return jsonify({"success": False, "message": "Invalid file type"})

@app.route('/api/download_model/<filename>')
def download_model(filename):
    """Download model file"""
    if os.path.exists(filename):
        from flask import send_file
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "File not found"})

@app.route('/api/delete_model/<filename>', methods=['DELETE'])
def delete_model(filename):
    """Delete model file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
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

# Vercel requires the app to be accessible
# This is the main entry point for Vercel
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Starting NodeA Web Interface")
    print("=" * 50)
    print("Web interface will be available at: http://localhost:5000")
    print("Features:")
    print("- Training management")
    print("- Model file management")
    print("- File transfer to PoCL")
    print("- Global model receiver")
    print("- Real-time logs")
    print("- System monitoring")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
