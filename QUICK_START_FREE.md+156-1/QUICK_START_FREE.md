# 🚀 NetScan - Quick Start (100% FREE!)

## ⚡ **Deploy in 30 Minutes - Zero Cost!**

### **What You'll Get:**
✅ Web app on Vercel (FREE)
✅ PWA installable on iOS + Android (FREE)
✅ Backend API on Railway (FREE)
✅ PostgreSQL database on Neon (FREE)
✅ Redis cache on Upstash (FREE)
✅ Push notifications via Firebase (FREE)

**💰 Total Cost: $0/month**

---

## 📋 **Prerequisites (5 minutes)**

Create these FREE accounts:

1. **GitHub**: https://github.com/signup
2. **Vercel**: https://vercel.com/signup (sign up with GitHub)
3. **Neon**: https://neon.tech/signup
4. **Upstash**: https://upstash.com/signup
5. **Railway**: https://railway.app/signup (sign up with GitHub)
6. **Firebase**: https://firebase.google.com

---

## 🚀 **Deployment Steps**

### **Step 1: Setup Database (5 minutes)**

```bash
# 1. Go to https://neon.tech
# 2. Create new project: "netscan"
# 3. Copy connection string:
export DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/netscan?sslmode=require"
```

### **Step 2: Setup Redis (5 minutes)**

```bash
# 1. Go to https://upstash.com
# 2. Create Redis database: "netscan-cache"
# 3. Copy REST URL:
export REDIS_URL="redis://default:TOKEN@xxx.upstash.io:6379"
```

### **Step 3: Deploy Backend (10 minutes)**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Set environment variables
railway variables set DATABASE_URL="$DATABASE_URL"
railway variables set REDIS_URL="$REDIS_URL"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"

# Deploy
railway up

# Get URL
railway domain
# Save this: https://netscan-production.up.railway.app
```

### **Step 4: Deploy Web App + PWA (10 minutes)**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Set environment
export VITE_API_URL="https://netscan-production.up.railway.app"

# Deploy
vercel --prod

# Your app is live!
# URL: https://netscan.vercel.app
```

---

## 📱 **Install as PWA (For Users)**

### **iOS:**
1. Open Safari → https://netscan.vercel.app
2. Tap Share (⬆️) → "Add to Home Screen"
3. Tap "Add"

### **Android:**
1. Open Chrome → https://netscan.vercel.app
2. Tap "Install" prompt
3. Tap "Install"

### **Desktop:**
1. Open Chrome/Edge → https://netscan.vercel.app
2. Click install icon in address bar
3. Click "Install"

---

## 🎉 **You're Live!**

✅ **Web App**: https://netscan.vercel.app
✅ **PWA**: Installable on all devices
✅ **Backend**: https://netscan-production.up.railway.app
✅ **Database**: Neon PostgreSQL
✅ **Cache**: Upstash Redis

**💰 Cost: $0/month**
**⏱️ Deploy Time: 30 minutes**
**👥 Supports: 500-1000 users**

---

## 📊 **Free Tier Limits**

| Service | Free Limit | Good For |
|---------|------------|----------|
| Vercel | 100GB bandwidth | ~500-1000 users |
| Neon | 0.5GB storage | ~1000 scans |
| Upstash | 10k commands/day | ~5000 users |
| Railway | $5 credit/month | ~500-1000 users |

---

## 🔄 **Updates**

```bash
# Update code
git push

# Vercel auto-deploys!
# Railway auto-deploys!
```

---

## 📞 **Need Help?**

- **GitHub Issues**: Report bugs
- **Documentation**: Full guides included

---

**🎉 NetScan is Live - 100% FREE! 🚀**
