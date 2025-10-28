# NodeA Web Interface

A comprehensive web interface for managing NodeA federated learning operations, including training management, model file handling, file transfer to PoCL server, and global model reception.

## 🌟 Features

### 📊 Dashboard
- Real-time system status monitoring
- PoCL server connection status
- Training and receiver status indicators
- Quick action buttons for common operations
- Model files overview with metadata
- System information display

### 🧠 Training Management
- Start/stop training processes
- Real-time training progress monitoring
- Configurable training parameters
- Training logs viewing
- Model file management after training
- Automatic model transfer after successful training

### 📁 Model Management
- Upload model files (.h5, .json)
- Download model files
- Model file comparison
- Bulk operations (send, delete)
- File integrity verification with SHA256 hashes
- Model metadata display

### 🔄 File Transfer
- Send models to PoCL server
- Connection testing and status monitoring
- Transfer history tracking
- Global model receiver management
- Real-time transfer logs
- Retry mechanisms for failed transfers

### 📋 Logs
- Training process logs
- Global model receiver logs
- System logs
- Real-time log updates
- Log filtering and search
- Log download functionality

### ⚙️ Settings
- Network configuration (PoCL server, ports, timeouts)
- Training parameters (epochs, batch size, learning rate)
- Node configuration (ID, address, location)
- System settings (auto-start, logging, backups)
- Settings import/export

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Web Interface
```bash
python start_web_interface.py
```

### 3. Access Web Interface
Open your browser and navigate to:
- **Main Dashboard**: http://localhost:5000
- **Training**: http://localhost:5000/training
- **Models**: http://localhost:5000/models
- **Transfer**: http://localhost:5000/transfer
- **Logs**: http://localhost:5000/logs
- **Settings**: http://localhost:5000/settings

## 📋 Prerequisites

- Python 3.8+
- Flask 2.3.3+
- TensorFlow 2.13.0+
- All dependencies listed in `requirements.txt`

## 🏗️ Architecture

```
nodeA/
├── web_interface.py          # Main Flask application
├── start_web_interface.py    # Startup script
├── requirements.txt          # Python dependencies
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Dashboard
│   ├── training.html       # Training management
│   ├── models.html         # Model management
│   ├── transfer.html       # File transfer
│   ├── logs.html           # Logs viewing
│   └── settings.html       # Settings
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # JavaScript functionality
├── uploads/                # File upload directory
└── logs/                   # Log files directory
```

## 🔧 Configuration

### Network Settings
- **PoCL Server Host**: Tailscale IP of PoCL server (default: 100.64.0.1)
- **PoCL Server Port**: Port for file transfer (default: 8888)
- **Receiver Port**: Port for global model reception (default: 8889)
- **Connection Timeout**: Network timeout in seconds (default: 30)
- **Retry Attempts**: Number of retry attempts (default: 3)
- **Retry Delay**: Delay between retries in seconds (default: 5)

### Training Settings
- **Default Epochs**: Number of training epochs (default: 5)
- **Default Batch Size**: Training batch size (default: 16)
- **Default Learning Rate**: Learning rate (default: 0.001)
- **Accuracy Threshold**: Minimum accuracy to save model (default: 0.7)
- **Early Stopping Patience**: Epochs to wait before early stopping (default: 10)
- **Validation Split**: Fraction of data for validation (default: 0.2)

### Node Configuration
- **Node ID**: Unique identifier (default: nodeA)
- **Ethereum Address**: Blockchain address for this node
- **Node Name**: Display name (default: NodeA)
- **Location**: Geographic location (default: Local)

## 🎯 Usage Examples

### Starting Training
1. Navigate to **Training** page
2. Configure training parameters
3. Click **Start Training**
4. Monitor progress in real-time
5. Model automatically sent to PoCL after completion

### Managing Models
1. Navigate to **Models** page
2. Upload new model files
3. View model metadata and statistics
4. Download or send models to PoCL
5. Compare different models

### File Transfer
1. Navigate to **Transfer** page
2. Test connection to PoCL server
3. Select model to send
4. Monitor transfer progress
5. View transfer history

### Monitoring Logs
1. Navigate to **Logs** page
2. Select log type (Training/Receiver/System)
3. View real-time log updates
4. Clear logs if needed
5. Download logs for analysis

## 🔌 API Endpoints

### System Information
- `GET /api/system_info` - Get system status and information

### Training Management
- `POST /api/start_training` - Start training process
- `POST /api/stop_training` - Stop training process

### Receiver Management
- `POST /api/start_receiver` - Start global model receiver
- `POST /api/stop_receiver` - Stop global model receiver

### File Transfer
- `POST /api/send_model` - Send model to PoCL server
- `GET /api/test_connection` - Test PoCL server connection

### Model Management
- `POST /api/upload_model` - Upload model file
- `GET /api/download_model/<filename>` - Download model file
- `DELETE /api/delete_model/<filename>` - Delete model file

### Logs
- `POST /api/clear_logs` - Clear logs

## 🎨 UI Features

### Responsive Design
- Mobile-friendly interface
- Adaptive layouts for different screen sizes
- Touch-friendly controls

### Dark Mode Support
- Automatic dark mode detection
- Consistent theming across all pages

### Real-time Updates
- Auto-refresh for status indicators
- Live log updates
- Progress monitoring

### Interactive Elements
- Drag-and-drop file upload
- Keyboard shortcuts
- Tooltips and help text
- Confirmation dialogs

## 🔒 Security Features

- File type validation
- File size limits (100MB max)
- Secure file upload handling
- Input sanitization
- CSRF protection

## 🐛 Troubleshooting

### Common Issues

1. **Web interface won't start**
   - Check if all dependencies are installed
   - Verify Python version (3.8+)
   - Check if port 5000 is available

2. **Connection to PoCL fails**
   - Verify PoCL server is running
   - Check Tailscale connectivity
   - Verify IP address and port settings

3. **File upload fails**
   - Check file size (max 100MB)
   - Verify file type (.h5, .json only)
   - Check upload directory permissions

4. **Training won't start**
   - Check if training data is available
   - Verify model files exist
   - Check system resources

### Debug Mode
Enable debug mode by setting `debug=True` in `web_interface.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📈 Performance

- Optimized for concurrent users
- Efficient file handling
- Minimal memory usage
- Fast page load times
- Responsive UI updates

## 🔄 Integration

The web interface integrates seamlessly with:
- NodeA training scripts
- File transfer clients
- Global model receivers
- PoCL server
- Blockchain components

## 📝 License

This web interface is part of the NodeA federated learning system.

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error messages
3. Verify configuration settings
4. Test network connectivity

---

**NodeA Web Interface** - Comprehensive federated learning management made simple.
