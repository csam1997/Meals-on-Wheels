"""
FastAPI Backend for SNAP Benefit Food Shop
Provides REST API endpoints for consumer and merchant recommendations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = 'snap_food_shop'
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173", "*"]  # Allow local dev

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class NutritionNeeds(BaseModel):
    calories: float
    protein: float
    fiber: float
    calcium: float
    iron: float
    vitamin_c: float
    vitamin_a_rae: float

class FoodItem(BaseModel):
    name: str
    category: str
    price: float
    nutrition: Dict

class UserProfile(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    monthly_budget: float
    health_conditions: List[str] = []
    nutritional_needs: NutritionNeeds

class RecommendationRequest(BaseModel):
    user_id: str
    current_nutrition: Optional[Dict] = None
    num_recommendations: int = 15
    scope: str = "individual"  # individual or family

class FamilyRecommendationRequest(BaseModel):
    family_id: str
    num_recommendations: int = 20

class OrderRequest(BaseModel):
    user_id: str
    items: List[Dict]
    total: float

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="SNAP Food Shop Recommendation API",
    description="AI/ML powered food recommendations for SNAP benefit shoppers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

class MongoDBConnection:
    """Singleton MongoDB connection manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
                cls._instance.client.admin.command('ping')
                cls._instance.db = cls._instance.client[DB_NAME]
                logger.info("✓ Connected to MongoDB")
            except ServerSelectionTimeoutError:
                logger.error("✗ Failed to connect to MongoDB")
                cls._instance.db = None
        
        return cls._instance

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and load data on startup"""
    db_conn = MongoDBConnection()
    
    if db_conn.db is not None:
        # Check if collections exist, if not load dummy data
        collections = db_conn.db.list_collection_names()
        
        if 'users' not in collections:
            logger.info("Loading dummy data into MongoDB...")
            try:
                with open('dummy_data.json', 'r') as f:
                    data = json.load(f)
                
                # Insert data
                db_conn.db['users'].insert_many(data['users'])
                db_conn.db['families'].insert_many(data['families'])
                db_conn.db['orders'].insert_many(data['orders'])
                db_conn.db['foods'].insert_many(data['food_catalog'])
                
                # Create indexes
                db_conn.db['users'].create_index('id')
                db_conn.db['orders'].create_index([('user_id', 1)])
                db_conn.db['families'].create_index([('primary_user_id', 1)])
                db_conn.db['foods'].create_index([('category', 1)])
                
                logger.info("✓ Dummy data loaded successfully")
            except FileNotFoundError:
                logger.warning("dummy_data.json not found - database may be empty")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    db_conn = MongoDBConnection()
    if db_conn.client:
        db_conn.client.close()
        logger.info("MongoDB connection closed")

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Check API and database health"""
    db_conn = MongoDBConnection()
    
    return {
        "status": "ok",
        "api": "running",
        "database": "connected" if db_conn.db is not None else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: str):
    """Get user profile by ID"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    user = db_conn.db['users'].find_one({'id': user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Remove MongoDB's _id field
    user.pop('_id', None)
    return user

@app.get("/api/users", tags=["Users"])
async def list_users(skip: int = 0, limit: int = 10):
    """List all users with pagination"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    users = list(db_conn.db['users'].find().skip(skip).limit(limit))
    for user in users:
        user.pop('_id', None)
    
    return {
        "users": users,
        "skip": skip,
        "limit": limit,
        "count": len(users)
    }

# ============================================================================
# FAMILY MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/families/{family_id}", tags=["Families"])
async def get_family(family_id: str):
    """Get family profile by ID"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    family = db_conn.db['families'].find_one({'id': family_id})
    
    if not family:
        raise HTTPException(status_code=404, detail=f"Family {family_id} not found")
    
    family.pop('_id', None)
    return family

@app.get("/api/families", tags=["Families"])
async def list_families(skip: int = 0, limit: int = 10):
    """List all families with pagination"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    families = list(db_conn.db['families'].find().skip(skip).limit(limit))
    for family in families:
        family.pop('_id', None)
    
    return {
        "families": families,
        "skip": skip,
        "limit": limit,
        "count": len(families)
    }

# ============================================================================
# FOOD CATALOG ENDPOINTS
# ============================================================================

@app.get("/api/foods", tags=["Foods"])
async def list_foods(category: Optional[str] = None, skip: int = 0, limit: int = 20):
    """List foods from catalog, optionally filtered by category"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    query = {}
    if category:
        query['category'] = category
    
    foods = list(db_conn.db['foods'].find(query).skip(skip).limit(limit))
    for food in foods:
        food.pop('_id', None)
    
    return {
        "foods": foods,
        "category": category,
        "count": len(foods)
    }

@app.get("/api/foods/categories", tags=["Foods"])
async def get_food_categories():
    """Get list of available food categories"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    categories = db_conn.db['foods'].distinct('category')
    return {
        "categories": sorted(categories),
        "count": len(categories)
    }

# ============================================================================
# RECOMMENDATION ENDPOINTS (CONSUMER SIDE)
# ============================================================================

