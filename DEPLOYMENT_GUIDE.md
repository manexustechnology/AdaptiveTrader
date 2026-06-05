# 🚀 DEPLOYMENT GUIDE - AdaptiveTrader Dashboard

## RINGKASAN PROJECT

✅ **Backend API**: FastAPI server running on VPS (195.26.240.233:8000)
✅ **Frontend Dashboard**: Next.js app (deploy ke Vercel)
✅ **Integration**: Real CMC API dengan live market data testing

---

## 📋 PART 1: BACKEND API (VPS)

### Status: ✅ RUNNING on http://195.26.240.233:8000

API sudah running di VPS dengan endpoints:
- `GET /` - API info
- `GET /health` - Health check  
- `GET /api/signal/{symbol}` - Generate trading signal (BTC, ETH, etc)

### Test API:
```bash
curl http://195.26.240.233:8000/health
curl http://195.26.240.233:8000/api/signal/BTC
```

### Start API (if not running):
```bash
cd /home/hermes/bnb-hackathon-track2
python api_server.py
```

### Run as systemd service (persistent):
```bash
sudo nano /etc/systemd/system/adaptivetrader-api.service
```

Paste:
```ini
[Unit]
Description=AdaptiveTrader API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/hermes/bnb-hackathon-track2
Environment="CMC_API_KEY=2d36e231e7fb4dadaf52fd00e26aee4b"
ExecStart=/root/.pyenv/shims/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable adaptivetrader-api
sudo systemctl start adaptivetrader-api
sudo systemctl status adaptivetrader-api
```

---

## 📋 PART 2: FRONTEND (VERCEL)

### Option A: Deploy via Vercel CLI (RECOMMENDED)

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy**:
```bash
cd /home/hermes/bnb-hackathon-track2/frontend
vercel
```

3. **Follow prompts**:
   - Login to Vercel account
   - Setup project (accept defaults)
   - Deploy!

4. **Set environment variable**:
```bash
vercel env add BACKEND_API
# Enter: http://195.26.240.233:8000
```

5. **Re-deploy with env**:
```bash
vercel --prod
```

### Option B: Deploy via GitHub + Vercel Dashboard

1. **Push frontend to GitHub**:
```bash
cd /home/hermes/bnb-hackathon-track2
git add frontend/
git commit -m "add frontend dashboard"
git push origin main
```

2. **Go to https://vercel.com/new**

3. **Import GitHub repository**: `manexustechnology/AdaptiveTrader`

4. **Configure project**:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)

5. **Environment Variables** (add in settings):
   - Key: `BACKEND_API`
   - Value: `http://195.26.240.233:8000`

6. **Deploy!**

---

## 📋 PART 3: LOCAL TESTING (Optional)

Test frontend locally sebelum deploy:

```bash
cd /home/hermes/bnb-hackathon-track2/frontend
npm install
npm run dev
```

Open: http://localhost:3000

---

## 🎯 PART 4: ISI FORM SUBMISSION

Sekarang Anda bisa isi form hackathon dengan informasi berikut:

### **Need teammates?**
```
☑️ No
```

### **Ask hackers questions** (Contact)
```
Telegram: @manexustech
Email: dev@manexus.tech
```
*(ganti dengan contact sebenarnya)*

### **Ask BUIDLers questions** (Contact)
```
Same as above
```

### **Share your agent address** (Track 1 only)
```
N/A - Track 2 submission (Strategy Skills)
```

### **Project Website URL**
Setelah deploy Vercel, masukkan:
```
https://adaptive-trader-xxxx.vercel.app
```
*(URL akan muncul setelah deployment)*

### **GitHub Repository**
```
https://github.com/manexustechnology/AdaptiveTrader
```

### **Demo Video** (buat nanti)
Upload ke YouTube/Loom, paste link

---

## ✅ CHECKLIST

- [x] Backend API running on VPS (195.26.240.233:8000)
- [ ] Frontend deployed to Vercel
- [ ] Tested frontend dashboard (input BTC → shows live data)
- [ ] Form submission complete dengan URL dashboard
- [ ] Demo video created (3-5 minutes)

---

## 🎬 DEMO VIDEO CONTENT (when ready)

Record 3-5 minute video showing:

1. **Dashboard Overview** (30s)
   - Open deployed website
   - Explain what it does

2. **Live CMC Testing** (2 min)
   - Input "BTC" → show real price, regime, signal
   - Input "ETH" → show different regime/signal
   - Input "BNB" → show adaptation

3. **Strategy Explanation** (1.5 min)
   - Show STRATEGY_SPEC.md
   - Explain 4 regimes
   - Show adaptive logic

4. **Code Walkthrough** (30s)
   - Show GitHub repo structure
   - Highlight CMC API integration

5. **Closing** (30s)
   - Summarize innovation
   - Thank organizers

---

## 🆘 TROUBLESHOOTING

### API not accessible from Vercel?

1. **Check VPS firewall**:
```bash
sudo ufw allow 8000/tcp
```

2. **Check API is running**:
```bash
curl http://195.26.240.233:8000/health
```

3. **Check CORS** (already enabled in api_server.py)

### Frontend build fails?

1. **Check Node.js version** (needs 18+):
```bash
node --version
```

2. **Clear cache**:
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

---

## 📊 EXPECTED RESULTS

After deployment, dashboard will:
- ✅ Fetch live CMC data in real-time
- ✅ Display market price, volume, market cap
- ✅ Detect market regime (bull/bear/sideways/volatile)
- ✅ Generate trading signals (BUY/SELL/HOLD)
- ✅ Show confidence scores and reasoning
- ✅ Display position sizing and stop loss levels

---

## 🎯 NEXT STEPS

1. Deploy frontend ke Vercel (10 minutes)
2. Test live dashboard dengan BTC/ETH/BNB
3. Submit form hackathon dengan URL dashboard
4. Create demo video (record dashboard + code)
5. Submit to DoraHacks before June 21!

**Good luck! 🚀**
