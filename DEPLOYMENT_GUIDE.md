# SNAP Food Shop - Deployment & Setup Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 16+ 
- MongoDB Atlas account (free tier)
- Git

---

## PART 1: BACKEND SETUP (Python + FastAPI + MongoDB)

### Step 1: Clone/Create Project Structure

```bash
# Create project directory
mkdir snap-food-shop
cd snap-food-shop

# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.0
uvicorn[standard]==0.24.0
pymongo==4.6.0
pandas==2.1.1
scikit-learn==1.3.2
numpy==1.24.3
python-dotenv==1.0.0
pydantic==2.4.2
apscheduler==3.10.4
requests==2.31.0
EOF

# Install all packages
pip install -r requirements.txt
```

### Step 3: MongoDB Atlas Setup

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create new project → Create database
4. Choose "Free" tier (M0)
5. Select region closest to DC (e.g., us-east-1)
6. Create database user:
   - Username: `snap_user`
   - Password: (auto-generate strong password)
7. Add IP address to whitelist (use 0.0.0.0/0 for testing, restrict in production)
8. Click "Connect" → "Drivers" → Copy connection string

Example:
```
mongodb+srv://snap_user:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### Step 4: Configure Environment

```bash
# Create .env file in backend directory
cat > .env << 'EOF'
MONGODB_URI=mongodb+srv://snap_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=snap_food_shop
ENVIRONMENT=development
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# NEVER commit .env file - add to .gitignore
echo ".env" >> .gitignore
```

### Step 5: Copy Application Files

```bash
# Copy the three Python files to backend/
# - dummy_data_generator.py
# - recommendation_engine.py
# - main.py
```

### Step 6: Generate Dummy Data

```bash
python dummy_data_generator.py

# Output should show:
# ✓ Dummy data exported to dummy_data.json
#   - Users: 50
#   - Families: 20
#   - Order History: 249
#   - Food Catalog: 23
```

### Step 7: Start Development Server

```bash
# From backend directory
python main.py

# Server starts at http://localhost:8000
# API Docs at http://localhost:8000/docs (Swagger UI)
```

### Step 8: Verify Installation

```bash
# In another terminal, test the API
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "api": "running",
#   "database": "connected",
#   "timestamp": "2024-04-18T..."
# }
```

---

## PART 2: FRONTEND SETUP (React + Vite)

### Step 1: Create React App

```bash
# From project root (snap-food-shop/)
npm create vite@latest frontend -- --template react

# Navigate to frontend
cd frontend

# Install dependencies
npm install
npm install axios recharts react-router-dom
```

### Step 2: Create API Configuration

```bash
# Create src/config/api.js
mkdir -p src/config

cat > src/config/api.js << 'EOF'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json();
  },
};
EOF
```

### Step 3: Create Sample Components

```bash
# Create src/pages/RecommendationsPage.jsx
mkdir -p src/pages

cat > src/pages/RecommendationsPage.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { apiClient } from '../config/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RecommendationsPage() {
  const [userId, setUserId] = useState('user_0001');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const data = await apiClient.post('/recommendations/individual', {
        user_id: userId,
        num_recommendations: 15,
        scope: 'individual',
      });
      setRecommendations(data);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Personalized Food Recommendations</h1>
      
      <div className="mb-6">
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter user ID (e.g., user_0001)"
          className="px-4 py-2 border rounded-lg w-full md:w-1/3 mb-3"
        />
        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {recommendations && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Recommendations for {recommendations.user_name}</h2>
          <p className="text-gray-600 mb-4">Budget: ${recommendations.budget} | Scope: {recommendations.scope}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.recommendations.map((rec, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:shadow-lg transition">
                <h3 className="font-bold text-lg">{rec.name}</h3>
                <p className="text-sm text-gray-600">{rec.category}</p>
                <p className="text-lg font-semibold mt-2">${rec.price}</p>
                <p className="text-sm text-blue-600 mt-2">{rec.reason}</p>
                <p className="text-xs text-gray-500 mt-2">Score: {rec.score.toFixed(0)}</p>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-100 rounded-lg">
            <h3 className="font-bold mb-2">Summary</h3>
            <p>Total Items: {recommendations.summary.total_recommendations}</p>
            <p>Estimated Cost: ${recommendations.summary.estimated_cost}</p>
          </div>
        </div>
      )}
    </div>
  );
}
EOF
```

### Step 4: Create Environment File

```bash
# Create .env.local in frontend/
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000/api
EOF
```

### Step 5: Start Frontend Dev Server

```bash
# From frontend/ directory
npm run dev

# Server starts at http://localhost:5173
```

---

## PART 3: DEPLOYMENT TO CLOUD

### Option A: Deploy Backend to Railway.app (Recommended)

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Connect Repository**
   - Link your GitHub repo (ensure code is pushed)
   - Railway auto-detects Python project

3. **Configure Environment**
   - In Railway dashboard → Project → Variables
   - Add: `MONGODB_URI` (from MongoDB Atlas)
   - Add: `ENVIRONMENT=production`

4. **Deploy**
   ```bash
   # Railway auto-deploys on git push
   # View logs: Railway Dashboard → Logs
   # Your API is live at: https://your-project.railway.app
   ```

### Option B: Deploy Backend to Heroku (Alternative)

1. **Install Heroku CLI**
   ```bash
   curl https://cli.heroku.com/install.sh | sh
   ```

2. **Create Procfile**
   ```bash
   # In backend/ directory
   echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create snap-food-shop-api
   heroku config:set MONGODB_URI="your_connection_string"
   git push heroku main
   ```

### Deploy Frontend to Vercel

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to https://vercel.com
   - Click "Import Project"
   - Select GitHub repo
   - Configure:
     - Framework: Vite (auto-detected)
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **Add Environment Variable**
   - In Vercel dashboard → Settings → Environment Variables
   - Add: `VITE_API_URL=https://your-railway-api.railway.app/api`
   - Redeploy