@app.post("/api/recommendations/individual", tags=["Recommendations"])
async def get_individual_recommendations(request: RecommendationRequest):
    """
    Get personalized food recommendations for an individual
    
    Request body:
    {
        "user_id": "user_0001",
        "current_nutrition": {"calories": 500, "protein": 20, ...},  # optional
        "num_recommendations": 15,
        "scope": "individual"
    }
    """
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Get user
    user = db_conn.db['users'].find_one({'id': request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
    
    user.pop('_id', None)
    
    # Get all orders from this user for collaborative filtering
    orders = list(db_conn.db['orders'].find({'user_id': request.user_id}))
    for order in orders:
        order.pop('_id', None)
    
    # Get all users and foods
    all_users = list(db_conn.db['users'].find())
    for u in all_users:
        u.pop('_id', None)
    
    all_foods = list(db_conn.db['foods'].find())
    for f in all_foods:
        f.pop('_id', None)
    
    # Initialize recommendation engine (imported from recommendation_engine.py)
    from recommendation_engine import HybridRecommender
    
    recommender = HybridRecommender(all_users, orders, all_foods)
    
    # Get recommendations
    recommendations = recommender.get_personalized_recommendations(
        user=user,
        current_nutrition=request.current_nutrition,
        num_recommendations=request.num_recommendations,
        scope=request.scope
    )
    
    # Save recommendation
    recommendations['_id'] = f"{request.user_id}_{datetime.now().isoformat()}"
    db_conn.db['recommendations'].insert_one(recommendations)
    
    recommendations.pop('_id', None)
    return recommendations

@app.post("/api/recommendations/family", tags=["Recommendations"])
async def get_family_recommendations(request: FamilyRecommendationRequest):
    """
    Get food recommendations for a whole family
    
    Request body:
    {
        "family_id": "family_user_0002",
        "num_recommendations": 20
    }
    """
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Get family
    family = db_conn.db['families'].find_one({'id': request.family_id})
    if not family:
        raise HTTPException(status_code=404, detail=f"Family {request.family_id} not found")
    
    family.pop('_id', None)
    
    # Get all data for recommendation engine
    all_users = list(db_conn.db['users'].find())
    for u in all_users:
        u.pop('_id', None)
    
    all_orders = list(db_conn.db['orders'].find())
    for o in all_orders:
        o.pop('_id', None)
    
    all_foods = list(db_conn.db['foods'].find())
    for f in all_foods:
        f.pop('_id', None)
    
    # Initialize recommendation engine
    from recommendation_engine import HybridRecommender
    
    recommender = HybridRecommender(all_users, all_orders, all_foods)
    
    # Get recommendations
    recommendations = recommender.get_family_recommendations(family)
    
    # Save recommendation
    rec_doc = recommendations.copy()
    rec_doc['_id'] = f"{request.family_id}_{datetime.now().isoformat()}"
    db_conn.db['recommendations'].insert_one(rec_doc)
    
    return recommendations

# ============================================================================
# ORDER ENDPOINTS
# ============================================================================

@app.get("/api/orders/user/{user_id}", tags=["Orders"])
async def get_user_orders(user_id: str, skip: int = 0, limit: int = 10):
    """Get order history for a user"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    orders = list(db_conn.db['orders'].find({'user_id': user_id}).skip(skip).limit(limit))
    for order in orders:
        order.pop('_id', None)
    
    return {
        "user_id": user_id,
        "orders": orders,
        "count": len(orders)
    }

@app.post("/api/orders", tags=["Orders"])
async def create_order(request: OrderRequest):
    """Record a new order"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    order = {
        'id': f"order_{datetime.now().timestamp()}",
        'user_id': request.user_id,
        'items': request.items,
        'total': request.total,
        'order_date': datetime.now().isoformat()
    }
    
    result = db_conn.db['orders'].insert_one(order)
    order['_id'] = result.inserted_id
    
    return {
        "message": "Order created successfully",
        "order": order
    }

# ============================================================================
# STATISTICS & ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/stats/summary", tags=["Analytics"])
async def get_summary_statistics():
    """Get summary statistics about the system"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    return {
        "total_users": db_conn.db['users'].count_documents({}),
        "total_families": db_conn.db['families'].count_documents({}),
        "total_orders": db_conn.db['orders'].count_documents({}),
        "total_foods": db_conn.db['foods'].count_documents({}),
        "total_recommendations_generated": db_conn.db['recommendations'].count_documents({})
    }

@app.get("/api/stats/popular-foods", tags=["Analytics"])
async def get_popular_foods(limit: int = 10):
    """Get most frequently purchased foods"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    pipeline = [
        {'$unwind': '$items'},
        {'$group': {'_id': '$items.name', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': limit}
    ]
    
    results = list(db_conn.db['orders'].aggregate(pipeline))
    
    return {
        "popular_foods": results,
        "limit": limit
    }

@app.get("/api/stats/average-order-value", tags=["Analytics"])
async def get_average_order_value():
    """Get average order value statistics"""
    db_conn = MongoDBConnection()
    
    if not db_conn.db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    pipeline = [
        {'$group': {
            '_id': None,
            'avg_total': {'$avg': '$total'},
            'min_total': {'$min': '$total'},
            'max_total': {'$max': '$total'},
            'total_orders': {'$sum': 1}
        }}
    ]
    
    result = list(db_conn.db['orders'].aggregate(pipeline))
    
    if result:
        return {
            'average_order_value': round(result[0]['avg_total'], 2),
            'min_order_value': round(result[0]['min_total'], 2),
            'max_order_value': round(result[0]['max_total'], 2),
            'total_orders': result[0]['total_orders']
        }
    else:
        return {'error': 'No orders found'}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and documentation"""
    return {
        "name": "SNAP Food Shop Recommendation API",
        "version": "1.0.0",
        "description": "AI/ML powered food recommendations for SNAP benefit shoppers",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "users": "/api/users",
            "families": "/api/families",
            "foods": "/api/foods",
            "recommendations": "/api/recommendations/individual, /api/recommendations/family",
            "orders": "/api/orders",
            "analytics": "/api/stats/summary"
        }
    }

# ============================================================================
# RUNNING THE SERVER
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   SNAP Food Shop Recommendation API                        ║
    ║   Starting FastAPI server...                               ║
    ║                                                            ║
    ║   📚 API Docs: http://localhost:8000/docs                 ║
    ║   🔌 API URL: http://localhost:8000                       ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Hot reload on code changes
    )
