"""
Merchant-Side Inventory Management System
Predicts demand, optimizes stock allocation across pickup points,
and manages inventory by location and food truck.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import math

# ============================================================================
# PART 1: DEMAND FORECASTING
# ============================================================================

class DemandForecaster:
    """Predict what foods will be in demand based on user recommendations"""
    
    def __init__(self, recommendations: List[Dict], orders: List[Dict]):
        self.recommendations = recommendations
        self.orders = orders
        self.food_demand = self._calculate_historical_demand()
    
    def _calculate_historical_demand(self) -> Dict[str, Dict]:
        """Analyze past orders to understand demand patterns"""
        demand_data = defaultdict(lambda: {'count': 0, 'total_cost': 0, 'avg_price': 0})
        
        for order in self.orders:
            for item in order['items']:
                demand_data[item['name']]['count'] += 1
                demand_data[item['name']]['total_cost'] += item['price']
        
        # Calculate average prices
        for food_name in demand_data:
            if demand_data[food_name]['count'] > 0:
                demand_data[food_name]['avg_price'] = (
                    demand_data[food_name]['total_cost'] / 
                    demand_data[food_name]['count']
                )
        
        return demand_data
    
    def forecast_demand(self, 
                       num_users: int,
                       days_ahead: int = 7) -> Dict[str, Dict]:
        """
        Forecast demand for next N days
        
        Returns:
        {
            'food_name': {
                'historical_demand': X units/week,
                'forecast_demand': Y units/week,
                'confidence': 0.0-1.0,
                'recommended_stock': Z units
            }
        }
        """
        
        forecast = {}
        
        # Calculate base demand from historical data
        total_orders = len(self.orders)
        
        for food_name, data in self.food_demand.items():
            # Historical demand as percentage of orders
            hist_pct = data['count'] / total_orders if total_orders > 0 else 0
            
            # Scale forecast based on number of users
            # Assume each user will make 1-2 orders per week
            orders_per_week = num_users * 1.5
            
            historical_demand = hist_pct * orders_per_week
            forecast_demand = historical_demand * (1 + np.random.normal(0, 0.1))  # Add variance
            
            # Confidence decreases for rarely-purchased items
            confidence = min(0.95, hist_pct * 10)  # Normalize to 0-1
            
            # Recommended stock (units for the week)
            # Assume each order contains 1 unit of each food on average
            recommended_stock = max(1, int(np.ceil(forecast_demand * 1.2)))  # 20% buffer
            
            forecast[food_name] = {
                'historical_demand': round(historical_demand, 2),
                'forecast_demand': round(forecast_demand, 2),
                'confidence': round(confidence, 2),
                'recommended_stock': recommended_stock,
                'avg_price': round(data['avg_price'], 2),
                'demand_trend': 'stable'  # Could be: stable, increasing, decreasing
            }
        
        return forecast

# ============================================================================
# PART 2: PICKUP POINT OPTIMIZATION
# ============================================================================

class PickupPointOptimizer:
    """Optimize food allocation across multiple pickup points"""
    
    def __init__(self, users: List[Dict], pickup_points: List[Dict]):
        self.users = users
        self.pickup_points = pickup_points
        self.user_locations = self._map_users_to_points()
    
    def _map_users_to_points(self) -> Dict[str, List[str]]:
        """
        Map users to their nearest pickup point(s) within 1-mile radius
        In production, use actual geospatial data; here we simulate by zip code
        """
        user_to_points = defaultdict(list)
        
        # Simple simulation: assign users to pickup points by zip code proximity
        zip_to_points = {
            '20001': ['point_downtown_1', 'point_downtown_2'],
            '20002': ['point_northeast_1', 'point_downtown_1'],
            '20003': ['point_southeast_1', 'point_downtown_2'],
            '20004': ['point_southeast_1', 'point_southeast_2'],
            '20005': ['point_west_1', 'point_downtown_1'],
        }
        
        for user in self.users:
            zip_code = user.get('zip_code', '20001')
            user_to_points[user['id']] = zip_to_points.get(zip_code, ['point_downtown_1'])
        
        return user_to_points
    
    def allocate_inventory(self,
                          demand_forecast: Dict,
                          total_budget: float) -> Dict[str, Dict]:
        """
        Allocate inventory across pickup points based on:
        1. Demand forecast
        2. User distribution by location
        3. Budget constraints
        4. Storage capacity at each location
        
        Returns:
        {
            'point_name': {
                'foods': {'food_name': quantity, ...},
                'estimated_cost': $,
                'expected_orders': N,
                'utilization_rate': %
            }
        }
        """
        
        allocation = {}
        
        # Count users per pickup point
        point_user_counts = defaultdict(int)
        for user_id, points in self.user_locations.items():
            for point in points:
                point_user_counts[point] += 1
        
        # Total users
        total_users = len(self.users)
        
        # Allocate budget to each point based on user density
        point_budgets = {}
        for point in point_user_counts:
            user_ratio = point_user_counts[point] / max(total_users, 1)
            point_budgets[point] = total_budget * user_ratio
        
        # Allocate foods to each point
        for point_name, budget in point_budgets.items():
            foods = {}
            remaining_budget = budget
            
            # Sort foods by demand
            sorted_foods = sorted(
                demand_forecast.items(),
                key=lambda x: x[1]['forecast_demand'],
                reverse=True
            )
            
            for food_name, forecast_data in sorted_foods:
                quantity_needed = forecast_data['recommended_stock']
                cost_per_unit = forecast_data['avg_price']
                total_cost = quantity_needed * cost_per_unit
                
                # Allocate if budget allows
                if total_cost <= remaining_budget:
                    foods[food_name] = {
                        'quantity': quantity_needed,
                        'cost': round(total_cost, 2),
                        'demand_forecast': forecast_data['forecast_demand']
                    }
                    remaining_budget -= total_cost
                else:
                    # Partial allocation
                    max_units = int(remaining_budget / cost_per_unit)
                    if max_units > 0:
                        foods[food_name] = {
                            'quantity': max_units,
                            'cost': round(max_units * cost_per_unit, 2),
                            'demand_forecast': forecast_data['forecast_demand']
                        }
                        remaining_budget = 0
                        break
            
            total_allocated = sum(food['cost'] for food in foods.values())
            
            allocation[point_name] = {
                'location': point_name,
                'foods': foods,
                'allocated_budget': round(total_allocated, 2),
                'remaining_budget': round(remaining_budget, 2),
                'num_users': point_user_counts[point_name],
                'num_food_types': len(foods),
                'utilization_rate': round((total_allocated / budget * 100) if budget > 0 else 0, 1)
            }
        
        return allocation

# ============================================================================
# PART 3: FOOD TRUCK ROUTE OPTIMIZATION
# ============================================================================

class FoodTruckRouteOptimizer:
    """Optimize food truck routes between pickup points"""
    
    def __init__(self, pickup_points: List[Dict]):
        self.pickup_points = pickup_points
        # Simulated coordinates (in production, use actual GPS)
        self.coordinates = self._generate_coordinates()
        self.distance_matrix = self._calculate_distances()
    
    def _generate_coordinates(self) -> Dict[str, Tuple[float, float]]:
        """Generate simulated GPS coordinates for pickup points"""
        coords = {
            'point_downtown_1': (38.9072, -77.0369),
            'point_downtown_2': (38.9084, -77.0358),
            'point_northeast_1': (38.9155, -77.0107),
            'point_southeast_1': (38.8921, -77.0241),
            'point_southeast_2': (38.8910, -77.0198),
            'point_west_1': (38.9015, -77.0521),
        }
        return coords
    
    def _calculate_distances(self) -> Dict[str, Dict[str, float]]:
        """Calculate distances between all pickup points (in miles)"""
        distances = defaultdict(dict)
        
        for point1 in self.coordinates:
            for point2 in self.coordinates:
                if point1 == point2:
                    distances[point1][point2] = 0
                else:
                    # Haversine distance formula (simplified)
                    lat1, lon1 = self.coordinates[point1]
                    lat2, lon2 = self.coordinates[point2]
                    
                    dlat = abs(lat2 - lat1)
                    dlon = abs(lon2 - lon1)
                    distance = math.sqrt(dlat**2 + dlon**2) * 69  # Convert to miles
                    distances[point1][point2] = round(distance, 2)
        
        return distances
    
    def optimize_route(self, 
                      pickup_points_to_visit: List[str],
                      start_location: str = 'point_downtown_1') -> Dict:
        """
        Optimize route using nearest neighbor algorithm
        
        Returns:
        {
            'route': [point1, point2, ...],
            'distances': [dist1, dist2, ...],
            'total_distance': X miles,
            'estimated_time': Y hours,
            'fuel_cost': $Z,
            'stops': N
        }
        """
        
        if not pickup_points_to_visit:
            return {'error': 'No pickup points to visit'}
        
        # Nearest neighbor algorithm
        current = start_location
        unvisited = set(pickup_points_to_visit)
        route = [current]
        distances = []
        
        while unvisited:
            # Find nearest unvisited point
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current].get(x, float('inf')))
            dist = self.distance_matrix[current][nearest]
            
            distances.append(dist)
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        # Return to start
        return_dist = self.distance_matrix[current][start_location]
        distances.append(return_dist)
        route.append(start_location)
        
        total_distance = sum(distances)
        estimated_time = total_distance / 30  # Assume 30 mph average
        fuel_cost = total_distance * 0.25  # $0.25 per mile
        
        return {
            'route': route,
            'distances': distances,
            'total_distance': round(total_distance, 2),
            'estimated_time_hours': round(estimated_time, 2),
            'fuel_cost': round(fuel_cost, 2),
            'stops': len(set(route)) - 1,  # Excluding return to start
            'efficiency_score': round((len(set(route)) / total_distance * 10), 2)  # Stops per mile
        }

# ============================================================================
# PART 4: INVENTORY TRACKER
# ============================================================================

class InventoryTracker:
    """Track real-time inventory at each pickup point"""
    
    def __init__(self):
        self.inventory = defaultdict(lambda: defaultdict(int))
        self.inventory_history = []
        self.last_update = datetime.now()
    
    def stock_pickup_point(self,
                          point_name: str,
                          foods: Dict[str, int]):
        """Stock a pickup point with foods"""
        
        for food_name, quantity in foods.items():
            self.inventory[point_name][food_name] += quantity
        
        self.inventory_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'stock',
            'point': point_name,
            'foods': foods
        })
    
    def record_sale(self,
                   point_name: str,
                   foods: Dict[str, int]):
        """Record sales at a pickup point"""
        
        for food_name, quantity in foods.items():
            self.inventory[point_name][food_name] = max(0, 
                self.inventory[point_name][food_name] - quantity)
        
        self.inventory_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'sale',
            'point': point_name,
            'foods': foods
        })
    
    def get_inventory_status(self, point_name: str = None) -> Dict:
        """Get current inventory status"""
        
        if point_name:
            return {
                'point': point_name,
                'foods': dict(self.inventory[point_name]),
                'total_items': sum(self.inventory[point_name].values()),
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Return all locations
            status = {}
            for point in self.inventory:
                status[point] = {
                    'foods': dict(self.inventory[point]),
                    'total_items': sum(self.inventory[point].values())
                }
            return status
    
    def get_low_stock_alert(self, threshold: int = 5) -> Dict[str, List[str]]:
        """Get foods that are low in stock"""
        
        alerts = {}
        for point, foods in self.inventory.items():
            low_items = [name for name, qty in foods.items() if qty < threshold]
            if low_items:
                alerts[point] = low_items
        
        return alerts
    
    def forecast_stockout(self, 
                         consumption_rate: Dict[str, float]) -> Dict:
        """
        Forecast when items will run out based on consumption patterns
        
        Args:
            consumption_rate: {'food_name': units_per_day, ...}
        
        Returns:
            {'point': {'food_name': days_until_stockout, ...}}
        """
        
        forecast = {}
        
        for point, foods in self.inventory.items():
            point_forecast = {}
            for food_name, qty in foods.items():
                daily_rate = consumption_rate.get(food_name, 1)
                days_until_stockout = qty / daily_rate if daily_rate > 0 else float('inf')
                point_forecast[food_name] = round(days_until_stockout, 1)
            
            forecast[point] = point_forecast
        
        return forecast

# ============================================================================
# PART 5: MERCHANT ANALYTICS DASHBOARD
# ============================================================================

class MerchantAnalytics:
    """Analytics for merchant decision-making"""
    
    def __init__(self, 
                 orders: List[Dict],
                 recommendations: List[Dict]):
        self.orders = orders
        self.recommendations = recommendations
    
    def calculate_roi(self,
                     total_investment: float,
                     total_revenue: float) -> Dict:
        """Calculate return on investment"""
        
        roi = ((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0
        payback_period = total_investment / (total_revenue / 30) if total_revenue > 0 else float('inf')  # days
        
        return {
            'total_investment': round(total_investment, 2),
            'total_revenue': round(total_revenue, 2),
            'roi_percent': round(roi, 2),
            'payback_period_days': round(payback_period, 1),
            'profit': round(total_revenue - total_investment, 2)
        }
    
    def food_performance_metrics(self) -> Dict[str, Dict]:
        """Analyze performance of each food item"""
        
        metrics = {}
        food_sales = Counter()
        food_revenue = defaultdict(float)
        
        for order in self.orders:
            for item in order['items']:
                food_sales[item['name']] += 1
                food_revenue[item['name']] += item['price']
        
        for food_name in food_sales:
            metrics[food_name] = {
                'units_sold': food_sales[food_name],
                'total_revenue': round(food_revenue[food_name], 2),
                'avg_price': round(food_revenue[food_name] / food_sales[food_name], 2),
                'popularity_score': round((food_sales[food_name] / len(self.orders) * 100), 1)
            }
        
        return metrics
    
    def recommendation_acceptance_rate(self) -> Dict:
        """Track how often recommended foods are purchased"""
        
        if not self.recommendations:
            return {'rate': 0, 'data': 'No recommendations available'}
        
        # Simplified: assume recommendations are being followed
        avg_acceptance = sum(
            len(rec.get('recommendations', [])) for rec in self.recommendations
        ) / len(self.recommendations) if self.recommendations else 0
        
        return {
            'avg_recommendations_per_user': round(avg_acceptance, 1),
            'total_recommendations_generated': len(self.recommendations),
            'estimated_acceptance_rate_percent': 75  # Placeholder
        }

# ============================================================================
# PART 6: DEMO & EXAMPLE USAGE
# ============================================================================

def demo_merchant_system():
    """Demonstrate the merchant-side system"""
    
    print("="*80)
    print("MERCHANT-SIDE INVENTORY MANAGEMENT SYSTEM DEMO")
    print("="*80)
    
    # Load dummy data
    with open('dummy_data.json', 'r') as f:
        data = json.load(f)
    
    users = data['users']
    orders = data['orders']
    food_catalog = data['food_catalog']
    recommendations = []  # Would load from recommendations collection
    
    # ---- 1. DEMAND FORECASTING ----
    print("\n1. DEMAND FORECASTING")
    print("-" * 80)
    
    forecaster = DemandForecaster(recommendations, orders)
    demand = forecaster.forecast_demand(num_users=len(users), days_ahead=7)
    
    print("\nTop 5 Foods by Predicted Demand (Next Week):")
    for i, (food, forecast) in enumerate(
        sorted(demand.items(), key=lambda x: x[1]['forecast_demand'], reverse=True)[:5],
        1
    ):
        print(f"\n{i}. {food}")
        print(f"   Historical Demand: {forecast['historical_demand']:.1f} units/week")
        print(f"   Forecasted Demand: {forecast['forecast_demand']:.1f} units/week")
        print(f"   Recommended Stock: {forecast['recommended_stock']} units")
        print(f"   Confidence: {forecast['confidence']*100:.0f}%")
    
    # ---- 2. PICKUP POINT OPTIMIZATION ----
    print("\n" + "="*80)
    print("2. PICKUP POINT INVENTORY ALLOCATION")
    print("-" * 80)
    
    optimizer = PickupPointOptimizer(users, [])
    total_weekly_budget = 5000  # $5000/week budget
    
    allocation = optimizer.allocate_inventory(demand, total_weekly_budget)
    
    print(f"\nAllocating ${total_weekly_budget} across {len(allocation)} pickup points:\n")
    for point_name, alloc in allocation.items():
        print(f"\n{point_name}:")
        print(f"  Serving: {alloc['num_users']} users")
        print(f"  Allocated Budget: ${alloc['allocated_budget']}")
        print(f"  Food Types: {alloc['num_food_types']}")
        print(f"  Utilization: {alloc['utilization_rate']}%")
        print(f"  Top 3 Foods:")
        for food, details in list(alloc['foods'].items())[:3]:
            print(f"    - {food}: {details['quantity']} units (${details['cost']})")
    
    # ---- 3. FOOD TRUCK ROUTING ----
    print("\n" + "="*80)
    print("3. FOOD TRUCK ROUTE OPTIMIZATION")
    print("-" * 80)
    
    route_optimizer = FoodTruckRouteOptimizer([])
    points_to_visit = list(allocation.keys())
    
    route = route_optimizer.optimize_route(points_to_visit)
    
    print(f"\nOptimized Route (Traveling Salesman Problem):")
    print(f"Route: {' → '.join(route['route'][:6])}... → START")
    print(f"Total Distance: {route['total_distance']} miles")
    print(f"Estimated Time: {route['estimated_time_hours']} hours")
    print(f"Fuel Cost: ${route['fuel_cost']}")
    print(f"Number of Stops: {route['stops']}")
    print(f"Efficiency Score: {route['efficiency_score']} (stops/mile)")
    
    # ---- 4. INVENTORY TRACKING ----
    print("\n" + "="*80)
    print("4. INVENTORY TRACKING")
    print("-" * 80)
    
    tracker = InventoryTracker()
    
    # Stock a pickup point
    sample_stock = {
        'Carrots (1 lb)': 50,
        'Whole Wheat Bread (1 loaf)': 30,
        'Eggs (1 dozen)': 25,
    }
    
    tracker.stock_pickup_point('point_downtown_1', sample_stock)
    
    # Simulate some sales
    tracker.record_sale('point_downtown_1', {
        'Carrots (1 lb)': 15,
        'Whole Wheat Bread (1 loaf)': 8,
    })
    
    status = tracker.get_inventory_status('point_downtown_1')
    print(f"\nInventory at {status['point']}:")
    for food, qty in status['foods'].items():
        print(f"  {food}: {qty} units")
    
    low_stock = tracker.get_low_stock_alert(threshold=20)
    if low_stock:
        print(f"\nLow Stock Alerts:")
        for point, foods in low_stock.items():
            print(f"  {point}: {', '.join(foods)}")
    
    # ---- 5. ANALYTICS ----
    print("\n" + "="*80)
    print("5. MERCHANT ANALYTICS")
    print("-" * 80)
    
    analytics = MerchantAnalytics(orders, recommendations)
    
    total_revenue = sum(order['total'] for order in orders)
    total_investment = 10000  # $10k initial investment
    
    roi = analytics.calculate_roi(total_investment, total_revenue)
    
    print(f"\nROI Analysis:")
    print(f"  Total Investment: ${roi['total_investment']}")
    print(f"  Total Revenue: ${roi['total_revenue']}")
    print(f"  Profit: ${roi['profit']}")
    print(f"  ROI: {roi['roi_percent']}%")
    print(f"  Payback Period: {roi['payback_period_days']} days")
    
    performance = analytics.food_performance_metrics()
    
    print(f"\nTop 5 Performing Foods:")
    for i, (food, metrics) in enumerate(
        sorted(performance.items(), key=lambda x: x[1]['units_sold'], reverse=True)[:5],
        1
    ):
        print(f"\n{i}. {food}")
        print(f"   Units Sold: {metrics['units_sold']}")
        print(f"   Revenue: ${metrics['total_revenue']}")
        print(f"   Popularity: {metrics['popularity_score']}%")
    
    # Save merchant report
    merchant_report = {
        'timestamp': datetime.now().isoformat(),
        'demand_forecast': {k: v for k, v in list(demand.items())[:10]},
        'allocation': {k: v for k, v in list(allocation.items())[:3]},
        'route_optimization': route,
        'roi_analysis': roi,
        'performance_metrics': {k: v for k, v in list(performance.items())[:5]}
    }
    
    with open('merchant_report.json', 'w') as f:
        json.dump(merchant_report, f, indent=2)
    
    print("\n✓ Merchant report saved to merchant_report.json")

if __name__ == '__main__':
    demo_merchant_system()
