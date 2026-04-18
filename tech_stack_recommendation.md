# SNAP Benefit Food Shop - Tech Stack & Architecture Guide

## Project Overview
Building an AI/ML-powered recommendation system for a SNAP-like benefit shop with consumer-facing personalized nutrition recommendations and merchant-side inventory management optimization.

---

## PART 1: TECH STACK BY COMPONENT

### 1. **DATABASE** ✓ SELECTED
- **MongoDB Atlas (Starter Kit - $50 budget)**
  - **Purpose:** Store user profiles, family members, order history, nutritional data, food catalog
  - **Collections:**
    - `users` - Customer profiles (age, gender, health conditions, dietary restrictions)
    - `families` - Family compositions with member relationships
    - `orderHistory` - Past purchases for pattern analysis
    - `foodCatalog` - Available foods with nutritional info (USDA data)
    - `recommendations` - Generated recommendations with explanations
    - `inventory` - Current stock at pickup points
  - **Why MongoDB:** Flexible schema (family structures vary), geospatial queries (1-mile radius), quick iterations in hackathon
  - **Cost:** Free tier + $50 starter kit = unlimited development

---

### 2. **BACKEND API & ML ENGINE** (NEEDS SELECTION)
**Option A: Node.js + Express (RECOMMENDED for hackathon)**
- **Purpose:** REST API for consumer app, recommendation engine execution
- **Stack:**
  - `express` - HTTP server
  - `mongoose` - MongoDB ODM
  - `scikit-learn` (via Python bridge) or `ml.js` - ML algorithms
  - `axios` - HTTP requests
  - `dotenv` - Environment config
- **Why:** Fast development, npm ecosystem, easy to deploy

**Option B: Python + FastAPI (RECOMMENDED if ML-heavy)**
- **Purpose:** Better for complex ML pipelines, data science libraries
- **Stack:**
  - `FastAPI` - High-performance API
  - `PyMongo` - MongoDB driver
  - `scikit-learn`, `pandas` - ML and data manipulation
  - `numpy` - Numerical operations
  - `Pydantic` - Data validation
- **Why:** Native ML libraries, better for recommendation algorithms, easier NumPy/Pandas integration
- **Deployment:** Heroku, Railway, Render (free tier options)

**Recommendation:** Use **Python + FastAPI** for better ML capabilities, **Node.js** as secondary for frontend integration if needed.

---

### 3. **RECOMMENDATION ENGINE** (CORE ALGORITHM)

**Algorithm Type: Hybrid Recommendation System**

1. **Collaborative Filtering** 
   - Users similar to target user → their food purchases
   - Tool: `scikit-learn` KNeighborsRegressor
   - Why: Leverages order history patterns

2. **Content-Based Filtering**
   - Match nutritional needs with food nutrition profiles
   - Tool: `scikit-learn` cosine similarity
   - Why: Works even with new users (no order history)

3. **Knowledge-Based Filtering**
   - Rule engine for dietary restrictions, allergies, health conditions
   - Tool: Custom Python rules or `experta` (Python expert system)
   - Why: Captures domain expertise (e.g., diabetics avoid sugar)

4. **USDA Thrifty Food Plan Optimization**
   - Uses USDA data to optimize for cost + nutrition
   - Tool: `pulp` (Python linear programming)
   - Why: Maximizes value for budget-constrained users

**Libraries:**
```
scikit-learn==1.3.0      # ML algorithms
pandas==2.0.0            # Data manipulation
numpy==1.24.0            # Numerical ops
pulp==2.7.0              # Linear optimization
```

---

### 4. **FRONTEND (CONSUMER APP)** (NEEDS SELECTION)

**Option A: React.js (RECOMMENDED)**
- **Purpose:** Interactive UI for personal/family recommendations
- **Stack:**
  - `react` - UI framework
  - `react-router` - Navigation
  - `axios` - API calls
  - `tailwindcss` or `material-ui` - Styling
  - `chart.js` - Nutrition visualizations
- **Why:** Fast, component-based, large ecosystem
- **Deployment:** Vercel (free tier)

**Option B: React Native (Mobile-first)**
- **Purpose:** If mobile app needed for checkout
- **Why:** Cross-platform, matches SNAP use case
- **Deployment:** Expo (free tier)

**Recommendation:** Start with **React web app** for hackathon, add mobile later

---

### 5. **NUTRITION DATA SOURCES** ✓ READY

