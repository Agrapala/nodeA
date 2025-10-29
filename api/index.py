#!/usr/bin/env python3
"""
Vercel-compatible NodeA Web Interface
Serverless version for Vercel deployment
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import hashlib

app = Flask(__name__)
app.secret_key = 'nodeA_secret_key_2024'

# PoCL Configuration
POCL_HOST = "100.122.240.40"
POCL_PORT = 8888
NODE_IP = "100.86.236.121"

# Global variables (will reset on each request in serverless)
receiver_status = "stopped"
receiver_logs = []

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
        "deployment": "Vercel",
        "limitations": [
            "No file system access (except /tmp)",
            "No subprocess execution",
            "No persistent storage",
            "Limited to 10MB uploads",
            "No real-time receiver process"
        ]
    }
    
    # Check for model files in /tmp (Vercel's writable directory)
    model_files = []
    tmp_dir = '/tmp'
    if os.path.exists(tmp_dir):
        try:
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
        except Exception as e:
            print(f"Error reading /tmp directory: {e}")
    
    info["model_files"] = model_files
    
    return info

def render_template(template_name, **kwargs):
    """Simple template renderer for Vercel"""
    try:
        with open(f'templates/{template_name}', 'r') as f:
            content = f.read()
        
        # Simple template variable replacement
        if 'info' in kwargs:
            info = kwargs['info']
            content = content.replace('{{ info.node_id }}', info.get('node_id', ''))
            content = content.replace('{{ info.node_ip }}', info.get('node_ip', ''))
            content = content.replace('{{ info.pocl_ip }}', info.get('pocl_ip', ''))
            content = content.replace('{{ info.timestamp }}', info.get('timestamp', ''))
            content = content.replace('{{ info.receiver_status }}', info.get('receiver_status', ''))
            content = content.replace('{{ info.deployment }}', info.get('deployment', ''))
            
            # Handle model files
            model_files_html = ""
            if info.get('model_files'):
                for file in info['model_files']:
                    model_files_html += f"""
                    <tr>
                        <td><i class="fas fa-file"></i> {file['name']}</td>
                        <td>{file['size'] / 1024 / 1024:.2f} MB</td>
                        <td>{file['modified']}</td>
                        <td><code>{file['hash'][:16]}...</code></td>
                        <td>
                            <a href="/api/download_model/{file['name']}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download"></i>
                            </a>
                        </td>
                    </tr>
                    """
            content = content.replace('{{ model_files_html }}', model_files_html)
        
        return content
    except Exception as e:
        return f"Error loading template: {str(e)}"

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
    return render_template('settings.html', info=get_system_info())

# API Endpoints

@app.route('/api/start_receiver', methods=['POST'])
def start_receiver():
    """Start global model receiver - Vercel compatible version"""
    global receiver_status
    
    # In Vercel, we can't run subprocess, so we simulate
    receiver_status = "running"
    receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Receiver started (simulated)")
    receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Note: Actual receiver requires local deployment")
    
    return jsonify({"success": True, "message": "Global model receiver started (simulated - Vercel limitation)"})

@app.route('/api/stop_receiver', methods=['POST'])
def stop_receiver():
    """Stop global model receiver"""
    global receiver_status
    
    receiver_status = "stopped"
    receiver_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Receiver stopped")
    return jsonify({"success": True, "message": "Receiver stopped"})

@app.route('/api/send_model', methods=['POST'])
def send_model():
    """Send model_best.h5 to PoCL server - Vercel compatible version"""
    try:
        # Check if model exists in /tmp
        model_path = '/tmp/model_best.h5'
        if not os.path.exists(model_path):
            return jsonify({"success": False, "message": "model_best.h5 not found in /tmp"})
        
        # In Vercel, we can't actually send files, so we simulate
        return jsonify({"success": True, "message": "Model send simulated (Vercel limitation - use local deployment for actual transfer)"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error sending model: {str(e)}"})

@app.route('/api/receive_model', methods=['POST'])
def receive_model():
    """Receive global model from PoCL - Vercel compatible version"""
    try:
        # Check if global model exists in /tmp
        global_model_path = '/tmp/global_latest.h5'
        if os.path.exists(global_model_path):
            return jsonify({"success": True, "message": "Global model available", "file": "global_latest.h5"})
        else:
            return jsonify({"success": False, "message": "No global model available. Upload to /tmp directory."})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error receiving model: {str(e)}"})

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
    
    if file.filename.endswith('.h5'):
        try:
            # Save to /tmp directory
            filepath = os.path.join('/tmp', file.filename)
            file.save(filepath)
            return jsonify({"success": True, "message": f"File {file.filename} uploaded successfully to /tmp"})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error uploading file: {str(e)}"})
    
    return jsonify({"success": False, "message": "Only .h5 files are supported"})

@app.route('/api/download_model/<filename>')
def download_model(filename):
    """Download model file"""
    filepath = os.path.join('/tmp', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"success": False, "message": "File not found"})

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
