# MERCHANT-SIDE FEATURES - COMPLETE IMPLEMENTATION GUIDE

## 📊 Overview

Three complete merchant-facing systems have been implemented:

1. **Inventory Management System** (`merchant_inventory_system.py`)
   - Demand forecasting
   - Inventory allocation across pickup points
   - Food truck route optimization
   - Real-time inventory tracking
   - Stockout predictions

2. **Digital Signage System** (`digital_signage_system.py`)
   - Order ready notifications on truck screens
   - Advertisement content management
   - Nutrition education displays
   - Campaign tracking & ROI

3. **Merchant API** (`merchant_api_integration.py`)
   - RESTful endpoints for all merchant features
   - Dashboard for decision-making
   - Analytics & reporting

---

## 🏪 COMPONENT 1: INVENTORY MANAGEMENT SYSTEM

### Purpose
Optimize what food to stock at each pickup point based on:
- Predicted demand from consumer recommendations
- User geographic distribution
- Budget constraints
- Historical sales patterns

### Key Classes

#### 1. DemandForecaster
```python
forecaster = DemandForecaster(recommendations, orders)
forecast = forecaster.forecast_demand(num_users=50, days_ahead=7)

# Returns:
{
    'food_name': {
        'historical_demand': X units/week,
        'forecast_demand': Y units/week,
        'confidence': 0.0-1.0,
        'recommended_stock': Z units
    }
}
```

**How it works:**
1. Analyzes past order history
2. Calculates historical demand percentage
3. Scales based on number of users
4. Adds variance for real-world variability
5. Recommends stock with 20% safety buffer

**Example Output:**
```
Oats (1 lb): 
  - Historical: 22.3 units/week
  - Forecast: 25.6 units/week (±10% variance)
  - Recommended Stock: 31 units
  - Confidence: 95%
```

#### 2. PickupPointOptimizer
```python
optimizer = PickupPointOptimizer(users, pickup_points)
allocation = optimizer.allocate_inventory(demand_forecast, total_budget=5000)

# Returns allocation by location:
{
    'point_downtown_1': {
        'foods': {'Carrots': 50, 'Oats': 31, ...},
        'allocated_budget': $1,332.72,
        'utilization_rate': 38.1%,
        'num_users': 35
    }
}
```

**How it works:**
1. Maps users to nearest pickup points (1-mile radius)
2. Allocates budget proportional to user density
3. Prioritizes high-demand foods
4. Respects budget constraints
5. Maximizes utilization rate

**Example:**
- Downtown point serves 35 users → gets 35% of $5000 budget
- Northeast point serves 13 users → gets 13% of $5000 budget

#### 3. FoodTruckRouteOptimizer
```python
optimizer = FoodTruckRouteOptimizer(pickup_points)
route = optimizer.optimize_route(
    pickup_points_to_visit=['point_downtown_1', 'point_northeast_1', ...],
    start_location='point_downtown_1'
)

# Returns:
{
    'route': [start, point1, point2, ..., start],
    'total_distance': 7.38,  # miles
    'estimated_time_hours': 0.25,
    'fuel_cost': 1.84,
    'efficiency_score': 8.13  # stops per mile
}
```

**How it works:**
- Solves Traveling Salesman Problem using nearest neighbor algorithm
- Minimizes total distance traveled
- Calculates fuel costs (example: $0.25/mile)
- Provides efficiency metrics

**Example Route:**
```
Downtown Hub 1 (start)
    ↓ 0.5 mi
Downtown Hub 2
    ↓ 1.2 mi
Northeast Center
    ↓ 2.1 mi
Southeast Center
    ↓ 1.8 mi
West Hub
    ↓ 1.88 mi
Back to Downtown Hub 1

Total: 7.38 miles, 0.25 hours, $1.84 fuel cost
```

#### 4. InventoryTracker
```python
tracker = InventoryTracker()

# Stock a point
tracker.stock_pickup_point('point_downtown_1', {
    'Carrots (1 lb)': 50,
    'Oats (1 lb)': 31
})

# Record sale
tracker.record_sale('point_downtown_1', {
    'Carrots (1 lb)': 15
})

# Check status
status = tracker.get_inventory_status('point_downtown_1')
# Returns current inventory at that location

# Get alerts
low_stock = tracker.get_low_stock_alert(threshold=5)
# Returns foods below threshold

# Forecast stockouts
forecast = tracker.forecast_stockout({
    'Carrots (1 lb)': 2.5,  # units per day
    'Oats (1 lb)': 1.8
})
# Returns days until each food runs out
```

**Real-time tracking:**
- Updates when stock is added
- Decrements when sales occur
- Historical log of all transactions
- Stockout predictions

