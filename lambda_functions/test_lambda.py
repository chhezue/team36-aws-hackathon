#!/usr/bin/env python3
"""Lambda 함수 로컬 테스트"""

import json
import os
from datetime import datetime

# 환경변수 설정 (테스트용)
os.environ.update({
    'DB_HOST': 'your-rds-endpoint.amazonaws.com',
    'DB_NAME': 'catsavetheworld_db',
    'DB_USER': 'postgres',
    'DB_PASSWORD': 'your-password',
    'SEOUL_API_KEY': 'your-seoul-api-key',
    'KAKAO_API_KEY': 'your-kakao-api-key'
})

def test_crawler():
    """크롤링 Lambda 테스트"""
    print("🕷️ 크롤링 Lambda 테스트")
    
    # 테스트 이벤트
    event = {
        'district': '강남구',  # 특정 구 테스트
        'limit': 10
    }
    
    context = {}
    
    try:
        from crawler_handler import lambda_handler
        result = lambda_handler(event, context)
        print(f"✅ 결과: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def test_restaurant():
    """음식점 Lambda 테스트"""
    print("🍽️ 음식점 Lambda 테스트")
    
    event = {
        'district': '강남구'
    }
    
    context = {}
    
    try:
        from restaurant_handler import lambda_handler
        result = lambda_handler(event, context)
        print(f"✅ 결과: {result}")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    print("🧪 Lambda 함수 로컬 테스트 시작")
    print("=" * 50)
    
    # 크롤링 테스트
    test_crawler()
    print()
    
    # 음식점 테스트
    test_restaurant()
    
    print("=" * 50)
    print("✅ 테스트 완료")