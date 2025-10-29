#!/usr/bin/env python3
"""
NodeA Web Interface
Simple web interface for model management and PoCL communication
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import hashlib
import subprocess

app = Flask(__name__)
app.secret_key = 'nodeA_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'h5', 'json', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global variables
receiver_process = None
receiver_status = "stopped"
receiver_logs = []

# PoCL Configuration
POCL_HOST = "100.122.240.40"
POCL_PORT = 8888
NODE_IP = "100.86.236.121"

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

def get_system_info():
    """Get system information"""
    info = {
        "node_id": "nodeA",
        "node_ip": NODE_IP,
        "pocl_ip": POCL_HOST,
        "timestamp": datetime.now().isoformat(),
        "receiver_status": receiver_status,
        "deployment": "Local"
    }
    
    # Check for model files
    model_files = []
    for filename in ['model_best.h5', 'model_final.h5', 'global_latest.h5', 'global_model.h5']:
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
    return render_template('logs.html', receiver_logs=receiver_logs)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Endpoints

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
        receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Receiver stopped")
        return jsonify({"success": True, "message": "Receiver stopped"})
    else:
        return jsonify({"success": False, "message": "No receiver process running"})

@app.route('/api/send_model', methods=['POST'])
def send_model():
    """Send model_best.h5 to PoCL server"""
    try:
        if not os.path.exists("model_best.h5"):
            return jsonify({"success": False, "message": "model_best.h5 not found"})
        
        from file_transfer_client import FileTransferClient
        
        client = FileTransferClient(POCL_HOST, POCL_PORT)
        
        if client.send_model_and_metadata():
            return jsonify({"success": True, "message": "Model sent successfully to PoCL"})
        else:
            return jsonify({"success": False, "message": "Failed to send model to PoCL"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error sending model: {str(e)}"})

@app.route('/api/receive_model', methods=['POST'])
def receive_model():
    """Receive global model from PoCL"""
    try:
        # This would typically be handled by the receiver process
        # For now, we'll check if global_latest.h5 exists
        if os.path.exists("global_latest.h5"):
            return jsonify({"success": True, "message": "Global model available", "file": "global_latest.h5"})
        else:
            return jsonify({"success": False, "message": "No global model available. Start receiver first."})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error receiving model: {str(e)}"})

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
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((POCL_HOST, POCL_PORT))
        sock.close()
        is_connected = result == 0
        
        return jsonify({
            "success": True,
            "connected": is_connected,
            "message": "Connected to PoCL server" if is_connected else "Cannot connect to PoCL server"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        })

@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    """Clear logs"""
    global receiver_logs
    receiver_logs.clear()
    return jsonify({"success": True, "message": "Logs cleared"})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    print("🚀 Starting NodeA Web Interface")
    print("=" * 50)
    print(f"Node IP: {NODE_IP}")
    print(f"PoCL IP: {POCL_HOST}")
    print("Web interface will be available at: http://localhost:5000")
    print("Features:")
    print("- Model file management")
    print("- Send model_best.h5 to PoCL")
    print("- Receive global model from PoCL")
    print("- Real-time logs")
    print("- System monitoring")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