#### 5. MerchantAnalytics
```python
analytics = MerchantAnalytics(orders, recommendations)

# ROI analysis
roi = analytics.calculate_roi(
    total_investment=10000,
    total_revenue=3592.28
)
# Returns: roi_percent, payback_period_days, profit

# Food performance
metrics = analytics.food_performance_metrics()
# Returns: units_sold, revenue, avg_price, popularity %

# Recommendation acceptance
acceptance = analytics.recommendation_acceptance_rate()
# Returns: estimated adoption rate
```

---

## 📺 COMPONENT 2: DIGITAL SIGNAGE SYSTEM

### Purpose
Manage content displayed on food truck screens:
- Order notifications (high priority)
- Advertisements (revenue generation)
- Nutrition education (value-add)
- Announcements (operations)

### Key Classes

#### 1. DisplayContent
```python
display = DisplayContent()

# Create order ready display
content = display.create_order_ready_display(
    order_id='order_001',
    user_name='Michelle Garcia',
    pickup_time='2:15 PM',
    items=['Carrots', 'Eggs'],
    duration_seconds=30
)

# Create ad display
ad = display.create_advertisement(
    business_name='Dave\'s Corner Store',
    business_type='grocery',
    offer='Fresh Produce 20% Off',
    image_url='assets/promo.jpg',
    duration_seconds=15,
    revenue=0.50  # $0.50 per display
)

# Create nutrition tip
tip = display.create_nutrition_tip(
    tip='Dark leafy greens are nutrient-dense',
    category='vegetables',
    duration_seconds=10
)

# Manage queue
display.add_to_queue(ad)
next_content = display.get_next_content()
```

**Display Types & Layout:**

1. **Order Ready (Green, High Priority)**
   ```
   ╔═══════════════════════════════╗
   ║    ORDER READY! 🎉            ║
   ║                               ║
   ║  Michelle Garcia,             ║
   ║  your order is ready!          ║
   ║                               ║
   ║  Items: Carrots, Eggs, Spinach║
   ║  Pickup Time: 2:15 PM         ║
   ╚═══════════════════════════════╝
   [Display for 30 seconds]
   ```

2. **Advertisement (Blue, Revenue)**
   ```
   ╔═══════════════════════════════╗
   ║  Dave's Corner Store          ║
   ║  [Product Image]              ║
   ║  Fresh Produce 20% Off!       ║
   ║  This Week Only               ║
   ║  QR Code: [scan for more info]║
   ╚═══════════════════════════════╝
   [Display for 15 seconds]
   ```

3. **Nutrition Tip (Red/Orange, Education)**
   ```
   ╔═══════════════════════════════╗
   ║  💡 Nutrition Tip             ║
   ║                               ║
   ║  Dark leafy greens like       ║
   ║  spinach are nutrient-dense   ║
   ║  and low-calorie.             ║
   ║  Great for balanced meals!    ║
   ╚═══════════════════════════════╝
   [Display for 10 seconds]
   ```

#### 2. AdvertisementManager
```python
manager = AdvertisementManager()

# Register partner business
business = manager.add_partner_business(
    business_id='biz_001',
    name='Dave\'s Corner Store',
    type_category='grocery',
    location='Near Metro Station',
    contact='dave@cornerstore.local'
)

# Create campaign
campaign = manager.create_campaign(
    campaign_id='camp_001',
    business_id='biz_001',
    offer='Fresh Produce Specials',
    image_url='assets/promo.jpg',
    duration_days=7,
    pricing_tier='daily_package'  # $25/day = $175/week
)

# Track performance
manager.record_impression('camp_001')  # +1 display
manager.record_interaction('camp_001')  # +1 click/scan

# Calculate revenue
revenue = manager.calculate_revenue()
# Returns: total_revenue, revenue_by_business, revenue_by_model

# Calculate ROI for campaign
roi = manager.get_campaign_roi('camp_001')
# Returns: roi_percent, ctr, cost_per_impression
```

**Pricing Models:**

| Tier | Cost | When to Use |
|------|------|-----------|
| Per Impression | $0.50/display | Small campaigns, testing |
| Per Interaction | $2.00/click | Performance-based |
| Daily Package | $25/day | Small businesses, daily rotations |
| Weekly Package | $140/week | Regular campaigns |
| Monthly Package | $500/month | Premium partners, long-term |

**Example Campaign Performance:**
```
Campaign: Fresh Produce Specials
Partner: Dave's Corner Store
Duration: 7 days
Pricing: Daily Package ($25 × 7 = $175 cost)

Performance:
  - Impressions: 342 displays
  - Interactions: 18 QR scans
  - Click-through Rate: 5.26%
  - Cost per Impression: $0.51
  - Cost per Interaction: $9.72
  - Estimated ROI: Based on customer acquisition
```

