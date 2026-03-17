# 🚀 NetScan v2.0 - Deployment Commands (Step-by-Step)

## ⚡ **PHASE 1: Database Setup (5 minutes)**

### **Step 1.1: Create Neon Database**

```bash
# 1. Go to: https://console.neon.tech
# 2. Click "Create Project"
# 3. Project name: "netscan"
# 4. Region: Choose closest to you
# 5. Click "Create Project"

# 6. Copy connection string from dashboard
# It looks like: postgresql://user:pass@ep-xxx.neon.tech/netscan?sslmode=require

# 7. Save it temporarily:
export NEON_DATABASE_URL="postgresql://[your-connection-string-here]"
```

### **Step 1.2: Create Upstash Redis**

```bash
# 1. Go to: https://console.upstash.com
# 2. Click "Create Database"
# 3. Name: "netscan-cache"
# 4. Region: Choose closest to you
# 5. Click "Create"

# 6. Copy REST URL from dashboard
# It looks like: https://xxx.upstash.io

# 7. Save it temporarily:
export UPSTASH_REDIS_URL="redis://default:[token]@xxx.upstash.io:6379"
```

---

## 🔧 **PHASE 2: Backend Deployment (10 minutes)**

### **Step 2.1: Install Railway CLI**

```bash
# Install Railway CLI globally
npm install -g @railway/cli

# Verify installation
railway --version
```

### **Step 2.2: Login to Railway**

```bash
# Login (opens browser)
railway login

# Should see: "Logged in as [your-email]"
```

### **Step 2.3: Initialize Railway Project**

```bash
# Navigate to backend directory
cd backend

# Initialize Railway project
railway init

# When prompted:
# - Project name: "netscan-backend"
# - Press Enter

# Link to Railway project
railway link
```

### **Step 2.4: Set Environment Variables**

```bash
# Generate secure secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Set all environment variables
railway variables set DATABASE_URL="$NEON_DATABASE_URL"
railway variables set REDIS_URL="$UPSTASH_REDIS_URL"
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Verify variables are set
railway variables
```

### **Step 2.5: Deploy Backend**

```bash
# Deploy to Railway
railway up

# Wait for deployment... (2-3 minutes)
# Should see: "✓ Deployment successful"

# Get your backend URL
railway domain

# Save this URL! It looks like:
# https://netscan-backend-production.up.railway.app
export BACKEND_URL="[your-railway-url]"
```

### **Step 2.6: Test Backend**

```bash
# Test API is working
curl $BACKEND_URL/health

# Should return: {"status":"healthy"}

# View logs
railway logs
```

---

## 🌐 **PHASE 3: Frontend Deployment (10 minutes)**

### **Step 3.1: Install Vercel CLI**

```bash
# Return to project root
cd ..

# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version
```

### **Step 3.2: Login to Vercel**

```bash
# Login (opens browser)
vercel login

# Should see: "Success! Logged in as [your-email]"
```

### **Step 3.3: Configure Environment**

```bash
# Create production environment file
cat > .env.production << EOF
VITE_API_URL=$BACKEND_URL
EOF

# Verify
cat .env.production
```

### **Step 3.4: Deploy to Vercel**

```bash
# Deploy to production
vercel --prod

# When prompted:
# - Set up and deploy: Y
# - Which scope: [your-account]
# - Link to existing project: N
# - Project name: netscan
# - Directory: ./
# - Override settings: N

# Wait for deployment... (2-3 minutes)
# Should see: "✓ Production: https://netscan.vercel.app"

# Save your frontend URL
export FRONTEND_URL="https://netscan.vercel.app"
```

### **Step 3.5: Test Frontend + PWA**

```bash
# Open in browser
echo "🌐 Frontend: $FRONTEND_URL"

# Test PWA installation:
# 1. Open in Chrome/Safari
# 2. Look for "Install" button in address bar
# 3. Click to install as PWA
```

---

## 📱 **PHASE 4: Mobile PWA (Already Done!)**

### **PWA is Live!**

Your PWA is already deployed with the frontend! Users can install it:

#### **iOS (iPhone/iPad):**
```
1. Open Safari → https://netscan.vercel.app
2. Tap Share button (⬆️)
3. Scroll down → "Add to Home Screen"
4. Tap "Add"
5. Done! NetScan icon on home screen
```

#### **Android:**
```
1. Open Chrome → https://netscan.vercel.app
2. Tap "Install" prompt
3. Tap "Install"
4. Done! NetScan icon on home screen
```

#### **Desktop (Chrome/Edge):**
```
1. Open browser → https://netscan.vercel.app
2. Click install icon in address bar
3. Click "Install"
4. Done! NetScan launches like native app
```

---

## 💻 **PHASE 5: Desktop Apps (Optional - 30 minutes)**

### **Step 5.1: Build Desktop Apps**

```bash
# Navigate to desktop directory
cd netscan-desktop

# Install dependencies
npm install

# Build for all platforms
npm run package

# This creates:
# - out/netscan-win-portable.exe (Windows)
# - out/netscan-mac-portable.app.zip (macOS)
# - out/netscan-linux.AppImage (Linux)
```

### **Step 5.2: Create GitHub Release**

