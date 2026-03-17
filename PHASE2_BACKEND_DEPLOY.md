# 🚀 PHASE 2: Backend Deployment to Railway

## ✅ Prerequisites Complete:
- ✅ Neon Database: Connected
- ✅ Upstash Redis: Connected

---

## 📦 **Step 1: Install Railway CLI**

```bash
npm install -g @railway/cli
```

**Verify installation:**
```bash
railway --version
# Should show: railway version x.x.x
```

---

## 🔐 **Step 2: Login to Railway**

```bash
railway login
```

**This will:**
1. Open your browser
2. Ask you to authorize Railway CLI
3. Show "Logged in as [your-email]"

---

## 🎯 **Step 3: Initialize Railway Project**

```bash
# Navigate to backend directory
cd backend

# Initialize Railway project
railway init
```

**When prompted:**
- Project name: `netscan-backend`
- Press Enter to confirm

**Expected output:**
```
✓ Created project netscan-backend
✓ Linked to netscan-backend
```

---

## 🔧 **Step 4: Set Environment Variables**

**Generate secure secret key:**
```bash
export SECRET_KEY=$(openssl rand -hex 32)
echo "Generated SECRET_KEY: $SECRET_KEY"
```

**Set all environment variables:**
```bash
# Database (Neon)
railway variables set DATABASE_URL="postgresql://neondb_owner:npg_M5TA7vlKaPWh@ep-purple-wildflower-anov4vw1-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Cache (Upstash)
railway variables set REDIS_URL="redis://default:gQAAAAAAASZPAAIncDFjNjJmZmY5MzMyNTQ0ZWEyOTI4MWQyNWIyODUyMzZiNnAxNzUzNDM@genuine-ferret-75343.upstash.io:6379"

# Security
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

**Verify variables:**
```bash
railway variables
```

**Expected output:**
```
DATABASE_URL: postgresql://neondb_owner:...
REDIS_URL: redis://default:...
SECRET_KEY: [your-generated-key]
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
```

---

## 🚀 **Step 5: Deploy Backend**

```bash
railway up
```

**This will:**
1. Detect Python project
2. Install dependencies from requirements.txt
3. Build the application
4. Deploy to Railway

**Expected output:**
```
✓ Building...
✓ Deploying...
✓ Deployment successful
```

**Wait time:** 2-3 minutes

---

## 🌐 **Step 6: Get Your Backend URL**

```bash
railway domain
```

**Expected output:**
```
https://netscan-backend-production-xxxx.up.railway.app
```

**Save this URL!** You'll need it for Phase 3.

```bash
# Save to environment variable
export BACKEND_URL="https://netscan-backend-production-xxxx.up.railway.app"
echo "Backend URL: $BACKEND_URL"
```

---

## ✅ **Step 7: Test Backend API**

```bash
# Test health endpoint
curl $BACKEND_URL/health
```

**Expected response:**
```json
{"status":"healthy","timestamp":"2024-01-XX..."}
```

**Test API docs:**
```bash
# Open in browser
echo "API Docs: $BACKEND_URL/docs"
```

---

## 📊 **Step 8: Check Deployment Status**

```bash
# View logs
railway logs

# View deployment status
railway status

# Open Railway dashboard
railway open
```

---

## 🎉 **PHASE 2 COMPLETE!**

### **What You Have Now:**
- ✅ Backend API deployed to Railway
- ✅ Connected to Neon PostgreSQL
- ✅ Connected to Upstash Redis
- ✅ Health check passing
- ✅ API documentation live

### **Your Backend URL:**
```
$BACKEND_URL
```

### **Free Tier Status:**
- Railway: $5 credit (lasts ~1 month)
- Supports: 500-1000 users
- Cost after credit: ~$5/month

---

## 🔜 **NEXT: PHASE 3 - Frontend Deployment**

Ready to deploy the frontend to Vercel?

**Quick Preview:**
1. Install Vercel CLI
2. Configure environment with your backend URL
3. Deploy frontend
4. Test PWA installation

**Let me know when you're ready for Phase 3!** 🚀
