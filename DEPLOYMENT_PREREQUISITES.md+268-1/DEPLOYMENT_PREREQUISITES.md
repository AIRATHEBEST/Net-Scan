# 🎯 NetScan Multi-Platform Deployment - Prerequisites

## 📋 Required Accounts (Setup in Order)

### 1. **GitHub** (Free)
- **Purpose**: Code hosting + CI/CD
- **Sign up**: https://github.com/signup
- **What to do**:
  1. Create account
  2. Verify email
  3. Create new repository: `netscan`
  4. Set repository to public (for free CI/CD)

### 2. **Vercel** (Free - Hobby Plan)
- **Purpose**: Web app hosting
- **Sign up**: https://vercel.com/signup
- **What to do**:
  1. Sign up with GitHub account
  2. Grant Vercel access to your GitHub repos
  3. Note your Vercel Team ID (Settings → General)

### 3. **Neon** (Free - 0.5GB)
- **Purpose**: PostgreSQL database
- **Sign up**: https://neon.tech/signup
- **What to do**:
  1. Create account
  2. Create new project: "netscan"
  3. Copy connection string (will look like):
     ```
     postgresql://user:pass@ep-xxx.neon.tech/netscan?sslmode=require
     ```
  4. Save this for later!

### 4. **Upstash** (Free - 10k commands/day)
- **Purpose**: Redis cache/queue
- **Sign up**: https://upstash.com/signup
- **What to do**:
  1. Create account
  2. Create Redis database: "netscan-cache"
  3. Select region closest to your users
  4. Copy REST URL and token:
     ```
     UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
     UPSTASH_REDIS_REST_TOKEN=AxxxYyy
     ```

### 5. **Railway** (Free - $5 credit/month)
- **Purpose**: Backend API hosting
- **Sign up**: https://railway.app/signup
- **What to do**:
  1. Sign up with GitHub
  2. Link your GitHub repository
  3. Install Railway CLI:
     ```bash
     npm i -g @railway/cli
     railway login
     ```

### 6. **Firebase** (Free - Spark Plan)
- **Purpose**: Push notifications + Auth
- **Sign up**: https://firebase.google.com
- **What to do**:
  1. Create new project: "netscan"
  2. Add iOS app: `com.netscan.app`
  3. Add Android app: `com.netscan.app`
  4. Download `google-services.json` (Android)
  5. Download `GoogleService-Info.plist` (iOS)
  6. Enable Cloud Messaging

### 7. **Expo** (Free)
- **Purpose**: Mobile app builds
- **Sign up**: https://expo.dev/signup
- **What to do**:
  1. Create account
  2. Install EAS CLI:
     ```bash
     npm install -g eas-cli
     eas login
     ```
  3. Create new project in dashboard

### 8. **Apple Developer** ($99/year) - OPTIONAL for iOS
- **Purpose**: iOS App Store distribution
- **Sign up**: https://developer.apple.com
- **What to do**:
  1. Enroll in Apple Developer Program ($99/year)
  2. Create App ID: `com.netscan.app`
  3. Create provisioning profiles
  4. Get Team ID from Membership page

### 9. **Google Play Console** ($25 one-time) - OPTIONAL for Android
- **Purpose**: Android Play Store distribution
- **Sign up**: https://play.google.com/console
- **What to do**:
  1. Pay $25 one-time registration fee
  2. Create new app: "NetScan"
  3. Create service account for API access
  4. Download JSON key file

### 10. **Docker Hub** (Free)
- **Purpose**: Agent container hosting
- **Sign up**: https://hub.docker.com/signup
- **What to do**:
  1. Create account
  2. Create repository: `netscan-agent`
  3. Note your username

---

## 🔑 Environment Variables to Collect

As you go through the setup, save these values:

