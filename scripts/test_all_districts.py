#!/usr/bin/env python3
import sys
sys.path.append('localbriefing')
from restaurant_api import LocalBriefingRestaurantService

def test_all_districts():
    service = LocalBriefingRestaurantService()
    
    test_districts = ['강남구', '서초구', '마포구', '종로구', '중구']
    
    for district in test_districts:
        print(f"\n=== {district} 테스트 ===")
        restaurants = service.get_popular_restaurants(district)
        print(f"{district} 맛집 {len(restaurants)}개:")
        
        for i, restaurant in enumerate(restaurants, 1):
            print(f"{i}. {restaurant}")

if __name__ == "__main__":
    test_all_districts()