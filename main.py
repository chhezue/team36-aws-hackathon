#!/usr/bin/env python3
"""
LocalBriefing 프로젝트 메인 실행 파일
"""

import os
import sys
import subprocess

def run_django_server():
    """Django 서버 실행"""
    os.chdir('localbriefing')
    subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])

def test_data_sources():
    """데이터 소스 테스트"""
    print("=== Method 1: 신설 음식점 테스트 ===")
    os.chdir('data_sources/method1_recent_restaurants')
    subprocess.run([sys.executable, 'seoul_all_districts_restaurants.py'])
    
    print("\n=== Method 2: 인기 맛집 테스트 ===")
    os.chdir('../method2_popular_restaurants')
    subprocess.run([sys.executable, 'realtime_restaurants.py'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            run_django_server()
        elif sys.argv[1] == 'test':
            test_data_sources()
        else:
            print("사용법: python main.py [server|test]")
    else:
        print("LocalBriefing 프로젝트")
        print("사용법:")
        print("  python main.py server  # Django 서버 실행")
        print("  python main.py test    # 데이터 소스 테스트")