#!/usr/bin/env python3
"""
음식점 API 테스트 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localbriefing.settings')
django.setup()

from restaurants.views import get_restaurant_data

def test_restaurant_api():
    print("=== 음식점 API 테스트 ===")
    
    # 강남구 테스트
    district = '강남구'
    print(f"\n{district} 음식점 데이터 수집 중...")
    
    try:
        result = get_restaurant_data(district)
        
        print(f"\n결과:")
        print(f"- 신설 음식점: {len(result['new_restaurants'])}개")
        print(f"- 인기 맛집: {len(result['popular_restaurants'])}개")
        
        print(f"\n신설 음식점 목록:")
        for i, restaurant in enumerate(result['new_restaurants'], 1):
            print(f"  {i}. {restaurant.get('name', 'N/A')} - {restaurant.get('license_date', 'N/A')}")
        
        print(f"\n인기 맛집 목록:")
        for i, restaurant in enumerate(result['popular_restaurants'], 1):
            print(f"  {i}. {restaurant.get('name', 'N/A')} - {restaurant.get('place_url', 'N/A')}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_restaurant_api()