**Revenue Breakdown Example:**
```
Total Advertising Revenue: $350/week

By Business:
  - Dave's Corner Store: $175 (50%)
  - Healthy Juice Bar: $175 (50%)

By Pricing Model:
  - Daily Package: $350 (100%)
```

#### 3. FoodTruckDisplay
```python
truck = FoodTruckDisplay(
    truck_id='truck_01',
    location='Downtown DC - Pennsylvania Ave'
)

# Display order ready (interrupts current display)
truck.display_order_ready(
    order_id='order_12345',
    user_name='Michelle Garcia',
    pickup_time='2:15 PM',
    items=['Carrots', 'Eggs', 'Spinach']
)

# Schedule ads
truck.schedule_advertisement(
    campaign_id='camp_001',
    business_name='Dave\'s Corner Store',
    offer='20% Off Fresh Produce',
    image_url='assets/promo.jpg',
    frequency='idle'  # Show between orders
)

# Add nutrition content
truck.schedule_nutrition_tips()

# Update location
truck.update_location('Northeast Center - H St NE')

# Get status
status = truck.get_display_status()
```

**Display Queue Priority:**
1. **Order Ready Notifications** (HIGHEST)
   - Inserted at front of queue
   - Interrupts current display
   - Duration: 30 seconds

2. **Advertisements** (MEDIUM)
   - Normal queue position
   - Scheduled between orders
   - Revenue-generating

3. **Nutrition Tips** (LOW)
   - Fills idle time
   - Educational value
   - No revenue

---

## 🔗 COMPONENT 3: MERCHANT API

### REST Endpoints (Add to FastAPI server)

#### Inventory Management
```
POST   /api/merchant/demand-forecast
GET    /api/merchant/pickup-points
POST   /api/merchant/inventory-allocation
POST   /api/merchant/food-truck-route
POST   /api/merchant/inventory/stock
POST   /api/merchant/inventory/sale
GET    /api/merchant/inventory/status
GET    /api/merchant/inventory/stockout-forecast
```

#### Signage & Display
```
POST   /api/merchant/signage/order-ready
POST   /api/merchant/signage/schedule-ad
GET    /api/merchant/signage/display-status
```

#### Advertising
```
POST   /api/merchant/partners/register
GET    /api/merchant/advertising/campaigns
GET    /api/merchant/advertising/revenue
```

#### Analytics
```
GET    /api/merchant/analytics/roi
GET    /api/merchant/analytics/food-performance
GET    /api/merchant/analytics/revenue
GET    /api/merchant/dashboard
```

### Example API Calls

**1. Forecast Demand**
```bash
curl -X POST http://localhost:8000/api/merchant/demand-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "num_users": 50,
    "days_ahead": 7
  }'

Response:
{
  "Carrots (1 lb)": {
    "forecast_demand": 18.5,
    "recommended_stock": 22,
    "confidence": 0.95
  },
  ...
}
```

**2. Allocate Inventory**
```bash
curl -X POST http://localhost:8000/api/merchant/inventory-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_points": ["point_downtown_1", "point_northeast_1"],
    "total_budget": 5000,
    "days_ahead": 7
  }'

Response:
{
  "point_downtown_1": {
    "foods": {
      "Oats (1 lb)": 31,
      "Carrots (1 lb)": 25,
      ...
    },
    "allocated_budget": 1332.72,
    "utilization_rate": 38.1
  },
  ...
}
```

**3. Optimize Route**
```bash
curl -X POST http://localhost:8000/api/merchant/food-truck-route \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_points": [
      "point_downtown_1",
      "point_northeast_1",
      "point_southeast_1"
    ],
    "start_location": "point_downtown_1"
  }'

Response:
{
  "route": ["point_downtown_1", "point_northeast_1", "point_southeast_1", "point_downtown_1"],
  "total_distance": 7.38,
  "estimated_time_hours": 0.25,
  "fuel_cost": 1.84,
  "efficiency_score": 8.13
}
```

**4. Display Order Ready**
```bash
curl -X POST http://localhost:8000/api/merchant/signage/order-ready \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_12345",
    "user_name": "Michelle Garcia",
    "pickup_time": "2:15 PM",
    "items": ["Carrots (1 lb)", "Eggs (1 dozen)", "Spinach"]
  }'

Response:
{
  "status": "queued",
  "display_type": "order_ready",
  "order_id": "order_12345",
  "display_duration": 30
}
```

**5. Schedule Advertisement**
```bash
curl -X POST http://localhost:8000/api/merchant/signage/schedule-ad \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "biz_001",
    "offer": "Fresh Produce 20% Off This Week!",
    "image_url": "assets/daves_store_promo.jpg",
    "duration_days": 7,
    "pricing_tier": "daily_package"
  }'

Response:
{
  "status": "scheduled",
  "campaign_id": "camp_1234567890",
  "estimated_cost": 175.00,
  "duration_days": 7
}
```

