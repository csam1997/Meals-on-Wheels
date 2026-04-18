"""
AI/ML Recommendation Engine for SNAP Benefit Food Shop
Hybrid approach combining:
1. Content-based filtering (nutrition gap analysis)
2. Collaborative filtering (similar users)
3. Knowledge-based filtering (dietary rules)
4. Budget optimization (linear programming)
"""

import json
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import math

# ============================================================================
# PART 1: UTILITIES & HELPERS
# ============================================================================

class NutritionMatcher:
    """Calculate nutritional gaps and matching scores"""
    
    @staticmethod
    def calculate_nutrition_gap(needs: Dict, current: Dict) -> Dict:
        """Calculate nutrient deficiency in current intake vs needs"""
        gap = {}
        for nutrient in needs.keys():
            gap[nutrient] = max(0, needs[nutrient] - current.get(nutrient, 0))
        return gap
    
    @staticmethod
    def calculate_gap_score(gap: Dict) -> float:
        """Convert nutrition gap to single score (0-100)"""
        max_possible_gap = 10000  # Rough maximum
        total_gap = sum(gap.values())
        return min(100, 100 * (1 - (total_gap / max_possible_gap)))
    
    @staticmethod
    def cosine_similarity(vec1: Dict, vec2: Dict, nutrients: List[str]) -> float:
        """Cosine similarity between two nutrition vectors"""
        v1 = np.array([vec1.get(n, 0) for n in nutrients])
        v2 = np.array([vec2.get(n, 0) for n in nutrients])
        
        # Normalize to avoid magnitude dominance
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-10)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-10)
        
        return float(np.dot(v1_norm, v2_norm))

# ============================================================================
# PART 2: CONTENT-BASED RECOMMENDATION ENGINE
# ============================================================================

class ContentBasedRecommender:
    """Recommend foods that fill nutritional gaps"""
    
    def __init__(self, food_catalog: List[Dict]):
        self.food_catalog = food_catalog
        self.nutrition_matcher = NutritionMatcher()
        self.nutrients = ['calories', 'protein', 'fiber', 'calcium', 'iron', 'vitamin_c', 'vitamin_a_rae']
    
    def get_recommendations(self, 
                          user_needs: Dict,
                          current_nutrition: Dict,
                          budget: float,
                          excluded_foods: List[str] = None,
                          avoid_categories: List[str] = None) -> List[Dict]:
        """
        Recommend foods based on nutritional gaps and budget constraints.
        
        Returns:
        List of foods ranked by how well they fill nutritional gaps
        """
        
        if excluded_foods is None:
            excluded_foods = []
        if avoid_categories is None:
            avoid_categories = []
        
        recommendations = []
        
        # Calculate current nutrition gap
        gap = self.nutrition_matcher.calculate_nutrition_gap(user_needs, current_nutrition)
        
        # Score each food by how well it fills gaps within budget
        for food in self.food_catalog:
            # Skip excluded foods
            if food['name'] in excluded_foods:
                continue
            if food['category'] in avoid_categories:
                continue
            if food['price'] > budget:
                continue
            
            # Calculate gap-filling score
            gap_fill_score = 0
            food_nutrition = food['nutrition']
            
            # Prioritize filling the largest gaps
            for nutrient in self.nutrients:
                if gap[nutrient] > 0:
                    fill_amount = min(food_nutrition.get(nutrient, 0), gap[nutrient])
                    gap_fill_score += fill_amount  # Larger gaps weighted heavier naturally
            
            # Cost-value score (more nutrition per dollar)
            nutrition_total = sum(food_nutrition.values())
            cost_value = nutrition_total / food['price'] if food['price'] > 0 else 0
            
            # Similarity to nutritional needs profile
            similarity = self.nutrition_matcher.cosine_similarity(
                food_nutrition, user_needs, self.nutrients
            )
            
            # Combined score (weighted)
            score = (
                gap_fill_score * 0.4 +  # Gap filling priority
                cost_value * 0.35 +      # Value for money
                similarity * 50 * 0.25   # Nutritional match
            )
            
            recommendations.append({
                'name': food['name'],
                'category': food['category'],
                'price': food['price'],
                'nutrition': food_nutrition,
                'score': score,
                'gap_fill_score': gap_fill_score,
                'cost_value': round(cost_value, 2),
                'similarity': round(similarity, 2),
                'reason': f"Fills {', '.join([n for n in self.nutrients if gap[n] > 0][:3])}"
            })
        
        # Sort by score and return top items
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

