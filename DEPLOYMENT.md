# 🚀 Deploy to Render

This guide walks you through deploying your Honeypot API to Render.com for free.

---

## 📋 Prerequisites

1. A [Render.com](https://render.com) account (sign up with GitHub)
2. Your GitHub repository pushed: `https://github.com/0x-rudra/hcl-honeypot`
3. Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

---

## 🎯 Deployment Steps

### **Method 1: One-Click Deploy (Recommended)**

1. **Go to Render Dashboard:**
   - Visit [https://dashboard.render.com](https://dashboard.render.com)
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository:**
   - Select **"Build and deploy from a Git repository"**
   - Click **"Connect account"** (if first time)
   - Find and select: `0x-rudra/hcl-honeypot`
   - Click **"Connect"**

3. **Configure Service:**
   ```
   Name: hcl-honeypot-api
   Region: Oregon (US West)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Add Environment Variables:**
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Add these variables:
     ```
     GEMINI_API_KEY = your-gemini-api-key-here
     HONEYPOT_API_KEY = honeypot-test-key-2026-secure
     PYTHON_VERSION = 3.13.0
     ```

5. **Deploy:**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for build and deployment
   - Your API will be live at: `https://hcl-honeypot-api.onrender.com`

---

### **Method 2: Deploy from render.yaml (Blueprint)**

1. **Go to Render Dashboard:**
   - Visit [https://dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
   - Click **"New Blueprint Instance"**

2. **Connect Repository:**
   - Select your GitHub repository: `0x-rudra/hcl-honeypot`
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables:**
   - Set `GEMINI_API_KEY` to your actual API key
   - Keep `HONEYPOT_API_KEY` as default or customize

4. **Deploy:**
   - Click **"Apply"**
   - Render will deploy using blueprint configuration

---

## ✅ Verify Deployment

### **1. Check Health Endpoint:**
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1738617600.0,
  "gemini_configured": true,
  "active_sessions": 0
}
```

### **2. Test API Endpoint:**
```bash
curl -X POST https://your-app-name.onrender.com/honeypot \
  -H "x-api-key: honeypot-test-key-2026-secure" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your account blocked! Call 9876543210 urgently"}'
```

### **3. View Logs:**
- In Render Dashboard → Your Service → **"Logs"** tab
- Monitor requests and responses in real-time

---

## 🔧 Configuration

### **Environment Variables (Required):**

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `HONEYPOT_API_KEY` | Your API authentication key | `honeypot-test-key-2026-secure` |
| `PYTHON_VERSION` | Python version | `3.13.0` |

### **Update Environment Variables:**
1. Render Dashboard → Your Service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Enter key-value pairs
4. Click **"Save Changes"** (auto-redeploys)

---

## 📊 Monitoring

### **View Metrics:**
- Dashboard → Your Service → **"Metrics"** tab
- Monitor: CPU, Memory, Response time, Request count

### **View Logs:**
- Dashboard → Your Service → **"Logs"** tab
- Real-time log streaming
- Filter by log level (INFO, ERROR, etc.)

### **Alerts:**
- Dashboard → Your Service → **"Settings"** → **"Notifications"**
- Set up email/Slack alerts for downtime

---

## ⚙️ Important Notes

### **Free Tier Limitations:**
- ✅ 750 hours/month (enough for 24/7 operation)
- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ Cold start takes ~30 seconds
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS with custom domains

### **Keeping Service Awake (Optional):**
If you need to prevent spin-down, use a service like:
- **UptimeRobot** (free): Pings your API every 5 minutes
- **Cron-job.org** (free): Scheduled health checks

Setup:
1. Create account on UptimeRobot
2. Add new monitor: `https://your-app-name.onrender.com/health`
3. Set interval: 5 minutes

---

## 🔄 Auto-Deploy from GitHub

Every push to `main` branch triggers automatic redeployment:

```bash
# Make changes locally
git add .
git commit -m "Update API"
git push origin main

# Render automatically deploys in ~5 minutes
```

### **Disable Auto-Deploy:**
- Dashboard → Your Service → **"Settings"**
- Toggle **"Auto-Deploy"** off

---

## 🌐 Custom Domain (Optional)

### **Add Custom Domain:**
1. Dashboard → Your Service → **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain: `api.yourdomain.com`
4. Add DNS records from Render to your domain registrar:
   ```
   Type: CNAME
   Name: api
   Value: your-app-name.onrender.com
   ```
5. Wait for DNS propagation (~10 minutes)

---

## 🐛 Troubleshooting

### **Build Fails:**
- Check **"Logs"** tab for error messages
- Verify `requirements.txt` is valid
- Ensure Python version matches `runtime.txt`

### **Service Crashes:**
- Check **"Logs"** for error traces
- Verify `GEMINI_API_KEY` is set correctly
- Test locally first: `uvicorn app.main:app`

### **Slow Response:**
- First request after spin-down takes ~30s (cold start)
- Use UptimeRobot to keep service warm
- Consider upgrading to paid plan ($7/month) for always-on

### **API Key Issues:**
- Verify `HONEYPOT_API_KEY` environment variable is set
- Check logs for "API key validated successfully" messages
- Test with curl command from verification section

---

## 📱 Get Your API URL

After deployment, your API will be available at:
```
https://hcl-honeypot-api.onrender.com
```

**Update your evaluation submission with this URL!**

---

## 🔒 Security Best Practices

1. **Change Default API Key:**
   ```
   HONEYPOT_API_KEY=your-secure-random-key-here
   ```

2. **Keep Gemini Key Secret:**
   - Never commit API keys to GitHub
   - Use Render's environment variables

3. **Monitor Usage:**
   - Check logs regularly for suspicious activity
   - Set up alerts for errors

---

## 💰 Upgrade Options

If you need better performance:

| Plan | Cost | Benefits |
|------|------|----------|
| Free | $0 | Spin-down after 15min, 750hrs/month |
| Starter | $7/month | Always-on, faster builds, 1 GB RAM |
| Standard | $25/month | 4 GB RAM, priority support |

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **GitHub Issues:** https://github.com/0x-rudra/hcl-honeypot/issues

---

## ✅ Deployment Checklist

- [ ] GitHub repository pushed with latest code
- [ ] Gemini API key obtained
- [ ] Render account created
- [ ] Service deployed from render.yaml
- [ ] Environment variables configured
- [ ] Health endpoint returns "healthy"
- [ ] Test API with sample scam message
- [ ] Logs showing no errors
- [ ] URL shared with evaluation team

---

**Your API is now live and ready for evaluation! 🎉**
