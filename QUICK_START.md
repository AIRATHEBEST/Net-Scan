# 🚀 NetScan v2.0 - Quick Start Guide

## 🎯 Fastest Way to Deploy

### Option 1: One-Command Deployment (Docker)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/netscan.git
cd netscan

# 2. Run deployment script
chmod +x deploy.sh
./deploy.sh
```

**That's it!** 🎉

Access your app at:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000/docs

---

### Option 2: Manual Docker Compose

```bash
# 1. Setup environment
cp .env.example .env
nano .env  # Edit configuration

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs -f
```

---

### Option 3: VPS Deployment (DigitalOcean/Linode)

```bash
# 1. Create VPS (Ubuntu 22.04, 4GB RAM)

# 2. SSH into server
ssh root@YOUR_SERVER_IP

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Clone and deploy
git clone https://github.com/yourusername/netscan.git
cd netscan
chmod +x deploy.sh
./deploy.sh

# 5. Setup domain (optional)
# Point your domain A record to YOUR_SERVER_IP

# 6. Setup SSL (optional)
apt install nginx certbot python3-certbot-nginx -y
# Configure nginx (see DEPLOYMENT_GUIDE.md)
certbot --nginx -d your-domain.com
```

---

## 🔐 Security Checklist

Before going to production:

1. **Change default passwords**
   ```bash
   nano .env
   # Update SECRET_KEY and POSTGRES_PASSWORD
   ```

2. **Enable firewall**
   ```bash
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

3. **Setup SSL certificate**
   ```bash
   certbot --nginx -d your-domain.com
   ```

---

## 🧪 Test Your Deployment

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 2. Create Account
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "full_name": "Test User"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### 4. Test Features
Visit http://localhost:5173 and:
- ✅ Register account
- ✅ Create network
- ✅ Run scan
- ✅ View devices
- ✅ Test DPI capture
- ✅ View AI insights

---

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Resource Usage
```bash
docker stats
```

### Database Access
```bash
docker-compose exec postgres psql -U netscan -d netscan
```

---

## 🔄 Updates & Maintenance

### Update Application
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U netscan netscan > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U netscan netscan < backup.sql
```

---

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port Already in Use
```bash
# Find process using port
lsof -ti:8000
lsof -ti:5173

# Kill process
kill -9 $(lsof -ti:8000)
```

### Permission Denied (DPI)
```bash
# Backend needs network capabilities
# Already configured in docker-compose.yml with:
# cap_add: NET_ADMIN, NET_RAW
# privileged: true
```

---

## 🎉 You're Ready!

Your NetScan v2.0 is now live and ready to **DESTROY Fing**! 🚀

**Next Steps:**
1. Register your first account at http://localhost:5173
2. Create a network
3. Run your first scan
4. Enable DPI capture
5. View AI insights
6. Test router integration

**Need Help?**
- Full documentation: `DEPLOYMENT_GUIDE.md`
- GitHub Issues: https://github.com/yourusername/netscan/issues

---

**NetScan v2.0 - The Ultimate Network Scanner** 💜
