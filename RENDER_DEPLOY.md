# Material Delivery Dashboard - Render Deployment Guide

## Quick Deploy to Render

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub account

### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `pranavkithkin/Material-schedules`
3. Configure:
   - **Name**: `material-delivery-dashboard` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Environment Variables (Optional)
Add in Render dashboard → Environment:
```
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///delivery_dashboard.db
FLASK_DEBUG=False
```

### 4. Deploy
- Click **"Create Web Service"**
- Wait 2-3 minutes for deployment
- Your app will be live at: `https://material-delivery-dashboard.onrender.com`

### 5. Initialize Database
After first deploy, go to Shell tab in Render and run:
```bash
python init_db.py --with-samples -y
```

## Features Deployed
✅ Material tracking (35 types)
✅ Purchase orders management
✅ Payment tracking
✅ Delivery schedule monitoring
✅ AI suggestions system
✅ Document upload system
✅ PKP Engineering branding

## Demo Login
No authentication required - direct access to dashboard

## Notes
- Free tier: App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Database persists between deployments
- Uploads stored in `/static/uploads/` (will reset on redeploy on free tier)

## Support
For issues, check Render logs in dashboard
