"""
Digital Signage & Food Truck Display System
Manages order ready notifications and advertising content on truck displays
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from collections import defaultdict

# ============================================================================
# PART 1: DISPLAY CONTENT MANAGEMENT
# ============================================================================

class ContentType(Enum):
    ORDER_READY = "order_ready"
    ADVERTISEMENT = "advertisement"
    EDUCATIONAL = "educational"
    ANNOUNCEMENT = "announcement"
    NUTRITION_TIP = "nutrition_tip"

class DisplayContent:
    """Manages content displayed on food truck screens"""
    
    def __init__(self):
        self.content_queue = []
        self.display_history = []
        self.content_id_counter = 0
    
    def create_order_ready_display(self,
                                  order_id: str,
                                  user_name: str,
                                  pickup_time: str,
                                  items: List[str],
                                  duration_seconds: int = 30) -> Dict:
        """
        Create a display for "Order Ready for Pickup"
        
        Shown when customer arrives at pickup point
        """
        
        content = {
            'id': f"content_{self.content_id_counter}",
            'type': ContentType.ORDER_READY.value,
            'order_id': order_id,
            'user_name': user_name,
            'pickup_time': pickup_time,
            'items': items,
            'display_duration': duration_seconds,
            'created_at': datetime.now().isoformat(),
            'priority': 'high',
            'layout': {
                'background_color': '#2ecc71',  # Green
                'text_color': '#ffffff',
                'title': f"ORDER READY! 🎉",
                'message': f"{user_name}, your order is ready for pickup!",
                'details': f"Items: {', '.join(items)}",
                'footer': f"Pickup Time: {pickup_time}"
            },
            'animation': 'slide_in_from_left'
        }
        
        self.content_id_counter += 1
        return content
    
    def create_advertisement(self,
                            business_name: str,
                            business_type: str,
                            offer: str,
                            image_url: str,
                            duration_seconds: int = 15,
                            revenue: float = 0.0) -> Dict:
        """
        Create advertisement content for local businesses
        
        Generates revenue stream for the operation
        Displayed during idle times between orders
        """
        
        content = {
            'id': f"content_{self.content_id_counter}",
            'type': ContentType.ADVERTISEMENT.value,
            'business_name': business_name,
            'business_type': business_type,
            'offer': offer,
            'image_url': image_url,
            'display_duration': duration_seconds,
            'created_at': datetime.now().isoformat(),
            'priority': 'medium',
            'revenue': revenue,
            'campaign_id': f"campaign_{business_name.replace(' ', '_')}",
            'layout': {
                'background_color': '#3498db',  # Blue
                'text_color': '#ffffff',
                'title': business_name,
                'message': offer,
                'image_position': 'center'
            },
            'animation': 'fade_in',
            'tracking': {
                'impressions': 0,
                'interactions': 0,
                'qr_code': f"https://business.local/{business_name.replace(' ', '_')}"
            }
        }
        
        self.content_id_counter += 1
        return content
    
    def create_nutrition_tip(self,
                            tip: str,
                            category: str,
                            duration_seconds: int = 10) -> Dict:
        """
        Create educational content about nutrition
        
        Helps users make better food choices
        Positioned as value-add (not ad)
        """
        
        content = {
            'id': f"content_{self.content_id_counter}",
            'type': ContentType.NUTRITION_TIP.value,
            'tip': tip,
            'category': category,
            'display_duration': duration_seconds,
            'created_at': datetime.now().isoformat(),
            'priority': 'low',
            'layout': {
                'background_color': '#e74c3c',  # Red/Orange for health
                'text_color': '#ffffff',
                'title': '💡 Nutrition Tip',
                'message': tip
            },
            'animation': 'fade_in',
            'tracking': {
                'displays': 0,
                'engagement': 'passive'
            }
        }
        
        self.content_id_counter += 1
        return content
    
    def add_to_queue(self, content: Dict):
        """Add content to display queue"""
        self.content_queue.append(content)
    
    def queue_order_display(self,
                           order_id: str,
                           user_name: str,
                           pickup_time: str,
                           items: List[str]):
        """Priority method to queue order ready display"""
        content = self.create_order_ready_display(order_id, user_name, pickup_time, items)
        # Insert at front of queue (high priority)
        self.content_queue.insert(0, content)
    
    def get_next_content(self) -> Optional[Dict]:
        """Get next content to display"""
        if self.content_queue:
            content = self.content_queue.pop(0)
            self.display_history.append({
                'content_id': content['id'],
                'type': content['type'],
                'displayed_at': datetime.now().isoformat()
            })
            return content
        return None
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'queue_length': len(self.content_queue),
            'pending_orders': sum(1 for c in self.content_queue if c['type'] == ContentType.ORDER_READY.value),
            'pending_ads': sum(1 for c in self.content_queue if c['type'] == ContentType.ADVERTISEMENT.value),
            'estimated_duration_minutes': sum(c['display_duration'] for c in self.content_queue) / 60
        }

# ============================================================================
# PART 2: ADVERTISEMENT MANAGEMENT & REVENUE
# ============================================================================

class AdvertisementManager:
    """Manages ad campaigns and revenue generation"""
    
    def __init__(self):
        self.campaigns = {}
        self.partner_businesses = {}
        self.pricing_model = {
            'per_impression': 0.50,      # $0.50 per display
            'per_interaction': 2.00,     # $2.00 per click/scan
            'daily_package': 25.00,      # $25/day for unlimited displays
            'weekly_package': 140.00,    # $140/week
            'monthly_package': 500.00    # $500/month
        }
    
    def add_partner_business(self,
                            business_id: str,
                            name: str,
                            type_category: str,
                            location: str,
                            contact: str) -> Dict:
        """Register a local business as ad partner"""
        
        business = {
            'business_id': business_id,
            'name': name,
            'type': type_category,
            'location': location,
            'contact': contact,
            'registered_at': datetime.now().isoformat(),
            'active_campaigns': [],
            'total_revenue': 0.0,
            'total_impressions': 0
        }
        
        self.partner_businesses[business_id] = business
        return business
    
    def create_campaign(self,
                       campaign_id: str,
                       business_id: str,
                       offer: str,
                       image_url: str,
                       duration_days: int,
                       pricing_tier: str = 'per_impression') -> Dict:
        """Create an advertising campaign"""
        
        if business_id not in self.partner_businesses:
            raise ValueError(f"Business {business_id} not found")
        
        # Calculate pricing
        if pricing_tier == 'daily_package':
            cost = self.pricing_model['daily_package'] * duration_days
            projected_revenue_model = 'unlimited'
        elif pricing_tier == 'weekly_package':
            cost = self.pricing_model['weekly_package'] * (duration_days / 7)
            projected_revenue_model = 'unlimited'
        else:
            cost = 0  # Per impression - cost depends on actual displays
            projected_revenue_model = 'variable'
        
        campaign = {
            'campaign_id': campaign_id,
            'business_id': business_id,
            'offer': offer,
            'image_url': image_url,
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'duration_days': duration_days,
            'pricing_tier': pricing_tier,
            'total_cost': cost,
            'pricing_model': projected_revenue_model,
            'status': 'active',
            'metrics': {
                'impressions': 0,
                'interactions': 0,
                'ctr': 0.0,  # Click-through rate
                'conversion': 0.0
            }
        }
        
        self.campaigns[campaign_id] = campaign
        self.partner_businesses[business_id]['active_campaigns'].append(campaign_id)
        
        return campaign
    
    def record_impression(self, campaign_id: str):
        """Record when an ad is displayed"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id]['metrics']['impressions'] += 1
    
    def record_interaction(self, campaign_id: str):
        """Record when user interacts with ad (click, QR code scan)"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id]['metrics']['interactions'] += 1
            campaign = self.campaigns[campaign_id]
            
            # Calculate CTR
            impressions = campaign['metrics']['impressions']
            if impressions > 0:
                campaign['metrics']['ctr'] = (campaign['metrics']['interactions'] / impressions)
    
    def calculate_revenue(self) -> Dict:
        """Calculate total revenue from ad campaigns"""
        
        total_revenue = 0.0
        revenue_by_business = defaultdict(float)
        revenue_by_model = defaultdict(float)
        
        for campaign_id, campaign in self.campaigns.items():
            campaign_revenue = 0
            
            if campaign['pricing_model'] == 'unlimited':
                # Fixed tier pricing
                campaign_revenue = campaign['total_cost']
            else:
                # Per-impression or per-interaction
                impressions = campaign['metrics']['impressions']
                interactions = campaign['metrics']['interactions']
                
                if campaign['pricing_tier'] == 'per_impression':
                    campaign_revenue = impressions * self.pricing_model['per_impression']
                elif campaign['pricing_tier'] == 'per_interaction':
                    campaign_revenue = interactions * self.pricing_model['per_interaction']
            
            total_revenue += campaign_revenue
            revenue_by_business[campaign['business_id']] += campaign_revenue
            revenue_by_model[campaign['pricing_model']] += campaign_revenue
        
        return {
            'total_revenue': round(total_revenue, 2),
            'active_campaigns': len(self.campaigns),
            'revenue_by_business': {bid: round(rev, 2) for bid, rev in revenue_by_business.items()},
            'revenue_by_model': {mod: round(rev, 2) for mod, rev in revenue_by_model.items()},
            'average_revenue_per_campaign': round(total_revenue / len(self.campaigns), 2) if self.campaigns else 0
        }
    
    def get_campaign_roi(self, campaign_id: str) -> Dict:
        """Calculate ROI for a specific campaign"""
        if campaign_id not in self.campaigns:
            return {'error': 'Campaign not found'}
        
        campaign = self.campaigns[campaign_id]
        
        # Revenue calculations
        if campaign['pricing_model'] == 'unlimited':
            revenue = campaign['total_cost']  # Already paid
        else:
            impressions = campaign['metrics']['impressions']
            interactions = campaign['metrics']['interactions']
            
            if campaign['pricing_tier'] == 'per_impression':
                revenue = impressions * self.pricing_model['per_impression']
            else:
                revenue = interactions * self.pricing_model['per_interaction']
        
        cost = campaign['total_cost'] if campaign['pricing_model'] == 'unlimited' else 0
        roi = ((revenue - cost) / max(cost, 0.01) * 100) if cost > 0 else 0
        
        return {
            'campaign_id': campaign_id,
            'revenue': round(revenue, 2),
            'cost': round(cost, 2),
            'roi_percent': round(roi, 2),
            'impressions': campaign['metrics']['impressions'],
            'interactions': campaign['metrics']['interactions'],
            'ctr': round(campaign['metrics']['ctr'] * 100, 2),
            'cost_per_impression': round(cost / max(campaign['metrics']['impressions'], 1), 4),
            'cost_per_interaction': round(cost / max(campaign['metrics']['interactions'], 1), 2)
        }

# ============================================================================
# PART 3: FOOD TRUCK DISPLAY MANAGEMENT
# ============================================================================

class FoodTruckDisplay:
    """Manages the complete display system on a food truck"""
    
    def __init__(self, truck_id: str, location: str):
        self.truck_id = truck_id
        self.location = location
        self.display_content = DisplayContent()
        self.ad_manager = AdvertisementManager()
        self.current_display = None
        self.rotation_schedule = []
    
    def update_location(self, new_location: str):
        """Update truck location"""
        self.location = new_location
    
    def display_order_ready(self,
                           order_id: str,
                           user_name: str,
                           pickup_time: str,
                           items: List[str]):
        """Priority: immediately display order ready notification"""
        self.display_content.queue_order_display(order_id, user_name, pickup_time, items)
        self.refresh_display()
    
    def schedule_advertisement(self,
                              campaign_id: str,
                              business_name: str,
                              offer: str,
                              image_url: str,
                              frequency: str = 'idle'):
        """
        Schedule ad to display
        
        frequency: 'idle' (between orders), 'periodic', 'continuous'
        """
        
        ad_content = self.display_content.create_advertisement(
            business_name,
            'partner_business',
            offer,
            image_url
        )
        
        if frequency == 'idle':
            # Will show when queue is empty
            self.display_content.add_to_queue(ad_content)
    
    def schedule_nutrition_tips(self):
        """Add nutrition education content to rotation"""
        
        nutrition_tips = [
            ("Carrots are rich in Vitamin A, essential for eye health", "vegetables"),
            ("Whole grains provide more fiber than refined grains", "grains"),
            ("Beans are an affordable protein source with high fiber", "protein"),
            ("Dark leafy greens are nutrient-dense and low-calorie", "vegetables"),
            ("Eggs are complete proteins with all amino acids", "protein"),
        ]
        
        for tip, category in nutrition_tips:
            content = self.display_content.create_nutrition_tip(tip, category)
            self.display_content.add_to_queue(content)
    
    def refresh_display(self):
        """Get next content and update display"""
        self.current_display = self.display_content.get_next_content()
        return self.current_display
    
    def get_display_status(self) -> Dict:
        """Get current display status"""
        
        return {
            'truck_id': self.truck_id,
            'location': self.location,
            'current_display': self.current_display,
            'queue_status': self.display_content.get_queue_status(),
            'ad_revenue': self.ad_manager.calculate_revenue(),
            'total_ads_displayed': len(self.display_content.display_history),
            'last_update': datetime.now().isoformat()
        }

# ============================================================================
# PART 4: DEMO & EXAMPLE USAGE
# ============================================================================

def demo_display_system():
    """Demonstrate the digital signage system"""
    
    print("="*80)
    print("DIGITAL SIGNAGE & ADVERTISEMENT SYSTEM DEMO")
    print("="*80)
    
    # Initialize food truck display
    truck = FoodTruckDisplay(
        truck_id="truck_01",
        location="Downtown DC - 5th St & Pennsylvania Ave"
    )
    
    # ---- 1. ORDER READY NOTIFICATIONS ----
    print("\n1. ORDER READY NOTIFICATIONS")
    print("-" * 80)
    
    truck.display_order_ready(
        order_id="order_12345",
        user_name="Michelle Garcia",
        pickup_time="2:15 PM",
        items=["Carrots (1 lb)", "Eggs (1 dozen)", "Spinach"]
    )
    
    print(f"\nOrder Ready Display Created:")
    if truck.current_display:
        print(f"  Title: {truck.current_display['layout']['title']}")
        print(f"  Message: {truck.current_display['layout']['message']}")
        print(f"  Items: {', '.join(truck.current_display['items'])}")
        print(f"  Duration: {truck.current_display['display_duration']} seconds")
    
    # ---- 2. ADVERTISEMENT MANAGEMENT ----
    print("\n" + "="*80)
    print("2. ADVERTISEMENT MANAGEMENT")
    print("-" * 80)
    
    # Register local business partners
    ad_manager = truck.ad_manager
    
    ad_manager.add_partner_business(
        business_id="biz_001",
        name="Dave's Corner Store",
        type_category="grocery",
        location="Near Metro Station",
        contact="dave@cornerstore.local"
    )
    
    ad_manager.add_partner_business(
        business_id="biz_002",
        name="Healthy Juice Bar",
        type_category="beverage",
        location="Downtown",
        contact="juice@healthybar.local"
    )
    
    print(f"\nRegistered {len(ad_manager.partner_businesses)} partner businesses")
    
    # Create campaigns
    campaigns = []
    
    campaign_1 = ad_manager.create_campaign(
        campaign_id="camp_001",
        business_id="biz_001",
        offer="Fresh Produce Specials - 20% Off This Week!",
        image_url="assets/daves_store_promo.jpg",
        duration_days=7,
        pricing_tier='daily_package'
    )
    campaigns.append(campaign_1)
    
    campaign_2 = ad_manager.create_campaign(
        campaign_id="camp_002",
        business_id="biz_002",
        offer="Vitamin-Packed Smoothies - Try Our Green Detox!",
        image_url="assets/juice_bar_special.jpg",
        duration_days=7,
        pricing_tier='daily_package'
    )
    campaigns.append(campaign_2)
    
    print(f"\nActive Campaigns: {len(campaigns)}")
    for campaign in campaigns:
        print(f"\n  Campaign: {campaign['campaign_id']}")
        print(f"    Business: {ad_manager.partner_businesses[campaign['business_id']]['name']}")
        print(f"    Offer: {campaign['offer']}")
        print(f"    Duration: {campaign['duration_days']} days")
        print(f"    Pricing: {campaign['pricing_tier']}")
        if campaign['pricing_model'] == 'unlimited':
            print(f"    Cost: ${campaign['total_cost']}")
    
    # Simulate ad displays and interactions
    print(f"\n\nSimulating Ad Campaign Performance:")
    
    # Campaign 1: 100 impressions, 5 clicks
    for _ in range(100):
        ad_manager.record_impression('camp_001')
    for _ in range(5):
        ad_manager.record_interaction('camp_001')
    
    # Campaign 2: 80 impressions, 8 clicks
    for _ in range(80):
        ad_manager.record_impression('camp_002')
    for _ in range(8):
        ad_manager.record_interaction('camp_002')
    
    print(f"\n  Campaign 1 Performance:")
    roi_1 = ad_manager.get_campaign_roi('camp_001')
    print(f"    Impressions: {roi_1['impressions']}")
    print(f"    Interactions: {roi_1['interactions']}")
    print(f"    CTR: {roi_1['ctr']}%")
    print(f"    Cost per Impression: ${roi_1['cost_per_impression']}")
    
    print(f"\n  Campaign 2 Performance:")
    roi_2 = ad_manager.get_campaign_roi('camp_002')
    print(f"    Impressions: {roi_2['impressions']}")
    print(f"    Interactions: {roi_2['interactions']}")
    print(f"    CTR: {roi_2['ctr']}%")
    print(f"    Cost per Impression: ${roi_2['cost_per_impression']}")
    
    # ---- 3. REVENUE ANALYSIS ----
    print("\n" + "="*80)
    print("3. REVENUE ANALYSIS")
    print("-" * 80)
    
    revenue = ad_manager.calculate_revenue()
    
    print(f"\nAdvertising Revenue Report:")
    print(f"  Total Revenue: ${revenue['total_revenue']}")
    print(f"  Active Campaigns: {revenue['active_campaigns']}")
    print(f"  Avg Revenue per Campaign: ${revenue['average_revenue_per_campaign']}")
    print(f"\n  Revenue Breakdown by Business:")
    for biz_id, amount in revenue['revenue_by_business'].items():
        biz_name = ad_manager.partner_businesses[biz_id]['name']
        print(f"    {biz_name}: ${amount}")
    
    # ---- 4. DISPLAY SYSTEM STATUS ----
    print("\n" + "="*80)
    print("4. FOOD TRUCK DISPLAY SYSTEM STATUS")
    print("-" * 80)
    
    # Schedule some content
    truck.schedule_advertisement(
        'camp_001',
        'Dave\'s Corner Store',
        'Fresh Produce Specials - 20% Off!',
        'assets/daves_store.jpg'
    )
    
    truck.schedule_nutrition_tips()
    
    status = truck.get_display_status()
    
    print(f"\nFood Truck Display Status:")
    print(f"  Truck ID: {status['truck_id']}")
    print(f"  Location: {status['location']}")
    print(f"  Queue Length: {status['queue_status']['queue_length']}")
    print(f"  Pending Orders: {status['queue_status']['pending_orders']}")
    print(f"  Pending Ads: {status['queue_status']['pending_ads']}")
    print(f"  Est. Display Duration: {status['queue_status']['estimated_duration_minutes']:.1f} min")
    print(f"\n  Ad Revenue This Period: ${status['ad_revenue']['total_revenue']}")
    print(f"  Total Ads Displayed: {status['total_ads_displayed']}")
    
    # Save display system report
    report = {
        'timestamp': datetime.now().isoformat(),
        'truck_id': truck.truck_id,
        'location': truck.location,
        'campaigns': campaigns,
        'revenue_summary': revenue,
        'display_status': {
            'queue_length': status['queue_status']['queue_length'],
            'pending_orders': status['queue_status']['pending_orders'],
            'pending_ads': status['queue_status']['pending_ads']
        }
    }
    
    with open('display_system_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Display system report saved to display_system_report.json")

if __name__ == '__main__':
    demo_display_system()