```bash
# Database (Neon)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/netscan?sslmode=require

# Redis (Upstash)
REDIS_URL=redis://default:TOKEN@xxx.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AxxxYyy

# Backend (Railway)
RAILWAY_PROJECT_ID=xxx
API_URL=https://netscan-production.up.railway.app

# Frontend (Vercel)
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx

# Mobile (Expo)
EXPO_TOKEN=xxx
EAS_PROJECT_ID=xxx

# iOS (Apple Developer)
APPLE_ID=your-apple-id@email.com
APPLE_TEAM_ID=xxx
ASC_APP_ID=xxx

# Android (Google Play)
GOOGLE_PLAY_SERVICE_ACCOUNT=path/to/service-account.json

# Docker Hub
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password

# Security (Generate these)
SECRET_KEY=xxx  # Generate: openssl rand -hex 32
AGENT_KEY=xxx   # Generate: openssl rand -hex 32
```

---

## 🛠️ Required Software

### On Your Development Machine:

```bash
# 1. Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
node --version  # Should be 20+

# 2. Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version

# 3. Git
sudo apt install git -y
git --version

# 4. Docker
curl -fsSL https://get.docker.com | sh
docker --version

# 5. Expo CLI
npm install -g expo-cli eas-cli
expo --version

# 6. Vercel CLI
npm install -g vercel
vercel --version

# 7. Railway CLI
npm install -g @railway/cli
railway --version

# 8. GitHub CLI (optional but helpful)
sudo apt install gh -y
gh --version
```

---

## 📝 Pre-Deployment Checklist

Before starting deployment, verify you have:

### ✅ Accounts Created
- [ ] GitHub account
- [ ] Vercel account
- [ ] Neon account
- [ ] Upstash account
- [ ] Railway account
- [ ] Firebase project
- [ ] Expo account
- [ ] Docker Hub account
- [ ] Apple Developer (optional - iOS)
- [ ] Google Play Console (optional - Android)

### ✅ Software Installed
- [ ] Node.js 20+
- [ ] Python 3.11+
- [ ] Git
- [ ] Docker
- [ ] Expo CLI + EAS CLI
- [ ] Vercel CLI
- [ ] Railway CLI

### ✅ Configuration Files Downloaded
- [ ] Firebase `google-services.json`
- [ ] Firebase `GoogleService-Info.plist`
- [ ] Google Play service account JSON (if using Play Store)

### ✅ Environment Variables Collected
- [ ] Database URL (Neon)
- [ ] Redis URL (Upstash)
- [ ] API tokens (Vercel, Expo, etc.)
- [ ] Secret keys generated

---

## 💰 Cost Summary

| Service | Free Tier | When You'll Need Paid |
|---------|-----------|----------------------|
| GitHub | ✅ Unlimited | Never (for this project) |
| Vercel | ✅ 100GB bandwidth | >100GB traffic/month |
| Neon | ✅ 0.5GB storage | >0.5GB data |
| Upstash | ✅ 10k commands/day | >10k Redis ops/day |
| Railway | ✅ $5 credit/mo | After $5 usage |
| Firebase | ✅ 10GB storage | >10GB storage |
| Expo | ✅ Unlimited builds | Never |
| Docker Hub | ✅ Unlimited pulls | Never |
| **Apple Developer** | ❌ $99/year | Required for iOS |
| **Google Play** | ❌ $25 one-time | Required for Android |

**Estimated Monthly Cost**: 
- **Minimum**: $0 (web + agent only)
- **With iOS**: $8.25/month ($99/year)
- **With iOS + Android**: $10.33/month ($99/year + $25 one-time)

---

## 🚀 Ready to Deploy?

Once you have:
1. ✅ All accounts created
2. ✅ All software installed
3. ✅ All configuration files downloaded
4. ✅ All environment variables saved

You're ready to proceed with the deployment!

**Next step**: Follow `MULTI_PLATFORM_DEPLOYMENT.md`

---

## 🆘 Need Help?

If you get stuck on any prerequisite:

1. **Account Issues**: Check the service's help docs
2. **Installation Issues**: Check software version compatibility
3. **Configuration Issues**: Double-check URLs and tokens

**Common Issues**:
- **Node.js version too old**: Update to 20+
- **Python version too old**: Install 3.11+
- **Docker permission denied**: Add user to docker group
- **CLI not found**: Restart terminal after installation

---

**Once prerequisites are complete, you're ready to deploy!** 🚀
