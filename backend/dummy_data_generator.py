"""
Dummy Data Generator for SNAP Benefit Food Shop Hackathon
Generates realistic user profiles, family structures, order history, and food catalog
based on USDA nutritional guidelines and demographic patterns.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib

# ============================================================================
# PART 1: AGE-SEX NUTRITIONAL REQUIREMENTS (from USDA)
# ============================================================================

USDA_NUTRITIONAL_NEEDS = {
    # Format: (age_min, age_max, gender) -> {calories, protein(g), fiber(g), calcium(mg), iron(mg)}
    'child_1_year': {
        'calories': 900, 'protein': 11, 'fiber': 19, 'calcium': 700, 'iron': 11, 'vitamin_c': 50, 'vitamin_a_rae': 400
    },
    'child_2_3_years': {
        'calories': 1000, 'protein': 13, 'fiber': 19, 'calcium': 700, 'iron': 7, 'vitamin_c': 15, 'vitamin_a_rae': 300
    },
    'child_4_5_years': {
        'calories': 1200, 'protein': 19, 'fiber': 25, 'calcium': 1000, 'iron': 10, 'vitamin_c': 25, 'vitamin_a_rae': 400
    },
    'child_6_8_years': {
        'calories': 1400, 'protein': 19, 'fiber': 25, 'calcium': 1000, 'iron': 10, 'vitamin_c': 45, 'vitamin_a_rae': 500
    },
    'child_9_11_years': {
        'calories': 1600, 'protein': 34, 'fiber': 31, 'calcium': 1300, 'iron': 8, 'vitamin_c': 45, 'vitamin_a_rae': 600
    },
    'teen_female_12_13': {
        'calories': 1600, 'protein': 46, 'fiber': 26, 'calcium': 1300, 'iron': 8, 'vitamin_c': 65, 'vitamin_a_rae': 600
    },
    'teen_female_14_19': {
        'calories': 1800, 'protein': 46, 'fiber': 26, 'calcium': 1300, 'iron': 15, 'vitamin_c': 75, 'vitamin_a_rae': 700
    },
    'adult_female_20_50': {
        'calories': 1800, 'protein': 46, 'fiber': 25, 'calcium': 1000, 'iron': 18, 'vitamin_c': 75, 'vitamin_a_rae': 700
    },
    'adult_female_51_70': {
        'calories': 1600, 'protein': 46, 'fiber': 21, 'calcium': 1200, 'iron': 8, 'vitamin_c': 75, 'vitamin_a_rae': 700
    },
    'senior_female_71_plus': {
        'calories': 1600, 'protein': 46, 'fiber': 21, 'calcium': 1200, 'iron': 8, 'vitamin_c': 75, 'vitamin_a_rae': 700
    },
    'teen_male_12_13': {
        'calories': 1800, 'protein': 34, 'fiber': 31, 'calcium': 1300, 'iron': 8, 'vitamin_c': 45, 'vitamin_a_rae': 600
    },
    'teen_male_14_19': {
        'calories': 2200, 'protein': 52, 'fiber': 38, 'calcium': 1300, 'iron': 11, 'vitamin_c': 75, 'vitamin_a_rae': 900
    },
    'adult_male_20_50': {
        'calories': 2200, 'protein': 56, 'fiber': 38, 'calcium': 1000, 'iron': 8, 'vitamin_c': 90, 'vitamin_a_rae': 900
    },
    'adult_male_51_70': {
        'calories': 2000, 'protein': 56, 'fiber': 30, 'calcium': 1000, 'iron': 8, 'vitamin_c': 90, 'vitamin_a_rae': 900
    },
    'senior_male_71_plus': {
        'calories': 2000, 'protein': 56, 'fiber': 30, 'calcium': 1200, 'iron': 8, 'vitamin_c': 90, 'vitamin_a_rae': 900
    }
}

# ============================================================================
# PART 2: FOOD CATALOG (Simplified USDA foods with nutrition data)
# ============================================================================

FOOD_CATALOG = [
    # Vegetables (High in fiber, low cost)
    {'name': 'Carrots (1 lb)', 'category': 'vegetables', 'price': 0.89, 
     'nutrition': {'calories': 176, 'protein': 4, 'fiber': 9, 'calcium': 96, 'iron': 1.2, 'vitamin_c': 21, 'vitamin_a_rae': 1911}},
    
    {'name': 'Broccoli (1 lb)', 'category': 'vegetables', 'price': 1.49,
     'nutrition': {'calories': 124, 'protein': 12, 'fiber': 8, 'calcium': 240, 'iron': 1.5, 'vitamin_c': 283, 'vitamin_a_rae': 604}},
    
    {'name': 'Spinach (10 oz)', 'category': 'vegetables', 'price': 1.99,
     'nutrition': {'calories': 69, 'protein': 9, 'fiber': 2, 'calcium': 554, 'iron': 6, 'vitamin_c': 28, 'vitamin_a_rae': 943}},
    
    {'name': 'Onions (2 lb)', 'category': 'vegetables', 'price': 0.99,
     'nutrition': {'calories': 180, 'protein': 5, 'fiber': 7, 'calcium': 80, 'iron': 0.5, 'vitamin_c': 20, 'vitamin_a_rae': 0}},
    
    {'name': 'Bell Peppers (3 pack)', 'category': 'vegetables', 'price': 2.49,
     'nutrition': {'calories': 149, 'protein': 5, 'fiber': 5, 'calcium': 40, 'iron': 1, 'vitamin_c': 569, 'vitamin_a_rae': 117}},
    
    # Fruits (Vitamins, fiber, moderate cost)
    {'name': 'Bananas (3 lb)', 'category': 'fruits', 'price': 0.69,
     'nutrition': {'calories': 267, 'protein': 3, 'fiber': 7, 'calcium': 9, 'iron': 0.6, 'vitamin_c': 17, 'vitamin_a_rae': 32}},
    
    {'name': 'Apples (3 lb)', 'category': 'fruits', 'price': 1.99,
     'nutrition': {'calories': 238, 'protein': 0, 'fiber': 12, 'calcium': 11, 'iron': 0.2, 'vitamin_c': 8, 'vitamin_a_rae': 27}},
    
    {'name': 'Oranges (3 lb)', 'category': 'fruits', 'price': 2.49,
     'nutrition': {'calories': 142, 'protein': 3, 'fiber': 6, 'calcium': 74, 'iron': 0.3, 'vitamin_c': 109, 'vitamin_a_rae': 30}},
    
    {'name': 'Frozen Mixed Berries (10 oz)', 'category': 'fruits', 'price': 2.99,
     'nutrition': {'calories': 77, 'protein': 1, 'fiber': 4, 'calcium': 20, 'iron': 0.4, 'vitamin_c': 15, 'vitamin_a_rae': 66}},
    
    # Grains (Low cost, energy dense)
    {'name': 'Brown Rice (2 lb)', 'category': 'grains', 'price': 1.49,
     'nutrition': {'calories': 684, 'protein': 14, 'fiber': 7, 'calcium': 33, 'iron': 1.8, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    {'name': 'Whole Wheat Bread (1 loaf)', 'category': 'grains', 'price': 2.49,
     'nutrition': {'calories': 1264, 'protein': 44, 'fiber': 36, 'calcium': 480, 'iron': 8.4, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    {'name': 'Oats (1 lb)', 'category': 'grains', 'price': 2.99,
     'nutrition': {'calories': 1508, 'protein': 54, 'fiber': 27, 'calcium': 184, 'iron': 8.4, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    {'name': 'Pasta (1 lb)', 'category': 'grains', 'price': 0.99,
     'nutrition': {'calories': 1648, 'protein': 54, 'fiber': 4, 'calcium': 0, 'iron': 4.2, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    # Protein (Essential, higher cost)
    {'name': 'Chicken Breast (2 lb)', 'category': 'protein', 'price': 5.99,
     'nutrition': {'calories': 616, 'protein': 130, 'fiber': 0, 'calcium': 26, 'iron': 1.3, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    {'name': 'Ground Beef (1 lb)', 'category': 'protein', 'price': 4.99,
     'nutrition': {'calories': 894, 'protein': 81, 'fiber': 0, 'calcium': 18, 'iron': 2.4, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    {'name': 'Eggs (1 dozen)', 'category': 'protein', 'price': 2.49,
     'nutrition': {'calories': 715, 'protein': 63, 'fiber': 0, 'calcium': 280, 'iron': 4.8, 'vitamin_c': 0, 'vitamin_a_rae': 320}},
    
    {'name': 'Canned Beans (4 cans)', 'category': 'protein', 'price': 2.49,
     'nutrition': {'calories': 832, 'protein': 60, 'fiber': 44, 'calcium': 320, 'iron': 8, 'vitamin_c': 2, 'vitamin_a_rae': 0}},
    
    {'name': 'Peanut Butter (16 oz)', 'category': 'protein', 'price': 2.99,
     'nutrition': {'calories': 2520, 'protein': 96, 'fiber': 16, 'calcium': 80, 'iron': 3.2, 'vitamin_c': 0, 'vitamin_a_rae': 0}},
    
    # Dairy (Calcium essential, moderate cost)
    {'name': 'Milk (1 gallon)', 'category': 'dairy', 'price': 3.49,
     'nutrition': {'calories': 600, 'protein': 32, 'fiber': 0, 'calcium': 1176, 'iron': 0, 'vitamin_c': 0, 'vitamin_a_rae': 112}},
    
    {'name': 'Yogurt (32 oz)', 'category': 'dairy', 'price': 3.99,
     'nutrition': {'calories': 320, 'protein': 28, 'fiber': 0, 'calcium': 1040, 'iron': 0.4, 'vitamin_c': 1, 'vitamin_a_rae': 32}},
    
    {'name': 'Cheese (8 oz)', 'category': 'dairy', 'price': 3.99,
     'nutrition': {'calories': 896, 'protein': 56, 'fiber': 0, 'calcium': 1408, 'iron': 0.4, 'vitamin_c': 0, 'vitamin_a_rae': 224}},
    
    # Budget-friendly staples
    {'name': 'Canned Tomatoes (4 cans)', 'category': 'vegetables', 'price': 1.99,
     'nutrition': {'calories': 144, 'protein': 7, 'fiber': 4, 'calcium': 120, 'iron': 3.2, 'vitamin_c': 20, 'vitamin_a_rae': 96}},
    
    {'name': 'Frozen Vegetables (2 lb)', 'category': 'vegetables', 'price': 2.49,
     'nutrition': {'calories': 164, 'protein': 12, 'fiber': 12, 'calcium': 96, 'iron': 1.6, 'vitamin_c': 80, 'vitamin_a_rae': 600}},
]

# ============================================================================
# PART 3: HEALTH CONDITIONS & DIETARY RESTRICTIONS
# ============================================================================

HEALTH_CONDITIONS = [
    'diabetes', 'hypertension', 'obesity', 'anemia', 'celiac', 'lactose_intolerant',
    'nut_allergy', 'shellfish_allergy', 'vegetarian', 'vegan', 'kosher', 'halal'
]

DIETARY_RESTRICTIONS_RULES = {
    'diabetes': {
        'avoid': ['pasta', 'bread', 'rice', 'sugar'],  # High glycemic
        'encourage': ['vegetables', 'protein', 'beans'],
        'max_calories_per_meal': 600
    },
    'hypertension': {
        'avoid': ['canned', 'processed'],  # High sodium
        'encourage': ['vegetables', 'whole grains', 'beans'],
        'max_sodium_daily': 2300  # mg
    },
    'anemia': {
        'avoid': [],
        'encourage': ['meat', 'eggs', 'beans', 'spinach'],  # Iron sources
        'min_iron_daily': 18  # mg
    },
    'celiac': {
        'avoid': ['bread', 'pasta'],
        'encourage': ['rice', 'potatoes', 'vegetables'],
    },
    'lactose_intolerant': {
        'avoid': ['milk', 'cheese', 'yogurt'],
        'encourage': ['plant-based milk', 'eggs', 'vegetables'],
    },
    'nut_allergy': {
        'avoid': ['peanut butter'],
        'encourage': ['beans', 'meat', 'seeds'],
    },
    'vegetarian': {
        'avoid': ['meat', 'chicken'],
        'encourage': ['beans', 'eggs', 'dairy', 'vegetables'],
    },
    'vegan': {
        'avoid': ['meat', 'chicken', 'eggs', 'dairy'],
        'encourage': ['beans', 'vegetables', 'nuts', 'grains'],
    }
}

# ============================================================================
# PART 4: DUMMY USER GENERATOR
# ============================================================================

class DummyDataGenerator:
    def __init__(self, num_users=50):
        self.num_users = num_users
        self.users = []
        self.families = []
        self.order_history = []
        self.food_catalog = FOOD_CATALOG.copy()
        
    def get_nutritional_needs(self, age: int, gender: str) -> Dict:
        """Map age and gender to USDA nutritional needs"""
        if age < 1:
            return USDA_NUTRITIONAL_NEEDS['child_1_year']
        elif age <= 3:
            return USDA_NUTRITIONAL_NEEDS['child_2_3_years']
        elif age <= 5:
            return USDA_NUTRITIONAL_NEEDS['child_4_5_years']
        elif age <= 8:
            return USDA_NUTRITIONAL_NEEDS['child_6_8_years']
        elif age <= 11:
            return USDA_NUTRITIONAL_NEEDS['child_9_11_years']
        elif age <= 13:
            return USDA_NUTRITIONAL_NEEDS[f'teen_{gender}_12_13']
        elif age <= 19:
            return USDA_NUTRITIONAL_NEEDS[f'teen_{gender}_14_19']
        elif age <= 50:
            return USDA_NUTRITIONAL_NEEDS[f'adult_{gender}_20_50']
        elif age <= 70:
            return USDA_NUTRITIONAL_NEEDS[f'adult_{gender}_51_70']
        else:
            return USDA_NUTRITIONAL_NEEDS[f'senior_{gender}_71_plus']
    
    def generate_users(self) -> List[Dict]:
        """Generate realistic SNAP benefit users"""
        first_names_f = ['Maria', 'Sandra', 'Jennifer', 'Angela', 'Sarah', 'Michelle', 'Lisa', 'Carmen']
        first_names_m = ['Juan', 'Carlos', 'Miguel', 'David', 'James', 'Michael', 'Robert', 'Jose']
        last_names = ['Garcia', 'Martinez', 'Rodriguez', 'Lopez', 'Johnson', 'Smith', 'Williams', 'Brown']
        
        users = []
        for i in range(self.num_users):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(first_names_m if gender == 'male' else first_names_f)
            last_name = random.choice(last_names)
            
            age = random.randint(18, 75)
            budget = random.choice([50, 75, 100, 150, 200, 300])  # Monthly SNAP benefit in USD
            
            # Health conditions (20% have 1-2 conditions)
            conditions = []
            if random.random() < 0.2:
                num_conditions = random.randint(1, 2)
                conditions = random.sample(HEALTH_CONDITIONS, num_conditions)
            
            user = {
                'id': f'user_{i+1:04d}',
                'name': f'{first_name} {last_name}',
                'age': age,
                'gender': gender,
                'monthly_budget': budget,
                'zip_code': random.choice(['20001', '20002', '20003', '20004', '20005']),  # DC area codes
                'health_conditions': conditions,
                'preferences': [],
                'nutritional_needs': self.get_nutritional_needs(age, gender),
                'created_date': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            }
            users.append(user)
        
        self.users = users
        return users
    
    def generate_families(self) -> List[Dict]:
        """Generate family structures for users"""
        families = []
        
        for user in self.users:
            # 40% of users shop for families
            if random.random() < 0.4:
                num_family_members = random.randint(2, 5)
                
                family_members = []
                # Add the primary user
                family_members.append({
                    'member_id': f'{user["id"]}_self',
                    'relation': 'self',
                    'age': user['age'],
                    'gender': user['gender'],
                    'health_conditions': user['health_conditions'],
                    'nutritional_needs': user['nutritional_needs']
                })
                
                # Add other family members
                for j in range(1, num_family_members):
                    member_age = random.choice(
                        list(range(0, 8)) + [random.randint(10, 17)] + [random.randint(20, 60)]
                    )
                    member_gender = random.choice(['male', 'female'])
                    
                    family_members.append({
                        'member_id': f'{user["id"]}_member_{j}',
                        'relation': random.choice(['spouse', 'child', 'parent', 'sibling']),
                        'age': member_age,
                        'gender': member_gender,
                        'health_conditions': [] if random.random() > 0.15 else [random.choice(HEALTH_CONDITIONS)],
                        'nutritional_needs': self.get_nutritional_needs(member_age, member_gender)
                    })
                
                family = {
                    'id': f'family_{user["id"]}',
                    'primary_user_id': user['id'],
                    'total_members': len(family_members),
                    'members': family_members,
                    'combined_monthly_budget': user['monthly_budget'],  # Same budget for whole family
                    'created_date': user['created_date']
                }
                families.append(family)
                
                # Update user to reference family
                user['family_id'] = family['id']
        
        self.families = families
        return families
    
    def generate_order_history(self) -> List[Dict]:
        """Generate past purchase history"""
        orders = []
        order_id = 1
        
        for user in self.users:
            # Each user has 2-8 past orders
            num_orders = random.randint(2, 8)
            
            for order_num in range(num_orders):
                order_date = datetime.now() - timedelta(days=random.randint(1, 180))
                
                # Select 3-8 random items
                num_items = random.randint(3, 8)
                items = random.sample(self.food_catalog, min(num_items, len(self.food_catalog)))
                
                total_price = sum(item['price'] for item in items)
                
                # Filter for dietary restrictions
                if user['health_conditions']:
                    items = [item for item in items 
                           if not any(avoid in item['name'].lower() 
                                    for condition in user['health_conditions']
                                    for avoid in DIETARY_RESTRICTIONS_RULES.get(condition, {}).get('avoid', []))]
                
                order = {
                    'id': f'order_{order_id:05d}',
                    'user_id': user['id'],
                    'family_id': user.get('family_id'),
                    'items': [{'name': item['name'], 'price': item['price']} for item in items],
                    'total': round(total_price, 2),
                    'order_date': order_date.isoformat(),
                    'quantity_purchased': num_items
                }
                orders.append(order)
                order_id += 1
        
        self.order_history = orders
        return orders
    
    def generate_all_data(self) -> Dict:
        """Generate all dummy data"""
        print(f"Generating {self.num_users} users...")
        self.generate_users()
        
        print("Generating family structures...")
        self.generate_families()
        
        print("Generating order history...")
        self.generate_order_history()
        
        return {
            'users': self.users,
            'families': self.families,
            'orders': self.order_history,
            'food_catalog': self.food_catalog,
            'metadata': {
                'total_users': len(self.users),
                'total_families': len(self.families),
                'total_orders': len(self.order_history),
                'total_foods': len(self.food_catalog),
                'generated_at': datetime.now().isoformat(),
                'usda_thrifty_food_plan': 'January 2026 baseline used for nutritional requirements'
            }
        }

# ============================================================================
# PART 5: JSON EXPORT & DISPLAY
# ============================================================================

def export_dummy_data(output_file: str = 'dummy_data.json'):
    """Generate and export dummy data to JSON"""
    generator = DummyDataGenerator(num_users=50)
    data = generator.generate_all_data()
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Dummy data exported to {output_file}")
    print(f"  - Users: {len(data['users'])}")
    print(f"  - Families: {len(data['families'])}")
    print(f"  - Order History: {len(data['orders'])}")
    print(f"  - Food Catalog: {len(data['food_catalog'])}")
    
    return data

def print_sample_data(data: Dict):
    """Print sample records for inspection"""
    print("\n" + "="*80)
    print("SAMPLE USER RECORD")
    print("="*80)
    print(json.dumps(data['users'][0], indent=2))
    
    print("\n" + "="*80)
    print("SAMPLE FAMILY RECORD")
    print("="*80)
    if data['families']:
        print(json.dumps(data['families'][0], indent=2))
    
    print("\n" + "="*80)
    print("SAMPLE ORDER RECORD")
    print("="*80)
    print(json.dumps(data['orders'][0], indent=2))
    
    print("\n" + "="*80)
    print("SAMPLE FOOD CATALOG ITEMS (First 3)")
    print("="*80)
    print(json.dumps(data['food_catalog'][:3], indent=2))

if __name__ == '__main__':
    # Generate and export
    data = export_dummy_data('dummy_data.json')
    
    # Print samples
    print_sample_data(data)
    
    # Statistics
    print("\n" + "="*80)
    print("DATA STATISTICS")
    print("="*80)
    avg_budget = sum(u['monthly_budget'] for u in data['users']) / len(data['users'])
    users_with_conditions = sum(1 for u in data['users'] if u['health_conditions'])
    
    print(f"Average monthly budget: ${avg_budget:.2f}")
    print(f"Users with health conditions: {users_with_conditions}/{len(data['users'])}")
    print(f"Families (shopping for multiple): {len(data['families'])}/{len(data['users'])}")
    print(f"Average orders per user: {len(data['orders'])/len(data['users']):.1f}")
    print(f"Average items per order: {sum(o['quantity_purchased'] for o in data['orders'])/len(data['orders']):.1f}")
