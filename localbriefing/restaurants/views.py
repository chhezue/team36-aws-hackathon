import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../data_sources'))

from method1_recent_restaurants.seoul_all_districts_restaurants import SeoulAllDistrictsRestaurants
from method2_popular_restaurants.realtime_restaurants import RealtimeRestaurantAPI

def get_restaurant_data(district='강남구'):
    """Method 1, 2를 조합하여 음식점 데이터 수집"""
    try:
        # Method 1: 신설 음식점 (최근 개업)
        recent_collector = SeoulAllDistrictsRestaurants()
        recent_results = recent_collector.get_restaurants_by_districts([district])
        new_restaurants = recent_results.get(district, [])[:3]  # 상위 3개
        
        # Method 2: 인기 맛집
        popular_collector = RealtimeRestaurantAPI()
        popular_results = popular_collector.get_kakao_places(district)
        popular_restaurants = popular_results[:3]  # 상위 3개
        
        print(f"카카오 API 결과: {len(popular_results)}개")
        if popular_results:
            print(f"첫 번째 인기 맛집: {popular_results[0].get('name', 'N/A')}")
        else:
            print("카카오 API에서 데이터를 가져오지 못했습니다.")
        
        return {
            'new_restaurants': new_restaurants,
            'popular_restaurants': popular_restaurants
        }
        
    except Exception as e:
        print(f"음식점 데이터 수집 오류: {e}")
        return {
            'new_restaurants': [],
            'popular_restaurants': []
        }