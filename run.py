#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
import time

def run_backend():
    """백엔드 Django 서버 실행"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, 'venv', 'bin', 'python')
    manage_py = os.path.join(project_root, 'backend', 'manage.py')
    
    print("🔧 백엔드 서버 시작 중... (Django)")
    subprocess.run([venv_python, manage_py, 'runserver', '127.0.0.1:8000'])

def run_frontend():
    """프론트엔드 Next.js 서버 실행"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, 'frontend')
    
    if not os.path.exists(frontend_dir):
        print("❌ frontend 폴더가 없습니다.")
        return
    
    print("⚛️ 프론트엔드 서버 시작 중... (Next.js)")
    os.chdir(frontend_dir)
    
    # npm install 확인
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("📦 의존성 설치 중...")
        subprocess.run(['npm', 'install'])
    
    # Next.js 개발 서버 실행
    subprocess.run(['npm', 'run', 'dev'])

def main():
    print("🚀 VibeThermo 풀스택 서버를 시작합니다...")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, 'venv', 'bin', 'python')
    
    # 가상환경 확인
    if not os.path.exists(venv_python):
        print("❌ 가상환경이 없습니다. 먼저 'python -m venv venv'로 생성하세요.")
        sys.exit(1)
    
    print("\n📍 서버 주소:")
    print("   프론트엔드: http://localhost:3000")
    print("   백엔드 API: http://127.0.0.1:8000")
    print("\n⚠️  종료하려면 Ctrl+C를 두 번 누르세요\n")
    
    try:
        # 백엔드를 별도 스레드에서 실행
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # 백엔드 시작 대기
        time.sleep(3)
        
        # 프론트엔드를 메인 스레드에서 실행
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")
        sys.exit(0)

if __name__ == "__main__":
    main()