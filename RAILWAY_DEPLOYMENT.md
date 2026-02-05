# 🚂 Railway.app Deployment Guide

Complete guide to deploy the HCL Honeypot API to Railway.app.

---

## ⚡ Quick Deploy (3 Minutes)

### **Method 1: Deploy from GitHub (Recommended)**

1. **Go to [Railway.app](https://railway.app)** and sign up/login with GitHub

2. **Click "New Project"** → **"Deploy from GitHub repo"**

3. **Select your repository:** `0x-rudra/hcl-honeypot`

4. **Railway will auto-detect Python** and deploy automatically!

5. **Add Environment Variables:**
   - Click on your deployment
   - Go to "Variables" tab
   - Add:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     API_KEY=honeypot-test-key-2026-secure
     PORT=8000
     ```

6. **Get your URL:**
   - Go to "Settings" tab
   - Click "Generate Domain"
   - Your API will be at: `https://your-app.up.railway.app/honeypot`

**Done! ✅**

---

### **Method 2: Deploy with Railway CLI**

1. **Install Railway CLI:**
   ```powershell
   # Windows (PowerShell)
   iwr https://railway.app/install.ps1 -useb | iex

   # Mac/Linux
   bash <(curl -fsSL https://railway.app/install.sh)
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize and Deploy:**
   ```bash
   cd HCL-honeypot

   # Link to new project
   railway init

   # Add environment variables
   railway variables set GEMINI_API_KEY=your_key
   railway variables set API_KEY=honeypot-test-key-2026-secure
   railway variables set PORT=8000

   # Deploy
   railway up

   # Generate public URL
   railway domain
   ```

---

## ✅ Verify Deployment

### **Check Logs:**
```bash
railway logs
```

Or in Railway dashboard → "Deployments" → Click latest deployment

### **Test the API:**
```bash
curl -X POST https://your-app.up.railway.app/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "user",
      "text": "hello",
      "timestamp": "2026-02-06T10:00:00Z"
    }
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "reply": "hey! how can i help?"
}
```

---

## 🎯 Your Live API URLs

- **Main Endpoint:** `https://your-app.up.railway.app/honeypot`
- **Health Check:** `https://your-app.up.railway.app/health`
- **Docs:** `https://your-app.up.railway.app/docs`

---

## 🔧 Common Commands

### **View Logs:**
```bash
railway logs
railway logs --follow  # Live logs
```

### **Update Environment Variables:**
```bash
railway variables set GEMINI_API_KEY=new_key
railway variables set API_KEY=new_api_key
```

### **View All Variables:**
```bash
railway variables
```

### **Redeploy After Code Changes:**
```bash
git add .
git commit -m "Update code"
git push

# Railway auto-deploys from GitHub!
# Or manually: railway up
```

### **Link Existing Project:**
```bash
railway link
```

### **Open Dashboard:**
```bash
railway open
```

### **Check Status:**
```bash
railway status
```

---

## 🌍 Performance & Region

**Railway Features:**
- **Auto-scaling** - Handles traffic spikes automatically
- **Global CDN** - Fast worldwide
- **Zero cold starts** - Always responsive
- **Automatic HTTPS** - SSL included
- **GitHub integration** - Auto-deploy on push

**Regions:** Railway automatically routes to the nearest region for best performance.

---

## 💰 Pricing

**Free Tier ($5 credit/month):**
- ~400 hours runtime
- 512MB RAM
- 1GB disk
- Enough for development & testing

**Upgrade if needed:**
- Hobby: $5/month (more resources)
- Pro: $20/month (team features)

**Current Setup:** Should stay within free tier ✅

---

## 🐛 Troubleshooting

### **Build Failures:**
Check build logs in Railway dashboard:
- Dashboard → Deployments → Click failed deployment
- Check "Build Logs" tab

### **App Crashes:**
```bash
railway logs
```

Common issues:
- Missing environment variables (GEMINI_API_KEY)
- Wrong PORT (Railway provides $PORT, must use it)
- Dependencies not installed (check requirements.txt)

### **Environment Variables Not Working:**
```bash
# List all variables
railway variables

# Redeploy after setting variables
railway up --detach
```

### **Domain Issues:**
```bash
# Generate new domain
railway domain

# Or use custom domain in dashboard
```

---

## 🔄 Update Workflow

1. **Make code changes locally**

2. **Test locally:**
   ```bash
   $env:PORT = "8000"; uvicorn app.main:app --reload
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Fix: description"
   git push
   ```

4. **Railway auto-deploys!** (if GitHub integration is set up)

5. **Monitor logs:**
   ```bash
   railway logs --follow
   ```

---

## 🎓 Advanced Configuration

### **Custom Domain:**
1. Go to Railway dashboard
2. Click your project → "Settings"
3. Scroll to "Domains"
4. Click "Add Domain"
5. Enter your domain and follow DNS setup

### **Environment-Specific Variables:**
Railway supports multiple environments:
```bash
railway environment create production
railway environment create staging
```

### **Health Checks:**
Railway automatically monitors your app at `/health` endpoint (already implemented in your code).

### **Scaling:**
Railway auto-scales based on traffic. For manual scaling:
- Dashboard → Project → Settings → Resources
- Adjust CPU/RAM/Replicas

---

## 📊 Monitoring

### **View Metrics:**
- Go to Railway dashboard
- Click your project
- View CPU, RAM, Network usage in real-time

### **Logs:**
```bash
# Live logs
railway logs --follow

# Last 100 lines
railway logs --tail 100

# Filter errors
railway logs | grep ERROR
```

### **Alerts:**
Set up in Dashboard → Project → Settings → Notifications

---

## 🔒 Security

**Environment Variables:**
- Never commit secrets to Git
- Use Railway variables for all sensitive data
- GEMINI_API_KEY, API_KEY should only be in Railway

**API Security:**
- Your API requires `x-api-key` header (already implemented)
- Use strong API keys
- Change API_KEY regularly

---

## 🆘 Support

**Railway Documentation:** https://docs.railway.app/

**Discord Community:** https://discord.gg/railway

**Status Page:** https://status.railway.app/

**Project Issues:** https://github.com/0x-rudra/hcl-honeypot/issues

---

## ✨ Why Railway.app?

✅ **No Credit Card Required** - Start deploying immediately
✅ **Zero Cold Starts** - Always responsive, unlike serverless platforms
✅ **GitHub Integration** - Auto-deploy on git push
✅ **Simple Setup** - Deploy in 3 clicks
✅ **Developer-Friendly** - Easy CLI, great dashboard
✅ **Free Tier** - $5 credit/month for hobby projects
✅ **Auto HTTPS** - Instant SSL certificates
✅ **Live Logs** - Real-time debugging
✅ **No Configuration** - Works with your existing code

---

## 🚀 Quick Setup Checklist

- [ ] Sign up at Railway.app with GitHub
- [ ] Create new project from GitHub repo
- [ ] Add GEMINI_API_KEY environment variable
- [ ] Add API_KEY environment variable
- [ ] Add PORT=8000 environment variable
- [ ] Generate domain
- [ ] Test API endpoint
- [ ] Submit URL to hackathon tester

---

**🎉 Deployment Complete!**

Your HCL Honeypot API is now live at:
```
https://your-app.up.railway.app/honeypot
```

Railway will auto-deploy whenever you push to GitHub!

**No cold starts, no timeouts, always ready! 🚂**
