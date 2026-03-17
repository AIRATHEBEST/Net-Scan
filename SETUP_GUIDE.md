# NetScan - Complete Setup Guide

## 🚨 IMPORTANT: System Requirements

### Required Privileges
NetScan requires **elevated privileges** to perform network scanning:

- **Linux/macOS**: Root access or CAP_NET_RAW capability
- **Windows**: Administrator privileges

This is necessary for:
- Raw socket access (ARP scanning)
- Packet capture (traffic analysis)
- Port scanning (nmap)

## 📋 Step-by-Step Setup

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip postgresql redis-server nmap libpcap-dev
```

#### macOS
```bash
brew install python@3.11 postgresql redis nmap libpcap
brew services start postgresql
brew services start redis
```

#### Windows
1. Install Python 3.11+ from python.org
2. Install PostgreSQL from postgresql.org
3. Install Redis from redis.io/download
4. Install Nmap from nmap.org/download
5. Install Npcap from npcap.com

### 2. Setup PostgreSQL Database

```bash
# Create database
sudo -u postgres createdb netscan

# Create user (optional)
sudo -u postgres psql
postgres=# CREATE USER netscan WITH PASSWORD 'your-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE netscan TO netscan;
postgres=# \q
```

### 3. Setup Python Backend

```bash
# Navigate to project
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### 4. Configure Environment Variables

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://netscan:your-password@localhost:5432/netscan

# Redis
REDIS_URL=redis://localhost:6379

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here

# Firebase (optional)
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# NVD API (optional - for vulnerability scanning)
NVD_API_KEY=your-api-key

# Email (optional - for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Setup Frontend

```bash
# Install Node.js dependencies
npm install
```

### 6. Grant Network Permissions

#### Linux
```bash
# Option 1: Grant capability (recommended)
sudo setcap cap_net_raw,cap_net_admin+eip $(which python3)

# Option 2: Run as root (not recommended)
# sudo python3 -m uvicorn api.main:app
```

#### macOS
```bash
# Run with sudo
sudo python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### Windows
- Right-click terminal/IDE
- Select "Run as Administrator"

### 7. Start Services

#### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Development mode
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or with npm
npm run backend
```

#### Terminal 2: Frontend
```bash
npm run dev
```

### 8. Access Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 🔧 Optional: Firebase Setup

### 1. Create Firebase Project
1. Go to https://console.firebase.google.com
2. Create new project
3. Enable Cloud Messaging

### 2. Download Credentials
1. Project Settings → Service Accounts
2. Generate new private key
3. Save as `backend/firebase-credentials.json`

### 3. Configure Frontend
Add Firebase config to frontend (future implementation)

## 🔐 Optional: NVD API Key

For vulnerability scanning:

1. Register at https://nvd.nist.gov/developers/request-an-api-key
2. Receive API key via email
3. Add to `backend/.env`:
```env
NVD_API_KEY=your-api-key-here
```

## 📧 Optional: Email Notifications

### Gmail Setup
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## ✅ Verify Installation

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 2. Check Database Connection
```bash
psql -U netscan -d netscan -c "SELECT 1;"
```

### 3. Check Network Interfaces
```bash
curl http://localhost:8000/api/scan/interfaces
```

### 4. Test Scan
1. Register account in frontend
2. Create network
3. Start scan
4. View discovered devices

## 🐛 Troubleshooting

### Permission Denied (Linux)
```bash
# Grant capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Or run with sudo
sudo -E venv/bin/python -m uvicorn api.main:app
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U netscan -d netscan
```

### Redis Connection Failed
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

### Nmap Not Found
```bash
# Install nmap
sudo apt install nmap       # Ubuntu/Debian
brew install nmap           # macOS
# Download from nmap.org    # Windows
```

### Port 5173 Already in Use
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9

# Or change port in package.json
"dev": "vite --port 5174"
```

### Backend Port 8000 in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or change port
uvicorn api.main:app --port 8001
```

## 🚀 Production Deployment

### Using Gunicorn (Linux)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

### Using Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/netscan.service
```

```ini
[Unit]
Description=NetScan API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=root
WorkingDirectory=/path/to/netscan/backend
Environment="PATH=/path/to/netscan/backend/venv/bin"
ExecStart=/path/to/netscan/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable netscan
sudo systemctl start netscan
sudo systemctl status netscan
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name netscan.yourdomain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

## 📊 Performance Tuning

### PostgreSQL
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
```

### Redis
```bash
# Edit redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Python Backend
```python
# Increase worker processes
gunicorn -w 8 -k uvicorn.workers.UvicornWorker api.main:app
```

## 🎉 You're Ready!

Your NetScan installation is complete. Start scanning your network!

For issues, check:
- Logs: `backend/logs/`
- API docs: http://localhost:8000/docs
- GitHub Issues: https://github.com/yourusername/netscan/issues
