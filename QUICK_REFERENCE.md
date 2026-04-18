# SNAP Food Shop - Quick Reference Guide

## 🚀 30-Second Quick Start

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python dummy_data_generator.py  # Creates fake data
python main.py                   # Starts API on http://localhost:8000

# Frontend (new terminal)
npm create vite frontend -- --template react
cd frontend && npm install && npm run dev  # Starts on http://localhost:5173
```

---

## 📋 What You Have Right Now

| File | What It Does | Key Info |
|------|-------------|----------|
| `dummy_data_generator.py` | Creates 50 realistic users, 20 families, 249 orders | Run once to generate `dummy_data.json` |
| `recommendation_engine.py` | The AI/ML brain - all 4 recommendation algorithms | HybridRecommender class is the main entry point |
| `main.py` | FastAPI server with REST endpoints | 15+ endpoints, auto-loads dummy data |
| `tech_stack_recommendation.md` | Explains which tools to use and why | Reference for decision-making |
| `DEPLOYMENT_GUIDE.md` | Step-by-step to get live on internet | Railway + Vercel instructions |
| `PROJECT_SUMMARY.md` | Architecture diagrams and data flows | Visual understanding of system |
| `dummy_data.json` | Test data (50 users, foods, orders) | Auto-generated, do not edit |

---

## 🔑 Key Concepts

### The 4 Recommendation Algorithms
1. **Content-Based** (40% weight) - "Fill your nutrition gaps"
2. **Collaborative** (30% weight) - "People like you buy this"
3. **Knowledge-Based** (filtering) - "Your doctor says avoid this"
4. **Optimization** (budget) - "Best nutrition per dollar"

### Core Classes
```python
# Recommendation engine
from recommendation_engine import HybridRecommender

recommender = HybridRecommender(users, orders, food_catalog)
recs = recommender.get_personalized_recommendations(user)
recs = recommender.get_family_recommendations(family)
```

---

## 🔌 API Endpoints (All Working!)

### Get Recommendations
```bash
# Individual
curl -X POST http://localhost:8000/api/recommendations/individual \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_0001",
    "num_recommendations": 15,
    "scope": "individual"
  }'

# Family
curl -X POST http://localhost:8000/api/recommendations/family \
  -H "Content-Type: application/json" \
  -d '{
    "family_id": "family_user_0002",
    "num_recommendations": 20
  }'
```

### Get User Profile
```bash
curl http://localhost:8000/api/users/user_0001
```

### Get Foods by Category
```bash
curl "http://localhost:8000/api/foods?category=vegetables"
```

### Get Analytics
```bash
curl http://localhost:8000/api/stats/summary
curl http://localhost:8000/api/stats/popular-foods
curl http://localhost:8000/api/stats/average-order-value
```

### Full API Docs
```
http://localhost:8000/docs  # Interactive Swagger UI
http://localhost:8000/openapi.json  # Raw spec
```

---

## 📊 Sample API Responses

### Recommendation Response
```json
{
  "user_id": "user_0001",
  "user_name": "Michelle Garcia",
  "recommendations": [
    {
      "name": "Carrots (1 lb)",
      "category": "vegetables",
      "price": 0.89,
      "score": 817.81,
      "reason": "Fills calories, protein, fiber",
      "nutrition": {
        "calories": 176,
        "protein": 4,
        "fiber": 9
      }
    }
  ],
  "summary": {
    "total_recommendations": 15,
    "estimated_cost": 42.50,
    "budget": 100.00
  }
}
```

### User Profile Response
```json
{
  "id": "user_0001",
  "name": "Michelle Garcia",
  "age": 32,
  "gender": "female",
  "monthly_budget": 100,
  "health_conditions": [],
  "nutritional_needs": {
    "calories": 1800,
    "protein": 46,
    "fiber": 25,
    "calcium": 1000,
    "iron": 18
  }
}
```

---

## 🛠️ Common Tasks

### Add a New Food to Catalog
```python
# Edit dummy_data_generator.py, add to FOOD_CATALOG list:
{
    'name': 'Salmon (8 oz)', 
    'category': 'protein', 
    'price': 6.99,
    'nutrition': {
        'calories': 280, 'protein': 36, 'fiber': 0,
        'calcium': 12, 'iron': 1.5, 'vitamin_c': 0, 'vitamin_a_rae': 174
    }
}

