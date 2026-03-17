# 🚀 NetScan v2.0 - Production Deployment Guide

## 📋 Deployment Options

Choose your deployment strategy:

1. **🐳 Docker Compose** (Recommended - Easiest)
2. **☁️ Cloud Platforms** (AWS/GCP/Azure)
3. **🖥️ VPS Deployment** (DigitalOcean/Linode)
4. **🔧 Manual Setup** (Ubuntu/Debian)

---

## 🐳 Option 1: Docker Compose (RECOMMENDED)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB storage

### Step 1: Create Docker Configuration

```bash
# Clone/navigate to project
cd netscan

# Create .env file
cp .env.example .env
nano .env
```

### Step 2: Configure Environment Variables

```env
# Database
DATABASE_URL=postgresql://netscan:secure_password_here@postgres:5432/netscan
REDIS_URL=redis://redis:6379

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-here-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firebase (Optional)
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# NVD API (Optional)
NVD_API_KEY=your-nvd-api-key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
VITE_API_URL=http://localhost:8000
```

### Step 3: Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 4: Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ☁️ Option 2: Cloud Platform Deployment

### AWS Deployment

#### Architecture
```
┌─────────────────────────────────────────┐
│  CloudFront (CDN)                       │
│  ├─ S3 (Frontend)                       │
│  └─ ALB (Backend)                       │
│      ├─ ECS Fargate (API)               │
│      ├─ RDS PostgreSQL                  │
│      └─ ElastiCache Redis               │
└─────────────────────────────────────────┘
```

#### Step 1: Setup RDS PostgreSQL

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier netscan-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username netscan \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --backup-retention-period 7 \
  --multi-az
```

#### Step 2: Setup ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id netscan-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx
```

#### Step 3: Deploy Backend to ECS

```bash
# Build and push Docker image
docker build -t netscan-backend ./backend
docker tag netscan-backend:latest YOUR_ECR_REPO/netscan-backend:latest
docker push YOUR_ECR_REPO/netscan-backend:latest

# Create ECS task definition
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster netscan-cluster \
  --service-name netscan-backend \
  --task-definition netscan-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

#### Step 4: Deploy Frontend to S3 + CloudFront

```bash
# Build frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://netscan-frontend/

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name netscan-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

### GCP Deployment

```bash
# Deploy backend to Cloud Run
gcloud run deploy netscan-backend \
  --image gcr.io/YOUR_PROJECT/netscan-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --memory 2Gi \
  --cpu 2

# Deploy frontend to Firebase Hosting
npm run build
firebase deploy --only hosting
```

### Azure Deployment

```bash
# Create resource group
az group create --name netscan-rg --location eastus

# Deploy backend to Container Instances
az container create \
  --resource-group netscan-rg \
  --name netscan-backend \
  --image YOUR_ACR/netscan-backend:latest \
  --cpu 2 --memory 4 \
  --environment-variables DATABASE_URL=postgresql://... \
  --ports 8000

# Deploy frontend to Static Web Apps
az staticwebapp create \
  --name netscan-frontend \
  --resource-group netscan-rg \
  --source dist/ \
  --location eastus
```

---

## 🖥️ Option 3: VPS Deployment (DigitalOcean/Linode)

### Step 1: Create VPS

**Recommended Specs:**
- 4GB RAM
- 2 CPU cores
- 50GB SSD
- Ubuntu 22.04 LTS

### Step 2: Initial Server Setup

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create non-root user
adduser netscan
usermod -aG docker netscan
usermod -aG sudo netscan
```

### Step 3: Deploy Application

```bash
# Switch to netscan user
su - netscan

# Clone repository
git clone https://github.com/yourusername/netscan.git
cd netscan

# Configure environment
cp .env.example .env
nano .env

# Start services
docker-compose up -d

# Setup nginx reverse proxy
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/netscan
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/netscan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 Option 4: Manual Setup (Ubuntu/Debian)

### Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Install network tools
sudo apt install nmap libpcap-dev -y
```

### Step 2: Setup Database

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE netscan;
CREATE USER netscan WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE netscan TO netscan;
\q
```

### Step 3: Setup Backend

```bash
# Create app directory
sudo mkdir -p /opt/netscan
sudo chown $USER:$USER /opt/netscan
cd /opt/netscan

# Clone or copy project
git clone https://github.com/yourusername/netscan.git .

# Setup Python environment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run database migrations
alembic upgrade head
```

### Step 4: Setup Frontend

```bash
cd /opt/netscan
npm install
npm run build
```

