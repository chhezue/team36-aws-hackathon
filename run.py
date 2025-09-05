#!/usr/bin/env python3
"""
LocalBriefing 프론트&백엔드 실행 스크립트
"""

import os
import sys
import subprocess
import time

def setup_environment():
    """환경 설정"""
    print("🔧 환경 설정 중...")
    
    # Django 설치 확인
    try:
        import django
        print(f"✅ Django {django.get_version()} 설치됨")
    except ImportError:
        print("📦 Django 설치 중...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'django'])
    
    # requests 설치 확인
    try:
        import requests
        print("✅ requests 라이브러리 설치됨")
    except ImportError:
        print("📦 requests 설치 중...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'])

def run_server():
    """Django 서버 실행"""
    print("\n🚀 LocalBriefing 서버 시작...")
    
    # localbriefing 디렉토리로 이동
    os.chdir('localbriefing')
    
    # 마이그레이션 실행
    print("📊 데이터베이스 마이그레이션...")
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=False)
    
    # 서버 실행
    print("🌐 서버 실행 중...")
    print("📱 브라우저에서 다음 주소로 접속하세요:")
    print("   - 온보딩: http://127.0.0.1:8000/")
    print("   - 브리핑: http://127.0.0.1:8000/briefing/")
    print("   - 설정: http://127.0.0.1:8000/settings/")
    print("\n⏹️  서버 종료: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n🛑 서버가 종료되었습니다.")

if __name__ == "__main__":
    try:
        setup_environment()
        run_server()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 문제가 지속되면 다음 명령어를 직접 실행해보세요:")
        print("   cd localbriefing")
        print("   python3 manage.py runserver")