# Regenerate data
python dummy_data_generator.py
```

### Change a User's Budget
```python
# Edit dummy_data.json or update in code:
user['monthly_budget'] = 150  # Change from whatever it was
```

### Add a Health Condition
```python
# Edit HEALTH_CONDITIONS list in dummy_data_generator.py:
HEALTH_CONDITIONS = ['diabetes', 'hypertension', ..., 'new_condition']

# Add rules in recommendation_engine.py:
DIETARY_RULES = {
    'new_condition': {
        'avoid': ['food1', 'food2'],
        'encourage': ['food3', 'food4']
    }
}
```

### Test Recommendations Locally
```bash
# Python shell
python
>>> from recommendation_engine import HybridRecommender
>>> import json
>>> with open('dummy_data.json') as f: data = json.load(f)
>>> rec = HybridRecommender(data['users'], data['orders'], data['foods'])
>>> result = rec.get_personalized_recommendations(data['users'][0])
>>> print(result['recommendations'][0])
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` |
| `MongoDB connection failed` | Check `.env` file has correct connection string |
| `Port 8000 already in use` | Change port: `uvicorn main:app --port 8001` |
| `CORS errors in frontend` | Add frontend URL to `CORS_ORIGINS` in `main.py` |
| `No data in MongoDB` | Run `python dummy_data_generator.py` first |
| `Empty recommendations returned` | Check user exists: `curl http://localhost:8000/api/users/user_0001` |

---

## 📱 Frontend Integration

### Call Recommendation API from React
```javascript
// In React component
const fetchRecommendations = async (userId) => {
  const response = await fetch('http://localhost:8000/api/recommendations/individual', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      num_recommendations: 15,
      scope: 'individual'
    })
  });
  const data = await response.json();
  console.log(data.recommendations);
};
```

---

## 📈 Scoring Algorithm Explained

```
For each food item:
  1. Gap Fill Score = How much nutrition you're missing × nutrition in food
  2. Cost-Value Score = Total nutrition ÷ Price
  3. Similarity Score = How close food matches your diet profile
  
  Final Score = (Gap × 0.4) + (CostValue × 0.35) + (Similarity × 0.25)
  
Example:
  Carrots: Gap=800, CostValue=1.2, Similarity=0.8
  Score = (800 × 0.4) + (1.2 × 0.35) + (0.8 × 0.25)
        = 320 + 0.42 + 0.2 = 320.62
```

---

## 💾 Database Schema

### users collection
```javascript
{
  _id: ObjectId,
  id: "user_0001",
  name: "Michelle Garcia",
  age: 32,
  gender: "female",
  monthly_budget: 100,
  zip_code: "20001",
  health_conditions: ["diabetes"],
  nutritional_needs: {
    calories: 1800,
    protein: 46,
    fiber: 25,
    ...
  },
  created_date: "2025-11-27T18:31:27"
}
```

### foods collection
```javascript
{
  _id: ObjectId,
  name: "Carrots (1 lb)",
  category: "vegetables",
  price: 0.89,
  nutrition: {
    calories: 176,
    protein: 4,
    fiber: 9,
    calcium: 96,
    iron: 1.2,
    vitamin_c: 21,
    vitamin_a_rae: 1911
  }
}
```

### orders collection
```javascript
{
  _id: ObjectId,
  id: "order_00001",
  user_id: "user_0001",
  family_id: null,
  items: [
    { name: "Carrots (1 lb)", price: 0.89 },
    { name: "Broccoli (1 lb)", price: 1.49 }
  ],
  total: 2.38,
  order_date: "2025-12-06T18:31:27"
}
```

