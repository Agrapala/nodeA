#!/usr/bin/env python3
"""
Global Model Receiver for NodeA
Receives global model updates from PoCL server over Tailscale network
"""

import os
import json
import socket
import threading
import hashlib
from datetime import datetime

class GlobalModelReceiver:
    def __init__(self, host="0.0.0.0", port=8889, node_id="nodeA"):
        """
        Initialize the global model receiver
        
        Args:
            host: Host address to bind to (0.0.0.0 for all interfaces)
            port: Port number to listen on
            node_id: ID of this node
        """
        self.host = host
        self.port = port
        self.node_id = node_id
        self.chunk_size = 8192  # 8KB chunks
        self.running = False
        
        # Log file for tracking global model updates
        self.log_file = "global_model_log.txt"
        
    def log_update(self, message):
        """Log global model update events to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write to log file: {e}")
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.log_update(f"❌ Error calculating hash for {file_path}: {e}")
            return None
    
    def handle_global_model(self, client_socket, client_address):
        """Handle a global model update from PoCL server"""
        try:
            self.log_update(f"🔗 New global model update from {client_address}")
            
            # Receive metadata length
            metadata_length_bytes = client_socket.recv(4)
            if len(metadata_length_bytes) != 4:
                self.log_update("❌ Invalid metadata length received")
                return
            
            metadata_length = int.from_bytes(metadata_length_bytes, byteorder='big')
            
            # Receive metadata
            metadata_bytes = b""
            while len(metadata_bytes) < metadata_length:
                chunk = client_socket.recv(min(metadata_length - len(metadata_bytes), 4096))
                if not chunk:
                    self.log_update("❌ Connection lost while receiving metadata")
                    return
                metadata_bytes += chunk
            
            try:
                metadata = json.loads(metadata_bytes.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.log_update(f"❌ Invalid JSON metadata: {e}")
                return
            
            self.log_update(f"📋 Received metadata: {metadata}")
            
            # Send acknowledgment
            client_socket.send(b"READY")
            
            # Determine file path
            file_type = metadata.get("file_type", "unknown")
            file_name = metadata.get("file_name", "global_latest.h5")
            expected_size = metadata.get("file_size", 0)
            expected_hash = metadata.get("file_hash", "")
            sender = metadata.get("sender", "unknown")
            
            if file_type != "global_model":
                self.log_update(f"❌ Unexpected file type: {file_type}")
                client_socket.send(b"INVALID_TYPE")
                return
            
            # Create backup of existing global model
            backup_path = f"global_latest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
            if os.path.exists("global_latest.h5"):
                try:
                    import shutil
                    shutil.copy2("global_latest.h5", backup_path)
                    self.log_update(f"📋 Created backup: {backup_path}")
                except Exception as e:
                    self.log_update(f"⚠️ Failed to create backup: {e}")
            
            # Receive file data
            self.log_update(f"📥 Receiving global model from {sender}")
            bytes_received = 0
            
            with open("global_latest.h5", 'wb') as f:
                while bytes_received < expected_size:
                    chunk = client_socket.recv(min(self.chunk_size, expected_size - bytes_received))
                    if not chunk:
                        self.log_update("❌ Connection lost while receiving file data")
                        return
                    
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    # Progress indicator
                    progress = (bytes_received / expected_size) * 100
                    print(f"\r📈 Progress: {progress:.1f}% ({bytes_received}/{expected_size} bytes)", end='', flush=True)
            
            print()  # New line after progress
            
            # Verify file
            if bytes_received != expected_size:
                self.log_update(f"❌ File size mismatch: expected {expected_size}, received {bytes_received}")
                client_socket.send(b"SIZE_MISMATCH")
                return
            
            # Verify hash
            actual_hash = self.calculate_file_hash("global_latest.h5")
            if actual_hash != expected_hash:
                self.log_update(f"❌ Hash mismatch: expected {expected_hash}, got {actual_hash}")
                client_socket.send(b"HASH_MISMATCH")
                return
            
            # Success
            self.log_update(f"✅ Global model updated successfully!")
            self.log_update(f"🔐 Hash verified: {actual_hash}")
            self.log_update(f"📁 File saved as: global_latest.h5")
            
            # Update metadata
            try:
                metadata_info = {
                    "last_update": datetime.now().isoformat(),
                    "sender": sender,
                    "file_hash": actual_hash,
                    "file_size": bytes_received,
                    "node_id": self.node_id
                }
                with open("global_model_info.json", "w") as f:
                    json.dump(metadata_info, f, indent=2)
                self.log_update("📄 Updated global_model_info.json")
            except Exception as e:
                self.log_update(f"⚠️ Failed to update metadata: {e}")
            
            client_socket.send(b"SUCCESS")
            
        except Exception as e:
            self.log_update(f"❌ Error handling global model update from {client_address}: {e}")
            try:
                client_socket.send(b"ERROR")
            except:
                pass
        finally:
            client_socket.close()
    
    def start_receiver(self):
        """Start the global model receiver server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.running = True
            self.log_update(f"🚀 Global model receiver started on {self.host}:{self.port}")
            self.log_update(f"👂 Listening for global model updates from PoCL server...")
            
            while self.running:
                try:
                    client_socket, client_address = server_socket.accept()
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_global_model,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except KeyboardInterrupt:
                    self.log_update("🛑 Global model receiver shutdown requested")
                    break
                except Exception as e:
                    self.log_update(f"❌ Server error: {e}")
                    time.sleep(1)
            
        except Exception as e:
            self.log_update(f"❌ Failed to start global model receiver: {e}")
        finally:
            try:
                server_socket.close()
            except:
                pass
            self.log_update("🔚 Global model receiver stopped")
    
    def stop_receiver(self):
        """Stop the receiver gracefully"""
        self.running = False

def main():
    """Main function for standalone execution"""
    print("🔧 NodeA Global Model Receiver")
    print("=" * 50)
    
    # Configuration
    HOST = "0.0.0.0"  # Listen on all interfaces
    PORT = 8889
    NODE_ID = "nodeA"
    
    receiver = GlobalModelReceiver(HOST, PORT, NODE_ID)
    
    try:
        receiver.start_receiver()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down global model receiver...")
        receiver.stop_receiver()

if __name__ == "__main__":
    main()
