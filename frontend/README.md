# AdaptiveTrader Frontend

Simple dashboard to test CMC API integration and trading signals in real-time.

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Deploy to Vercel

### Option 1: Vercel CLI

```bash
npm install -g vercel
cd frontend
vercel
```

### Option 2: GitHub Integration

1. Push frontend folder to GitHub
2. Go to https://vercel.com
3. Import your repository
4. Set root directory to `frontend`
5. Deploy

## Environment Variables

Set in Vercel dashboard:
- `BACKEND_API`: Your VPS API URL (http://195.26.240.233:8000)

## Backend Setup

Run Python API on VPS:

```bash
cd /home/hermes/bnb-hackathon-track2
pip install fastapi uvicorn
python api_server.py
```

This will start API server on http://195.26.240.233:8000