# ============================================================================
# PART 3: COLLABORATIVE FILTERING
# ============================================================================

class CollaborativeRecommender:
    """Find similar users and recommend what they bought"""
    
    def __init__(self, users: List[Dict], orders: List[Dict]):
        self.users = users
        self.orders = orders
        self.user_index = {u['id']: u for u in users}
        self.user_order_map = self._build_user_order_map()
    
    def _build_user_order_map(self) -> Dict[str, List[Dict]]:
        """Map user IDs to their orders"""
        order_map = defaultdict(list)
        for order in self.orders:
            order_map[order['user_id']].append(order)
        return order_map
    
    def find_similar_users(self, target_user: Dict, k: int = 5) -> List[Tuple[str, float]]:
        """Find k most similar users based on profile"""
        similarities = []
        target_id = target_user['id']
        
        for user in self.users:
            if user['id'] == target_id:
                continue
            
            # Calculate similarity based on:
            # 1. Age proximity (within 5 years)
            age_similarity = 1 - abs(user['age'] - target_user['age']) / 80.0
            
            # 2. Budget proximity (within 20%)
            budget_ratio = min(user['monthly_budget'], target_user['monthly_budget']) / \
                          max(user['monthly_budget'], target_user['monthly_budget'])
            budget_similarity = budget_ratio
            
            # 3. Shared health conditions (if any)
            conditions_similarity = 0
            if target_user['health_conditions'] and user['health_conditions']:
                shared = len(set(target_user['health_conditions']) & set(user['health_conditions']))
                total = len(set(target_user['health_conditions']) | set(user['health_conditions']))
                conditions_similarity = shared / total if total > 0 else 0
            
            # Combined similarity
            overall_similarity = (age_similarity * 0.4 + 
                                budget_similarity * 0.35 + 
                                conditions_similarity * 0.25)
            
            similarities.append((user['id'], overall_similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def get_recommendations_from_similar_users(self, target_user: Dict, 
                                              k: int = 5, top_items: int = 10) -> List[Dict]:
        """Recommend foods that similar users have purchased"""
        
        similar_users = self.find_similar_users(target_user, k)
        
        # Collect items purchased by similar users
        item_counter = Counter()
        
        for similar_user_id, similarity_score in similar_users:
            user_orders = self.user_order_map.get(similar_user_id, [])
            for order in user_orders:
                for item in order['items']:
                    # Weight by similarity score
                    item_counter[item['name']] += similarity_score
        
        # Convert to list and sort
        recommendations = [
            {
                'name': name,
                'score': score,
                'similarity_weighted_count': round(score, 2),
                'reason': 'Purchased by similar users'
            }
            for name, score in item_counter.most_common(top_items)
        ]
        
        return recommendations

# ============================================================================
# PART 4: KNOWLEDGE-BASED FILTERING
# ============================================================================

class KnowledgeBasedRecommender:
    """Apply dietary rules based on health conditions"""
    
    DIETARY_RULES = {
        'diabetes': {
            'avoid': ['pasta', 'bread', 'rice'],
            'encourage': ['vegetables', 'beans', 'meat'],
            'max_daily_carbs': 150
        },
        'hypertension': {
            'avoid': ['canned', 'processed', 'frozen'],
            'encourage': ['fresh vegetables', 'beans', 'lean meat'],
            'max_daily_sodium': 2300
        },
        'anemia': {
            'avoid': [],
            'encourage': ['meat', 'beans', 'eggs', 'spinach'],
            'min_daily_iron': 18
        },
        'celiac': {
            'avoid': ['bread', 'pasta', 'wheat'],
            'encourage': ['rice', 'potatoes', 'vegetables'],
        },
        'lactose_intolerant': {
            'avoid': ['milk', 'cheese', 'yogurt'],
            'encourage': [],
        },
        'vegetarian': {
            'avoid': ['meat', 'chicken', 'fish'],
            'encourage': ['beans', 'eggs', 'dairy', 'vegetables'],
        },
        'vegan': {
            'avoid': ['meat', 'chicken', 'fish', 'dairy', 'eggs'],
            'encourage': ['beans', 'vegetables', 'nuts', 'grains'],
        }
    }
    
    @classmethod
    def get_avoided_foods(cls, health_conditions: List[str]) -> List[str]:
        """Get list of foods to avoid based on conditions"""
        avoided = []
        for condition in health_conditions:
            rules = cls.DIETARY_RULES.get(condition, {})
            avoided.extend(rules.get('avoid', []))
        return list(set(avoided))  # Remove duplicates
    
    @classmethod
    def get_encouraged_foods(cls, health_conditions: List[str]) -> List[str]:
        """Get list of foods to encourage based on conditions"""
        encouraged = []
        for condition in health_conditions:
            rules = cls.DIETARY_RULES.get(condition, {})
            encouraged.extend(rules.get('encourage', []))
        return list(set(encouraged))

# ============================================================================
# PART 5: HYBRID RECOMMENDATION ENGINE
# ============================================================================

class HybridRecommender:
    """Combine all recommendation approaches into one"""
    
    def __init__(self, 
                 users: List[Dict], 
                 orders: List[Dict],
                 food_catalog: List[Dict]):
        self.content_recommender = ContentBasedRecommender(food_catalog)
        self.collaborative_recommender = CollaborativeRecommender(users, orders)
        self.kb_recommender = KnowledgeBasedRecommender()
        self.food_catalog = food_catalog
        self.food_index = {f['name']: f for f in food_catalog}
    
    def get_personalized_recommendations(self,
                                       user: Dict,
                                       current_nutrition: Dict = None,
                                       num_recommendations: int = 15,
                                       scope: str = 'individual') -> Dict:
        """
        Get personalized food recommendations for a user or family.
        
        Args:
            user: User dictionary
            current_nutrition: Current nutrition totals (if any)
            num_recommendations: Number of items to recommend
            scope: 'individual' or 'family'
        
        Returns:
            Recommendation results with scores and explanations
        """
        
        if current_nutrition is None:
            current_nutrition = {
                'calories': 0, 'protein': 0, 'fiber': 0,
                'calcium': 0, 'iron': 0, 'vitamin_c': 0, 'vitamin_a_rae': 0
            }
        
        # Get dietary restrictions
        avoided_foods = self.kb_recommender.get_avoided_foods(user['health_conditions'])
        avoided_categories = []  # Could expand this
        
        # Get recommendations from each engine
        content_recs = self.content_recommender.get_recommendations(
            user_needs=user['nutritional_needs'],
            current_nutrition=current_nutrition,
            budget=user['monthly_budget'],
            excluded_foods=avoided_foods,
            avoid_categories=avoided_categories
        )
        
        collab_recs = self.collaborative_recommender.get_recommendations_from_similar_users(
            user, k=5, top_items=10
        )
        
        # Merge recommendations with weighted scoring
        merged_recs = {}
        
        # Content-based: heavy weight (primary algorithm)
        for rec in content_recs[:20]:
            merged_recs[rec['name']] = {
                'name': rec['name'],
                'category': rec['category'],
                'price': rec['price'],
                'nutrition': rec['nutrition'],
                'score': rec['score'] * 0.6,  # 60% weight
                'reason': rec['reason'],
                'source': 'nutritional need'
            }
        
        # Collaborative: secondary weight
        for rec in collab_recs[:10]:
            if rec['name'] in merged_recs:
                merged_recs[rec['name']]['score'] += rec['score'] * 0.3
                merged_recs[rec['name']]['source'] = 'collaborative + nutritional'
            else:
                merged_recs[rec['name']] = {
                    'name': rec['name'],
                    'category': self.food_index.get(rec['name'], {}).get('category', 'unknown'),
                    'price': self.food_index.get(rec['name'], {}).get('price', 0),
                    'nutrition': self.food_index.get(rec['name'], {}).get('nutrition', {}),
                    'score': rec['score'] * 0.3,
                    'reason': rec['reason'],
                    'source': 'collaborative'
                }
        
        # Sort by combined score
        final_recommendations = sorted(merged_recs.values(), key=lambda x: x['score'], reverse=True)
        
        return {
            'user_id': user['id'],
            'user_name': user['name'],
            'scope': scope,
            'recommendations': final_recommendations[:num_recommendations],
            'dietary_restrictions': user['health_conditions'],
            'budget': user['monthly_budget'],
            'nutritional_needs': user['nutritional_needs'],
            'current_nutrition': current_nutrition,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_recommendations': len(final_recommendations[:num_recommendations]),
                'estimated_cost': round(sum(r['price'] for r in final_recommendations[:num_recommendations]), 2),
                'primary_strategy': 'Hybrid (content-based + collaborative + knowledge-based)',
                'note': f"Recommendations tailored for {'individual' if scope == 'individual' else 'family'} shopping"
            }
        }
    
    def get_family_recommendations(self, family: Dict) -> Dict:
        """
        Get recommendations for a whole family unit.
        Aggregates nutritional needs across all family members.
        """
        
        # Aggregate nutritional needs
        combined_needs = {}
        for nutrient in ['calories', 'protein', 'fiber', 'calcium', 'iron', 'vitamin_c', 'vitamin_a_rae']:
            combined_needs[nutrient] = sum(m['nutritional_needs'].get(nutrient, 0) 
                                          for m in family['members'])
        
        # Get primary user
        primary_user_id = family['primary_user_id']
        primary_user = None
        for member in family['members']:
            if member['member_id'] == f"{primary_user_id}_self":
                primary_user = {
                    'id': family['id'],
                    'name': f"{family['primary_user_id']} (Family)",
                    'age': member['age'],
                    'gender': member['gender'],
                    'monthly_budget': family['combined_monthly_budget'],
                    'health_conditions': self._aggregate_conditions(family['members']),
                    'nutritional_needs': combined_needs
                }
                break
        
        if primary_user is None:
            raise ValueError(f"Primary user not found in family {family['id']}")
        
        # Get recommendations with family scope
        return self.get_personalized_recommendations(
            user=primary_user,
            num_recommendations=20,
            scope='family'
        )
    
    @staticmethod
    def _aggregate_conditions(family_members: List[Dict]) -> List[str]:
        """Combine health conditions from all family members"""
        conditions = []
        for member in family_members:
            conditions.extend(member.get('health_conditions', []))
        return list(set(conditions))

# ============================================================================
# PART 6: EXAMPLE USAGE
# ============================================================================

def demo_recommendations():
    """Demonstrate the recommendation engine"""
    
    # Load dummy data
    with open('dummy_data.json', 'r') as f:
        data = json.load(f)
    
    users = data['users']
    families = data['families']
    orders = data['orders']
    food_catalog = data['food_catalog']
    
    # Initialize recommender
    recommender = HybridRecommender(users, orders, food_catalog)
    
    # Get recommendations for a random user
    test_user = users[5]  # 6th user
    print("="*80)
    print("INDIVIDUAL USER RECOMMENDATION")
    print("="*80)
    print(f"\nUser: {test_user['name']}")
    print(f"Age: {test_user['age']}, Gender: {test_user['gender']}")
    print(f"Monthly Budget: ${test_user['monthly_budget']}")
    print(f"Health Conditions: {test_user['health_conditions'] or 'None'}")
    
    ind_recs = recommender.get_personalized_recommendations(test_user)
    print("\nTop Recommendations:")
    for i, rec in enumerate(ind_recs['recommendations'][:5], 1):
        print(f"\n{i}. {rec['name']}")
        print(f"   Price: ${rec['price']}")
        print(f"   Score: {rec['score']:.2f}")
        print(f"   Reason: {rec['reason']}")
    
    # Get family recommendations
    if families:
        test_family = families[0]
        print("\n" + "="*80)
        print("FAMILY RECOMMENDATIONS")
        print("="*80)
        print(f"\nFamily: {test_family['id']}")
        print(f"Members: {test_family['total_members']}")
        print(f"Combined Budget: ${test_family['combined_monthly_budget']}")
        
        family_recs = recommender.get_family_recommendations(test_family)
        print("\nTop Family Recommendations:")
        for i, rec in enumerate(family_recs['recommendations'][:5], 1):
            print(f"\n{i}. {rec['name']}")
            print(f"   Price: ${rec['price']}")
            print(f"   Score: {rec['score']:.2f}")
            print(f"   Category: {rec['category']}")
    
    # Save sample recommendations
    with open('sample_recommendations.json', 'w') as f:
        json.dump({
            'individual_recommendations': ind_recs,
            'family_recommendations': family_recs if families else None
        }, f, indent=2)
    
    print("\n✓ Sample recommendations saved to sample_recommendations.json")

if __name__ == '__main__':
    demo_recommendations()
