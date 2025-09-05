#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'data_sources'))
sys.path.append(os.path.join(os.getcwd(), 'data_sources/method2_realtime_api'))

from realtime_restaurants import RealtimeRestaurantAPI

def test_multiple_districts():
    api = RealtimeRestaurantAPI()
    
    test_districts = ['서초구', '마포구', '종로구']
    
    for district in test_districts:
        print(f"\n=== {district} 테스트 ===")
        restaurants = api.get_all_new_restaurants(district)
        print(f"{district} 맛집 {len(restaurants)}개:")
        
        for i, r in enumerate(restaurants, 1):
            print(f"{i}. {r.get('name')} - {r.get('address')}")

if __name__ == "__main__":
    test_multiple_districts()