# NodeA Web Interface - Vercel Deployment

This is a Vercel-compatible version of the NodeA web interface for federated learning model management.

## 🚀 Vercel Deployment

### Prerequisites
- Vercel account
- Git repository with this code

### Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Vercel deployment files"
   git push origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Python configuration
   - Click "Deploy"

3. **Access your app:**
   - Your app will be available at `https://your-project-name.vercel.app`

## 📁 File Structure

```
nodeA/
├── api/
│   ├── index.py              # Main Vercel function
│   └── requirements.txt      # Vercel-specific dependencies
├── templates/                # HTML templates
│   ├── index.html
│   ├── models.html
│   ├── transfer.html
│   ├── logs.html
│   └── settings.html
├── vercel.json              # Vercel configuration
└── README_VERCEL.md         # This file
```

## ⚠️ Vercel Limitations

Due to Vercel's serverless architecture, this deployment has the following limitations:

- **No file system access** (except `/tmp`)
- **No subprocess execution** (can't run training scripts)
- **No persistent storage** (files lost between deployments)
- **Limited to 10MB uploads**
- **No real-time receiver process**
- **Functions timeout after 30 seconds**

## 🔧 Features Available

### ✅ Working Features:
- Web interface with modern UI
- Model file upload/download (stored in `/tmp`)
- PoCL connection testing
- Simulated model sending/receiving
- System information display
- Logs viewing

### ❌ Limited Features:
- Model training (use local deployment)
- Real-time file transfer (simulated)
- Persistent file storage
- Background processes

## 🏠 Local Development

For full functionality, use the local version:

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python web_interface.py

# Access at http://localhost:5000
```

## 🌐 Production Use

For production federated learning, use:
1. **Local deployment** for training and real file transfers
2. **Vercel deployment** for web interface and monitoring
3. **Separate server** for persistent model storage

## 📞 Support

- **Local Issues:** Check the main `web_interface.py`
- **Vercel Issues:** Check Vercel deployment logs
- **PoCL Issues:** Verify network connectivity to `100.122.240.40:8888`
