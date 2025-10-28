#!/usr/bin/env python3
"""
NodeA Startup Script
Runs both global model receiver and training with automatic model transfer
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime

class NodeAManager:
    def __init__(self):
        self.receiver_running = False
        self.training_running = False
        
    def start_global_model_receiver(self):
        """Start the global model receiver in a separate thread"""
        def run_receiver():
            try:
                from global_model_receiver import GlobalModelReceiver
                receiver = GlobalModelReceiver()
                self.receiver_running = True
                receiver.start_receiver()
            except Exception as e:
                print(f"❌ Error starting global model receiver: {e}")
                self.receiver_running = False
        
        receiver_thread = threading.Thread(target=run_receiver)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Wait a moment to ensure receiver starts
        time.sleep(2)
        return self.receiver_running
    
    def run_training(self):
        """Run the training process"""
        if self.training_running:
            print("⚠️ Training already running, skipping...")
            return
        
        self.training_running = True
        print("🔄 Starting training process...")
        
        try:
            # Run train.py
            result = subprocess.run([sys.executable, "train.py"], 
                                 capture_output=False, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                print("✅ Training completed successfully")
            else:
                print(f"❌ Training failed with return code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("❌ Training timed out")
        except Exception as e:
            print(f"❌ Error running training: {e}")
        finally:
            self.training_running = False
    
    def start(self):
        """Start the NodeA manager"""
        print("🚀 Starting NodeA Manager")
        print("=" * 50)
        print("This script will:")
        print("1. Start the global model receiver")
        print("2. Run training with automatic model transfer")
        print("3. Handle global model updates from PoCL")
        print("=" * 50)
        
        # Start global model receiver
        if not self.start_global_model_receiver():
            print("❌ Failed to start global model receiver")
            return False
        
        print("✅ Global model receiver started")
        print("👂 Listening for global model updates from PoCL server...")
        
        try:
            # Run training
            self.run_training()
            
            # Keep running to receive global model updates
            print("🔄 NodeA is now running and ready to receive global model updates")
            print("💡 Press Ctrl+C to stop")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down NodeA Manager...")
        finally:
            self.receiver_running = False
            print("🔚 NodeA Manager stopped")
        
        return True

def main():
    """Main function"""
    print("🔧 NodeA Manager")
    print("=" * 50)
    
    manager = NodeAManager()
    manager.start()

if __name__ == "__main__":
    main()