**Primary Sources:**
1. **USDA FoodData Central API** (FREE)
   - 400,000+ foods with complete nutrition data
   - Endpoint: `https://fdc.nal.usda.gov/api/`
   - Data: Calories, protein, fiber, vitamins, minerals, cost
   - Integration: `requests` library or direct HTTP calls

2. **USDA Thrifty Food Plan 2021** (From USDA link you provided)
   - Age-sex specific caloric needs
   - Cost benchmarks by food category
   - Recommended quantities for balanced diet

3. **USDA MyPlate Guidelines**
   - Food group servings by age/gender
   - Portion recommendations

**Implementation:**
```python
# Fetch nutrition data at startup, cache in MongoDB
# Update monthly with USDA cost-of-food reports
# Pre-compute nutritional completeness scores
```

---

### 6. **DATA PIPELINE & ETL** (NEEDS SELECTION)

**Tool: Python Scripts + Scheduler**
- **Libraries:**
  ```
  apache-airflow==2.7.0    # Orchestration (optional, can use simple cron)
  celery==5.3.0            # Task queuing
  schedule==1.2.0          # Simple scheduler
  ```
- **Purpose:**
  - Daily: Fetch updated USDA pricing data
  - Weekly: Recalculate user recommendations
  - Monthly: Update cost benchmarks
- **Why:** Keep data fresh, scale background jobs

**Simpler Alternative (Hackathon):**
- Use `APScheduler` (lightweight Python scheduler)
- Run on same server as API
- No separate infrastructure needed

---

### 7. **DEPLOYMENT & HOSTING** (NEEDS SELECTION)

| Component | Platform | Cost | Reason |
|-----------|----------|------|--------|
| Backend API | Heroku, Railway, Render | Free tier available | Easy Python/Node deployment |
| Frontend | Vercel, Netlify | Free tier | Optimized for React |
| Database | MongoDB Atlas | $50 starter kit ✓ | Already selected |
| Task Scheduler | Same as Backend | Free | No extra cost |
| Nutrition Data Cache | MongoDB | Included | Use same DB |

**Recommended Stack:**
- Backend: **Railway.app** (free tier, Python native)
- Frontend: **Vercel** (free tier, React native)
- Database: **MongoDB Atlas** (free + $50 kit)
- **Total Cost:** $50 (just MongoDB)

---

### 8. **AUTHENTICATION & SECURITY** (NEEDS SELECTION)

**Option A: Simple JWT (Hackathon)**
```
PyJWT==2.8.0             # JWT token generation
python-dotenv==1.0.0     # Secrets management
```

**Option B: Auth0 / Firebase (Scalable)**
- **Auth0:** Free tier supports 7,000 users
- **Firebase:** Free tier with Realtime Database
- **Why:** Production-ready, handles compliance

**Recommendation for Hackathon:** JWT + environment variables, migrate to Auth0 later

---

### 9. **MONITORING & ANALYTICS** (OPTIONAL)

```
prometheus==0.17.0       # Metrics collection
grafana (free tier)      # Dashboards
sentry-sdk==1.32.0       # Error tracking
```

**Purpose:** Track recommendation accuracy, API performance, usage patterns

---

### 10. **TESTING FRAMEWORK** (NEEDED)

```
pytest==7.4.0            # Unit tests
pytest-cov==4.1.0        # Coverage reporting
hypothesis==6.82.0       # Property-based testing
```

**Why:** ML algorithms need rigorous testing; hypothesis generates edge cases

---

## PART 2: RECOMMENDED COMPLETE TECH STACK

### ✅ FINAL STACK (Hackathon-Ready)

```
FRONTEND:
├── React 18.2 + Vite (fast dev build)
├── TailwindCSS (styling)
├── Recharts (nutrition charts)
└── Vercel (hosting)

BACKEND:
├── Python 3.11 + FastAPI
├── PyMongo for MongoDB
├── scikit-learn + pandas (ML)
├── APScheduler (background tasks)
└── Railway/Render (hosting)

DATABASE:
├── MongoDB Atlas (free tier + $50 starter kit)
├── Collections: users, families, orders, foods, recommendations
└── Geospatial indexes for pickup points

ML/DATA:
├── scikit-learn (algorithms)
├── pandas (data manipulation)
├── pulp (optimization)
├── USDA FoodData Central API
└── Thrifty Food Plan 2021 data

SECURITY:
├── PyJWT (tokens)
├── python-dotenv (env vars)
└── HTTPS/TLS (automatic via hosting platform)

TESTING:
├── pytest + hypothesis
├── Manual testing with Postman
└── Frontend: Jest + React Testing Library
```