### recommendations collection
```javascript
{
  _id: ObjectId,
  user_id: "user_0001",
  recommendations: [
    {
      name: "Carrots (1 lb)",
      category: "vegetables",
      price: 0.89,
      score: 817.81,
      reason: "Fills calories, protein, fiber"
    }
  ],
  dietary_restrictions: ["diabetes"],
  generated_at: "2025-12-07T10:00:00"
}
```

---

## 🚢 Deployment Commands

### Deploy Backend to Railway
```bash
# 1. Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 3. In Railway dashboard:
# - Connect GitHub repo
# - Set environment variables (MONGODB_URI)
# - Deploy (automatic on push)
```

### Deploy Frontend to Vercel
```bash
# 1. Create Vite project
npm create vite frontend -- --template react

# 2. Push to GitHub
git add .
git commit -m "Frontend"
git push origin main

# 3. In Vercel:
# - Import project from GitHub
# - Set VITE_API_URL environment variable
# - Deploy
```

---

## 🧪 Testing the System

### Test 1: Get a User
```bash
curl http://localhost:8000/api/users/user_0001
```

### Test 2: Get Recommendations
```bash
curl -X POST http://localhost:8000/api/recommendations/individual \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_0001","num_recommendations":5}'
```

### Test 3: Get Foods
```bash
curl "http://localhost:8000/api/foods?category=vegetables"
```

### Test 4: Get Stats
```bash
curl http://localhost:8000/api/stats/summary
```

---

## 📚 Documentation Files to Read

1. **Start here:** `DEPLOYMENT_GUIDE.md` (how to set up)
2. **For architecture:** `PROJECT_SUMMARY.md` (diagrams & overview)
3. **For tools:** `tech_stack_recommendation.md` (why each tool)
4. **For code:** Read comments in `.py` files (well-documented)

---

## 🎯 Hackathon Tips

1. **Show the AI working** - Demo recommendations in action
2. **Explain the algorithm** - Judges love understanding the "why"
3. **Show real data** - Use USDA data, not fake numbers
4. **Mobile-friendly** - Make UI work on phones
5. **Mention impact** - How many families could this help?
6. **Future vision** - What's next? (food truck features, merchant dashboard)

---

## 📞 Quick Help

```
"I don't know Python"
→ Copy/paste the code, follow DEPLOYMENT_GUIDE.md exactly

"API not responding"
→ Check if python main.py is running, check port 8000

"MongoDB failing"
→ Check .env file, verify connection string, check IP whitelist

"Recommendations look wrong"
→ Check user_id exists, verify dummy_data.json loaded

"Frontend not calling API"
→ Check CORS_ORIGINS in main.py, check fetch URL in React
```

---

## 🔗 Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com
- MongoDB: https://cloud.mongodb.com
- Railway: https://railway.app
- Vercel: https://vercel.com
- React: https://react.dev
- USDA Food Data: https://fdc.nal.usda.gov/api

---

## 📊 Your Data at a Glance

From `dummy_data.json`:
- **50 Users** with realistic profiles
- **20 Families** with multiple members
- **249 Orders** of historical purchases
- **23 Foods** with complete USDA nutrition data
- **10 Users** with health conditions (20% with diabetes, hypertension, etc.)

---

## ✨ Final Checklist Before Judging

- [ ] Run `python dummy_data_generator.py`
- [ ] Run `python main.py` (backend works)
- [ ] Test API endpoints (with curl or Postman)
- [ ] Run React frontend
- [ ] Make recommendation request in frontend
- [ ] Verify results are showing
- [ ] Check that math makes sense (budget, nutrition)
- [ ] Explain algorithm to judges

---

**You're ready to build! 🚀**

All the infrastructure is set up. Now focus on:
1. Making the UI beautiful
2. Explaining your algorithm clearly
3. Showing real impact for real people
4. Demonstrating the business model (merchant side)

Good luck! 💪