**6. Get Merchant Dashboard**
```bash
curl http://localhost:8000/api/merchant/dashboard

Response:
{
  "summary": {
    "total_users": 50,
    "total_orders": 249,
    "total_revenue": 3592.28,
    "active_pickup_points": 6,
    "active_campaigns": 2
  },
  "inventory": {
    "total_items_in_stock": 450,
    "low_stock_alerts": 3,
    "forecast_stockout_2days": 2
  },
  "advertising": {
    "total_impressions": 631,
    "ad_revenue": 350.00,
    "active_partners": 2
  }
}
```

---

## 🚀 DEPLOYMENT

### Add to Existing FastAPI Server

1. **Copy files to your project:**
   ```bash
   cp merchant_inventory_system.py /backend/
   cp digital_signage_system.py /backend/
   cp merchant_api_integration.py /backend/
   ```

2. **Add to main.py imports:**
   ```python
   from merchant_inventory_system import (
       DemandForecaster, PickupPointOptimizer, 
       FoodTruckRouteOptimizer, InventoryTracker, MerchantAnalytics
   )
   from digital_signage_system import (
       FoodTruckDisplay, AdvertisementManager
   )
   ```

3. **Initialize at startup:**
   ```python
   @app.on_event("startup")
   async def startup_merchant_systems():
       global inventory_tracker, ad_manager, food_truck_display
       inventory_tracker = InventoryTracker()
       ad_manager = AdvertisementManager()
       food_truck_display = FoodTruckDisplay("truck_01", "Downtown DC")
   ```

4. **Add all merchant endpoints** from `merchant_api_integration.py`

5. **Deploy same as before:**
   ```bash
   git add .
   git commit -m "Add merchant features"
   git push origin main  # Auto-deploys to Railway
   ```

### Database Collections Needed

```javascript
// MongoDB collections for merchant data
db.createCollection("demand_forecasts")
db.createCollection("inventory_allocations")
db.createCollection("inventory_tracker")
db.createCollection("food_truck_routes")
db.createCollection("advertisements")
db.createCollection("campaigns")
db.createCollection("ad_impressions")
db.createCollection("merchant_analytics")

// Create indexes
db.demand_forecasts.createIndex({ timestamp: -1 })
db.campaigns.createIndex({ business_id: 1 })
db.advertisements.createIndex({ campaign_id: 1 })
```

---

## 💰 REVENUE MODEL

### Advertising Revenue Stream
```
Monthly Revenue = (Impressions × $0.50) OR (Daily Package × 30 days)

Example:
- 5 active campaigns
- 200 impressions per campaign per day
- 200 × 5 × 30 × $0.50 = $15,000/month

OR

- 5 businesses at daily package ($25/day)
- 5 × $25 × 30 = $3,750/month

Combined (mix of models):
- 2 businesses on daily package: 2 × $25 × 30 = $1,500
- 3 businesses on per-impression: ~4,500
- Total: ~$6,000/month
```

### Scaling Economics
```
With 100 pickup points across city:
- 50 partner businesses
- Avg $120/month per business = $6,000/month
- 10 food trucks = $60,000/month potential revenue
- Reinvest in better food/nutrition to maintain program viability
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [x] Demand forecasting algorithm
- [x] Inventory allocation system
- [x] Route optimization (TSP solver)
- [x] Real-time inventory tracking
- [x] Digital display content management
- [x] Advertisement campaign system
- [x] Revenue tracking & ROI calculation
- [x] Merchant analytics dashboard
- [x] API endpoints (15+)
- [x] Demo & test data
- [ ] React admin dashboard UI
- [ ] Merchant mobile app
- [ ] SMS/Email notifications
- [ ] Advanced reporting

---

## 🎓 Next Steps

1. **Deploy merchant API** - Add to FastAPI server, test endpoints
2. **Build Admin Dashboard** - React UI for merchant operations
3. **Add Real-time Updates** - WebSocket for live inventory updates
4. **Integrate SMS Notifications** - Alert when stock is low
5. **Multi-truck Support** - Manage multiple food trucks simultaneously
6. **Advanced Analytics** - Predictive models, trend analysis
7. **Partner Mobile App** - Simplified ad management for businesses
8. **Scale to Multiple Cities** - Regional inventory management

---

## 📞 Support

All code is documented with docstrings. Run demos:
```bash
python merchant_inventory_system.py
python digital_signage_system.py
python merchant_api_integration.py
```

Check generated reports:
- `merchant_report.json` - Inventory & analytics
- `display_system_report.json` - Signage & ads