```bash
# Install GitHub CLI (if not installed)
# macOS: brew install gh
# Windows: winget install GitHub.cli
# Linux: See https://cli.github.com/

# Login to GitHub
gh auth login

# Create release with apps
gh release create v2.0.0-desktop \
  out/netscan-win-portable.exe \
  out/netscan-mac-portable.app.zip \
  out/netscan-linux.AppImage \
  --title "NetScan Desktop v2.0.0" \
  --notes "Portable desktop apps - no installation required"

# Get release URL
gh release view v2.0.0-desktop --web
```

---

## 🔌 **PHASE 6: Network Agent (Optional - 30 minutes)**

### **Step 6.1: Build Docker Image**

```bash
# Navigate to agent directory
cd ../netscan-agent

# Login to Docker Hub
docker login

# Create multi-arch builder
docker buildx create --use --name multiarch

# Build and push for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t yourusername/netscan-agent:latest \
  -t yourusername/netscan-agent:v2.0.0 \
  --push .

# Verify on Docker Hub
echo "View at: https://hub.docker.com/r/yourusername/netscan-agent"
```

### **Step 6.2: Test Agent**

```bash
# Test locally
docker run -d \
  --name netscan-agent \
  -e API_URL=$BACKEND_URL \
  -e AGENT_KEY="test-key" \
  --network host \
  yourusername/netscan-agent:latest

# Check logs
docker logs netscan-agent

# Stop test
docker stop netscan-agent
docker rm netscan-agent
```

---

## 📱 **PHASE 7: Mobile APK (Optional - 1 hour)**

### **Step 7.1: Setup Expo Account**

```bash
# Navigate to mobile directory
cd ../netscan-mobile

# Install dependencies
npm install

# Login to Expo
npx expo login

# Initialize EAS
eas init
```

### **Step 7.2: Configure EAS Build**

```bash
# Create eas.json
cat > eas.json << 'EOF'
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  }
}
EOF
```

### **Step 7.3: Build Android APK**

```bash
# Build APK (takes 10-15 minutes)
eas build --platform android --profile preview

# Wait for build to complete...
# You'll get a download link

# Download APK
# Then upload to GitHub Release
gh release create v2.0.0-mobile \
  netscan.apk \
  --title "NetScan Mobile v2.0.0" \
  --notes "Android APK - Install manually"
```

---

## 🍎 **PHASE 8: iOS TestFlight (Optional - 1 hour)**

### **Step 8.1: Create Apple Developer Account**

```bash
# 1. Go to: https://developer.apple.com
# 2. Sign up (FREE for TestFlight only!)
# 3. Accept terms
```

### **Step 8.2: Build iOS App**

```bash
# Build iOS (takes 15-20 minutes)
eas build --platform ios --profile preview

# Wait for build to complete...
```

### **Step 8.3: Submit to TestFlight**

```bash
# Submit to TestFlight
eas submit --platform ios --latest

# Follow prompts to complete submission
# App will be available in TestFlight in ~24 hours
```

---

## ✅ **DEPLOYMENT COMPLETE!**

### **Your Live URLs:**

```bash
# Print all URLs
echo "🎉 NETSCAN V2.0 - DEPLOYED!"
echo ""
echo "🌐 Web App: $FRONTEND_URL"
echo "🔌 Backend API: $BACKEND_URL"
echo "📱 PWA: Install from web app"
echo "💻 Desktop: GitHub Releases"
echo "🐳 Agent: Docker Hub"
echo ""
echo "💰 Total Cost: $0/month"
echo "👥 Supports: 500-1000 users"
```

### **Share with Users:**

```markdown
# NetScan v2.0 is Live! 🚀

## Install NetScan:

### 📱 Mobile (iOS/Android):
Visit: https://netscan.vercel.app
Tap "Install" or "Add to Home Screen"

### 💻 Desktop:
Visit: https://netscan.vercel.app
Click install icon in browser

### 🐳 Network Agent:
docker run -d --network host \
  -e API_URL=$BACKEND_URL \
  yourusername/netscan-agent:latest
```

---

## 📊 **Monitor Your Deployment**

### **Check Vercel Dashboard:**
```bash
vercel dashboard
# View: Bandwidth, requests, errors
```

### **Check Railway Dashboard:**
```bash
railway dashboard
# View: API usage, logs, $5 credit
```

### **Check Neon Dashboard:**
```bash
# Go to: https://console.neon.tech
# View: Storage usage, queries
```

### **Check Upstash Dashboard:**
```bash
# Go to: https://console.upstash.com
# View: Redis commands, bandwidth
```

---

## 🆘 **Troubleshooting**

### **Backend not responding:**
```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Restart service
railway restart
```

### **Frontend not loading:**
```bash
# Check Vercel logs
vercel logs

# Redeploy
vercel --prod
```

### **PWA not installing:**
```bash
# Check manifest.json is served
curl $FRONTEND_URL/manifest.json

# Check service worker
curl $FRONTEND_URL/sw.js

# Check HTTPS is enabled (required)
```

---

## 🎉 **SUCCESS!**

You've deployed NetScan across **ALL platforms** for **$0/month**!

✅ Web App (Vercel)
✅ PWA (iOS + Android + Desktop)
✅ Backend API (Railway)
✅ Database (Neon)
✅ Cache (Upstash)
✅ Desktop Apps (GitHub Releases)
✅ Network Agent (Docker Hub)

**Total Cost: $0/month**
**Supports: 500-1000 users**

---

## 📞 **Next Steps**

1. ✅ Test all platforms
2. ✅ Share with users
3. ✅ Monitor usage
4. ✅ Collect feedback
5. ✅ Iterate and improve

**🚀 NetScan v2.0 is LIVE!**