### Step 5: Setup Systemd Services

**Backend Service** (`/etc/systemd/system/netscan-backend.service`):
```ini
[Unit]
Description=NetScan Backend API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=root
WorkingDirectory=/opt/netscan/backend
Environment="PATH=/opt/netscan/backend/venv/bin"
ExecStart=/opt/netscan/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/netscan-frontend.service`):
```ini
[Unit]
Description=NetScan Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/netscan
ExecStart=/usr/bin/npm run preview -- --port 5173 --host 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable netscan-backend netscan-frontend
sudo systemctl start netscan-backend netscan-frontend

# Check status
sudo systemctl status netscan-backend
sudo systemctl status netscan-frontend
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### 2. SSL/TLS Setup

```bash
# Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 3. Environment Security

```bash
# Secure .env file
chmod 600 .env

# Generate strong secret key
openssl rand -hex 32
```

### 4. Database Security

```bash
# PostgreSQL hardening
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Change authentication method to scram-sha-256

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 📊 Monitoring & Logging

### Setup Logging

```bash
# Create log directory
sudo mkdir -p /var/log/netscan
sudo chown $USER:$USER /var/log/netscan

# Configure log rotation
sudo nano /etc/logrotate.d/netscan
```

**Log Rotation Config:**
```
/var/log/netscan/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 netscan netscan
    sharedscripts
    postrotate
        systemctl reload netscan-backend
    endscript
}
```

### Setup Monitoring (Optional)

```bash
# Install Prometheus & Grafana
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /opt/prometheus:/etc/prometheus \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

---

## 🧪 Post-Deployment Testing

### 1. Health Checks

```bash
# Backend health
curl http://your-domain.com/health

# API documentation
curl http://your-domain.com/docs
```

### 2. Feature Testing

```bash
# Test device scan
curl -X POST http://your-domain.com/api/scan/start \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test DPI
curl -X POST http://your-domain.com/api/intelligence/dpi/start \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test AI insights
curl http://your-domain.com/api/intelligence/network/{id}/insights \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils -y

# Run load test
ab -n 1000 -c 10 http://your-domain.com/
```

---

## 🔄 Backup & Recovery

### Database Backup

```bash
# Create backup script
cat > /opt/netscan/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/netscan/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U netscan netscan > $BACKUP_DIR/netscan_$DATE.sql

# Compress
gzip $BACKUP_DIR/netscan_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "netscan_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/netscan/backup.sh

# Setup cron job
crontab -e
# Add: 0 2 * * * /opt/netscan/backup.sh
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

```bash
# Add more backend workers
docker-compose up -d --scale backend=3

# Load balancer (nginx)
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Database Replication

```bash
# Setup PostgreSQL read replicas
# Master: postgresql://master:5432/netscan
# Replica: postgresql://replica:5432/netscan
```

---

## 🎯 Performance Optimization

### 1. Enable Caching

```bash
# Redis caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

### 2. CDN Setup

```bash
# CloudFlare
# Add your domain to CloudFlare
# Enable caching for static assets
```

### 3. Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_device_ip ON devices(ip_address);
CREATE INDEX idx_device_mac ON devices(mac_address);
CREATE INDEX idx_history_device ON device_history(device_id);
CREATE INDEX idx_history_timestamp ON device_history(timestamp);
```

---

## 🚨 Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend
# or
journalctl -u netscan-backend -f

# Common issues:
# - Database connection failed: Check DATABASE_URL
# - Permission denied: Run with sudo or check file permissions
# - Port already in use: Change port or kill existing process
```

### Frontend Build Fails

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### DPI Not Capturing

```bash
# Grant network capabilities
sudo setcap cap_net_raw,cap_net_admin+eip $(which python3)

# Or run backend as root (not recommended)
sudo systemctl edit netscan-backend
# Add: User=root
```

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] Database created and migrated
- [ ] Redis running
- [ ] Backend API responding
- [ ] Frontend accessible
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backups scheduled
- [ ] Load testing passed
- [ ] Documentation updated

---

## 🎉 You're Live!

Your NetScan v2.0 is now deployed and ready to **DESTROY Fing**! 🚀

**Next Steps:**
1. Register your first account
2. Create a network
3. Run your first scan
4. Enable DPI capture
5. View AI insights
6. Test router integration
7. Analyze device behavior

**Support:**
- Documentation: http://your-domain.com/docs
- GitHub Issues: https://github.com/yourusername/netscan/issues

---

**NetScan v2.0 - Production Deployment Complete!** 💜🚀