---

## PART 3: INSTALLATION & SETUP GUIDE

### Backend Setup (Python + FastAPI)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pymongo pandas scikit-learn numpy pulp python-dotenv apscheduler

# Create .env file
echo "MONGODB_URI=your_connection_string" > .env
echo "API_KEY=your_secret_key" >> .env

# Run development server
uvicorn main:app --reload
```

### Frontend Setup (React + Vite)
```bash
npm create vite@latest snap-shop -- --template react
cd snap-shop
npm install axios recharts

# Run dev server
npm run dev
```

---

## PART 4: DATA FLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                      CONSUMER APP                           │
│  React UI - Input: age, gender, family, budget, restrictions
└────────────────────┬────────────────────────────────────────┘
                     │ (API Call)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Load User Profile from MongoDB                    │  │
│  │ 2. Fetch User's Order History                        │  │
│  │ 3. Run ML Recommendation Engine:                     │  │
│  │    - Content-based: nutrition gaps vs. catalog      │  │
│  │    - Collaborative: similar users' purchases        │  │
│  │    - Knowledge-based: dietary rules                 │  │
│  │    - Optimization: USDA plan + budget constraints   │  │
│  │ 4. Rank & score recommendations                     │  │
│  │ 5. Return top 20 items + explanations              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ (JSON Response)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MONGODB ATLAS DATABASE                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ users: {_id, age, gender, conditions, budget}        │  │
│  │ families: {_id, user_id, members[], relationships}   │  │
│  │ orders: {_id, user_id, items[], date, total}        │  │
│  │ foods: {_id, name, nutrition{}, price, category}    │  │
│  │ recommendations: {_id, user_id, items[], score}      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

BACKGROUND JOB (APScheduler):
  Daily:   Update USDA pricing data
  Weekly:  Recalculate all user recommendations
  Monthly: Process & archive old orders
```

---

## PART 5: COST BREAKDOWN

| Component | Cost | Notes |
|-----------|------|-------|
| MongoDB Atlas | $50 | Starter kit ✓ |
| Backend Hosting | $0 | Railway/Render free tier |
| Frontend Hosting | $0 | Vercel free tier |
| USDA API | $0 | Free tier |
| Domain (optional) | $10/yr | Namecheap, Route53 |
| **TOTAL** | **$50** | Hackathon-ready |

---

## PART 6: ALTERNATIVE TOOLS (If You Want Variations)

### Instead of scikit-learn:
- **XGBoost**: Better for complex patterns
- **LightGBM**: Faster training, smaller model size
- **TensorFlow/Keras**: If using neural networks

### Instead of FastAPI:
- **Django REST Framework**: More batteries-included
- **Flask**: Lightweight alternative
- **Node.js/Express**: If team prefers JavaScript

### Instead of MongoDB:
- **PostgreSQL**: ACID compliance, structured data (but less flexible)
- **Supabase**: PostgreSQL + free tier + real-time
- **Firebase**: Google-managed, built-in auth

### ML Pipeline Instead of APScheduler:
- **Apache Airflow**: Enterprise-grade orchestration
- **Dagster**: Modern, data-aware
- **Prefect**: Cloud-native workflows

---

## NEXT STEPS

1. ✅ **Finalize backend choice:** Python FastAPI (recommended)
2. ✅ **Finalize frontend choice:** React + Vite (recommended)
3. ⏳ **Create dummy user data** (you're about to do this)
4. ⏳ **Implement recommendation algorithm**
5. ⏳ **Build API endpoints**
6. ⏳ **Deploy to Railway + Vercel**
7. ⏳ **Test with real USDA data**

---

## SUMMARY TABLE

| Need | Tool | Why | Cost |
|------|------|-----|------|
| Database | MongoDB Atlas | Flexible schema, free tier + $50 kit | $50 |
| Backend API | Python + FastAPI | ML-native, async, fast | Free |
| Frontend | React + Vite | Modern, fast, large ecosystem | Free |
| ML Algorithms | scikit-learn | Battle-tested, complete | Free |
| Nutrition Data | USDA FoodData Central | Authoritative, free, 400k foods | Free |
| Deployment | Railway/Vercel | Free tier, easy CI/CD | Free |
| Cost Optimization | PuLP | Linear programming for budgets | Free |
| Scheduling | APScheduler | Lightweight background jobs | Free |
| Testing | pytest | Industry standard | Free |
| **TOTAL COST** | | | **$50** |

---

This stack is production-grade, hackathon-ready, and can scale beyond the competition.
