import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '../../data_sources'))

def get_restaurant_data(district='강남구'):
    """실제 API 호출하여 음식점 데이터 수집"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== 음식점 데이터 수집 시작: {district} ===")
    
    new_restaurants = []
    popular_restaurants = []
    
    # Method 1: 신설 음식점 (서울시 API)
    try:
        logger.info("Method 1: 서울시 API 호출...")
        from method1_recent_restaurants.seoul_all_districts_restaurants import SeoulAllDistrictsRestaurants
        recent_collector = SeoulAllDistrictsRestaurants()
        recent_results = recent_collector.get_restaurants_by_districts([district])
        new_restaurants = recent_results.get(district, [])[:3]
        logger.info(f"Method 1 성공: {len(new_restaurants)}개 신설 음식점")
    except Exception as e:
        logger.error(f"Method 1 실패: {e}")
    
    # Method 2: 인기 맛집 (카카오 API)
    try:
        logger.info("Method 2: 카카오 API 호출...")
        from method2_popular_restaurants.realtime_restaurants import RealtimeRestaurantAPI
        popular_collector = RealtimeRestaurantAPI()
        popular_restaurants = popular_collector.get_all_new_restaurants(district)[:3]
        logger.info(f"Method 2 성공: {len(popular_restaurants)}개 인기 맛집")
        
        # API가 빈 결과를 반환하면 fallback 사용
        if not popular_restaurants:
            logger.info("API 결과가 비어있음, Fallback 사용")
            raise Exception("Empty API result")
            
    except Exception as e:
        logger.error(f"Method 2 실패: {e}")
        # Fallback: JSON 파일에서 로드
        try:
            json_path = Path(__file__).parent.parent.parent / 'data_sources' / 'method2_popular_restaurants' / 'realtime_new_restaurants.json'
            logger.info(f"Fallback JSON 로드: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                popular_restaurants = json.load(f)[:3]
            logger.info(f"Fallback 성공: {len(popular_restaurants)}개")
        except Exception as json_error:
            logger.error(f"Fallback 실패: {json_error}")
            popular_restaurants = []
    
    result = {
        'new_restaurants': new_restaurants,
        'popular_restaurants': popular_restaurants
    }
    
    logger.info(f"최종 결과: 신설 {len(new_restaurants)}개, 인기 {len(popular_restaurants)}개")
    return result