4. **Your frontend is live at:** `https://your-project.vercel.app`

---

## PART 4: ENVIRONMENT VARIABLES SUMMARY

### Backend (.env)
```
MONGODB_URI=mongodb+srv://snap_user:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=snap_food_shop
ENVIRONMENT=development|production
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend.vercel.app
```

### Frontend (.env.local or Vercel)
```
VITE_API_URL=http://localhost:8000/api  # Local
VITE_API_URL=https://your-api.railway.app/api  # Production
```

---

## PART 5: API ENDPOINTS REFERENCE

### Base URL
- Local: `http://localhost:8000`
- Production: `https://your-railway-api.railway.app`

### Health & Info
- `GET /` - API information
- `GET /health` - System health check

### Users
- `GET /api/users` - List all users
- `GET /api/users/{user_id}` - Get user details
- `GET /api/users?skip=0&limit=10` - Paginated list

### Families
- `GET /api/families` - List all families
- `GET /api/families/{family_id}` - Get family details

### Foods
- `GET /api/foods` - List foods
- `GET /api/foods?category=vegetables` - Filter by category
- `GET /api/foods/categories` - List available categories

### Recommendations (CONSUMER)
```
POST /api/recommendations/individual
{
  "user_id": "user_0001",
  "current_nutrition": {"calories": 500, ...},  // optional
  "num_recommendations": 15,
  "scope": "individual"
}
```

```
POST /api/recommendations/family
{
  "family_id": "family_user_0002",
  "num_recommendations": 20
}
```

### Orders
- `GET /api/orders/user/{user_id}` - User's order history
- `POST /api/orders` - Create new order

### Analytics
- `GET /api/stats/summary` - Overall statistics
- `GET /api/stats/popular-foods?limit=10` - Top purchased foods
- `GET /api/stats/average-order-value` - Order value stats

---

## PART 6: TROUBLESHOOTING

### MongoDB Connection Failed
```
Error: Failed to connect to MongoDB

Solution:
1. Check connection string in .env
2. Verify IP whitelist in MongoDB Atlas (add 0.0.0.0/0 for testing)
3. Check username/password (no special chars without URL encoding)
4. Ensure database exists in MongoDB Atlas
```

### CORS Errors
```
Error: Access to XMLHttpRequest has been blocked by CORS policy

Solution:
1. Add frontend URL to CORS_ORIGINS in backend .env
2. Redeploy backend
3. For local dev, use http://localhost:5173
```

### Import Errors
```
Error: No module named 'recommendation_engine'

Solution:
1. Ensure all .py files are in same directory
2. Check Python import paths
3. Run: pip install -e . (if in package)
```

### Database Empty
```
Error: No users/foods returned from API

Solution:
1. Run: python dummy_data_generator.py
2. Check MongoDB: db.users.count_documents({})
3. Verify collections exist in MongoDB Atlas
```

---

## PART 7: MONITORING & MAINTENANCE

### Check API Health
```bash
curl https://your-api.railway.app/health
```

### View Logs
- Railway: Dashboard → Logs
- Heroku: `heroku logs --tail`
- Local: Console output

### Database Backups
- MongoDB Atlas auto-backs up to M1+ tier
- For M0, manually export using:
```bash
mongoexport --uri "mongodb+srv://..." --collection users --out users_backup.json
```

### Performance Monitoring
- Monitor recommendation generation time
- Track most-requested endpoints
- Monitor database query performance

---

## PART 8: NEXT STEPS FOR PRODUCTION

1. **Add Authentication**
   - Implement JWT tokens
   - Add Auth0 integration
   - Secure sensitive endpoints

2. **Scale Database**
   - Upgrade MongoDB to M2+ tier
   - Implement caching (Redis)
   - Add database indexes

3. **Add Logging & Monitoring**
   - Implement Sentry for error tracking
   - Add Prometheus for metrics
   - Create Grafana dashboards

4. **Enhance ML Model**
   - Collect more user data
   - Retrain models weekly
   - A/B test recommendation strategies

5. **Add More Features**
   - User feedback system
   - Nutrition tracking
   - Barcode scanning
   - Mobile app

---

## USEFUL COMMANDS

```bash
# Backend
python -m pytest tests/  # Run tests
python main.py  # Start dev server
pip freeze > requirements.txt  # Export dependencies

# Frontend
npm run build  # Build for production
npm run preview  # Preview production build
npm run lint  # Check code quality

# Git
git add .
git commit -m "message"
git push origin main
```

---

## COST SUMMARY

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| MongoDB Atlas | M0 (Free) | $0 | Upgrade to M2 for production |
| Railway | Free Tier | $0 | $5 free credit/month, then $0.50/hour |
| Vercel | Free | $0 | Unlimited deployments |
| Domain (optional) | | $10-15/yr | Namecheap, GoDaddy |
| **TOTAL** | | **$0-50** | Very affordable! |

---

## SUPPORT & RESOURCES

- MongoDB Docs: https://docs.mongodb.com
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

---

You're ready to launch! 🚀
