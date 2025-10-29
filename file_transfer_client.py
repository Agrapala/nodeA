#!/usr/bin/env python3
"""
File Transfer Client for NodeA
Sends best_model.h5 and metadata.json to PoCL server over Tailscale network
"""

import os
import json
import socket
import time
import hashlib
import threading
from datetime import datetime
import requests

class FileTransferClient:
    def __init__(self, pocl_host="100.122.240.40", pocl_port=8888):
        """
        Initialize the file transfer client
        
        Args:
            pocl_host: Tailscale IP address of PoCL server
            pocl_port: Port number for file transfer
        """
        self.pocl_host = pocl_host
        self.pocl_port = pocl_port
        self.model_file = "model_best.h5"
        self.metadata_file = "metadata.json"
        self.chunk_size = 8192  # 8KB chunks for reliable transfer
        
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"❌ Error calculating hash for {file_path}: {e}")
            return None
    
    def send_file(self, file_path, file_type="model"):
        """
        Send a file to PoCL server
        
        Args:
            file_path: Path to the file to send
            file_type: Type of file (model, metadata, etc.)
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
            
        file_size = os.path.getsize(file_path)
        file_hash = self.calculate_file_hash(file_path)
        
        if not file_hash:
            return False
            
        print(f"📤 Sending {file_type} file: {file_path}")
        print(f"📊 File size: {file_size} bytes")
        print(f"🔐 File hash: {file_hash}")
        
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)  # 30 second timeout
            
            print(f"🔗 Connecting to PoCL server at {self.pocl_host}:{self.pocl_port}")
            sock.connect((self.pocl_host, self.pocl_port))
            
            # Send file metadata first
            metadata = {
                "file_type": file_type,
                "file_name": os.path.basename(file_path),
                "file_size": file_size,
                "file_hash": file_hash,
                "timestamp": datetime.now().isoformat(),
                "node_id": "nodeA"
            }
            
            metadata_json = json.dumps(metadata).encode('utf-8')
            metadata_length = len(metadata_json)
            
            # Send metadata length and metadata
            sock.send(metadata_length.to_bytes(4, byteorder='big'))
            sock.send(metadata_json)
            
            # Wait for server acknowledgment
            ack = sock.recv(1024).decode('utf-8')
            if ack != "READY":
                print(f"❌ Server not ready: {ack}")
                sock.close()
                return False
            
            # Send file data in chunks
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    sock.send(chunk)
                    bytes_sent += len(chunk)
                    
                    # Progress indicator
                    progress = (bytes_sent / file_size) * 100
                    print(f"\r📈 Progress: {progress:.1f}% ({bytes_sent}/{file_size} bytes)", end='', flush=True)
            
            print()  # New line after progress
            
            # Wait for final acknowledgment
            final_ack = sock.recv(1024).decode('utf-8')
            sock.close()
            
            if final_ack == "SUCCESS":
                print(f"✅ File sent successfully!")
                return True
            else:
                print(f"❌ Transfer failed: {final_ack}")
                return False
                
        except socket.timeout:
            print(f"❌ Connection timeout to {self.pocl_host}:{self.pocl_port}")
            return False
        except ConnectionRefusedError:
            print(f"❌ Connection refused by {self.pocl_host}:{self.pocl_port}")
            print("💡 Make sure PoCL server is running and accessible via Tailscale")
            return False
        except Exception as e:
            print(f"❌ Error sending file: {e}")
            return False
    
    def send_model_and_metadata(self):
        """Send both model file and metadata to PoCL server"""
        print("🚀 Starting file transfer to PoCL server...")
        print(f"🌐 Target: {self.pocl_host}:{self.pocl_port}")
        
        success_count = 0
        
        # Send model file
        if os.path.exists(self.model_file):
            if self.send_file(self.model_file, "model"):
                success_count += 1
        else:
            print(f"⚠️ Model file not found: {self.model_file}")
        
        # Send metadata file
        if os.path.exists(self.metadata_file):
            if self.send_file(self.metadata_file, "metadata"):
                success_count += 1
        else:
            print(f"⚠️ Metadata file not found: {self.metadata_file}")
        
        if success_count == 2:
            print("🎉 All files sent successfully!")
            return True
        elif success_count == 1:
            print("⚠️ Only one file sent successfully")
            return False
        else:
            print("❌ No files sent successfully")
            return False
    
    def check_pocl_server_status(self):
        """Check if PoCL server is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.pocl_host, self.pocl_port))
            sock.close()
            return result == 0
        except Exception:
            return False

def main():
    """Main function for standalone execution"""
    print("🔧 NodeA File Transfer Client")
    print("=" * 50)
    
    # Configuration - Update these for your Tailscale setup
    POCL_HOST = "100.122.240.40"  # PoCL Tailscale IP
    POCL_PORT = 8888
    
    client = FileTransferClient(POCL_HOST, POCL_PORT)
    
    # Check server status
    print(f"🔍 Checking PoCL server status at {POCL_HOST}:{POCL_PORT}")
    if not client.check_pocl_server_status():
        print("❌ PoCL server is not reachable")
        print("💡 Please ensure:")
        print("   1. PoCL server is running")
        print("   2. Tailscale is connected")
        print("   3. Correct IP address and port")
        return False
    
    print("✅ PoCL server is reachable")
    
    # Send files
    return client.send_model_and_metadata()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
