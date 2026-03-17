# NetScan - Complete Network Scanner & Security Platform

## 🚀 Features

### ✅ Phase 1: Real Network Engine
- **ARP Scanning**: Discover all devices on your network
- **Port Scanning**: Detect open ports and services using nmap
- **MAC Vendor Lookup**: Identify device manufacturers
- **Service Detection**: Identify running services and versions
- **OS Fingerprinting**: Detect operating systems

### ✅ Phase 2: Backend Infrastructure
- **PostgreSQL Database**: Store device history and analytics
- **REST API**: Complete API for all operations
- **WebSocket**: Real-time scan updates
- **User Authentication**: JWT-based auth system
- **Multi-Network Support**: Monitor multiple networks

### ✅ Phase 3: Advanced Device Fingerprinting
- **Intelligent Classification**: ML-based device type detection
- **Behavioral Analysis**: Traffic pattern recognition
- **Service Fingerprinting**: Detailed device identification
- **Confidence Scoring**: Accuracy metrics for classifications

### ✅ Phase 4: Notifications & Alerts
- **Push Notifications**: Firebase Cloud Messaging
- **Email Alerts**: SMTP integration
- **Real-time Alerts**: WebSocket-based notifications
- **Custom Alert Rules**: Configure notification preferences

### ✅ Phase 5: Security Scanning
- **CVE Database Integration**: Check for known vulnerabilities
- **Nmap NSE Scripts**: Advanced vulnerability detection
- **Security Scoring**: Risk assessment for each device
- **Router Security Checks**: Configuration analysis
- **Exploit Detection**: Identify potential attack vectors

### ✅ Phase 6: Cloud Sync & Remote Monitoring
- **Multi-Device Sync**: Access from anywhere
- **Historical Data**: Track changes over time
- **Remote Access**: Monitor your network remotely
- **Cross-Network Intelligence**: Device recognition across networks

### ✅ Phase 7: Deep Packet Inspection (DPI)
- **Traffic Analysis**: Monitor bandwidth per device
- **Protocol Detection**: Identify network protocols
- **Application Detection**: Recognize apps (Netflix, Zoom, etc.)
- **Anomaly Detection**: Spot unusual traffic patterns

### ✅ Phase 8: Router Control
- **Device Blocking**: Block/unblock devices
- **Bandwidth Control**: Manage bandwidth allocation
- **UPnP Integration**: Router control via UPnP/IGD
- **Parental Controls**: Time-based access restrictions

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core scanning engine
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for PostgreSQL
- **Scapy**: Packet manipulation
- **python-nmap**: Port scanning
- **Redis**: Caching layer
- **Firebase Admin**: Push notifications

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Axios**: HTTP client
- **Recharts**: Data visualization

### Database
- **PostgreSQL**: Primary database
- **Redis**: Cache and real-time data

## 📦 Installation

### Prerequisites
```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# PostgreSQL 14+
psql --version

# Redis
redis-cli --version
```

### Backend Setup

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Setup database**:
```bash
# Create PostgreSQL database
createdb netscan

# Run migrations (auto-creates tables on startup)
```

4. **Start backend**:
```bash
# Development mode
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use npm script
npm run backend
```

### Frontend Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Access application**:
```
http://localhost:5173
```

## 🔧 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/netscan
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
NVD_API_KEY=your-nvd-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Firebase Setup (Optional)
1. Create Firebase project
2. Download service account credentials
3. Place in `backend/firebase-credentials.json`
4. Configure in `.env`

### NVD API Key (Optional)
1. Register at https://nvd.nist.gov/developers/request-an-api-key
2. Add to `.env`

## 🚀 Usage

### 1. Register Account
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "secure-password",
  "full_name": "John Doe"
}
```

### 2. Create Network
```bash
POST /api/networks
{
  "name": "Home Network",
  "subnet": "192.168.1.0/24",
  "interface": "eth0"
}
```

### 3. Start Scan
```bash
POST /api/scan/network/{network_id}
```

### 4. View Devices
```bash
GET /api/devices?network_id={network_id}
```

### 5. Security Scan
```bash
POST /api/security/scan/{device_id}
```

## 🏗️ Architecture

```
NetScan/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── core/             # Config, database
│   ├── models/           # SQLAlchemy models
│   ├── scanner/          # Network scanning engine
│   ├── services/         # Business logic
│   └── requirements.txt
├── src/
│   ├── components/       # React components
│   ├── types/            # TypeScript types
│   ├── utils/            # Utilities
│   └── App.tsx
└── package.json
```

## 🔒 Security Requirements

### Linux
```bash
# Grant CAP_NET_RAW capability for packet capture
sudo setcap cap_net_raw+ep $(which python3)

# Or run as root (not recommended for production)
sudo python3 -m uvicorn api.main:app
```

### macOS
```bash
# Run with sudo for network access
sudo python3 -m uvicorn api.main:app
```

### Windows
- Run as Administrator
- Install Npcap: https://npcap.com/

## 📊 API Documentation

### Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### WebSocket
```javascript
// Real-time scan updates
const ws = new WebSocket('ws://localhost:8000/ws/scan');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Scan update:', data);
};
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker-compose up -d
```

### Production
```bash
# Backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app

# Frontend
npm run build
```

## 📈 Performance

- **Scan Speed**: ~1 second per device (ARP)
- **Port Scan**: ~2 seconds per device (quick scan)
- **Full Scan**: ~5 seconds per device (all ports)
- **Concurrent Scans**: Up to 255 devices simultaneously

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- **Scapy**: Network packet manipulation
- **Nmap**: Port scanning
- **NVD**: Vulnerability database
- **Firebase**: Push notifications

## 📞 Support

- **Issues**: https://github.com/yourusername/netscan/issues
- **Email**: support@netscan.com
- **Discord**: https://discord.gg/netscan

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Electron desktop app
- [ ] Advanced ML models
- [ ] Custom NSE scripts
- [ ] Integration with router APIs
- [ ] Network topology visualization
- [ ] Bandwidth shaping
- [ ] VPN detection

---

**Built with ❤️ by HyperDev**
