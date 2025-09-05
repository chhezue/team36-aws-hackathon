#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("🚀 LocalBriefing 서버를 시작합니다...")
    
    # 프로젝트 루트로 이동
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 가상환경 활성화 및 Django 서버 실행
    venv_python = os.path.join(project_root, 'venv', 'bin', 'python')
    manage_py = os.path.join(project_root, 'localbriefing', 'manage.py')
    
    if not os.path.exists(venv_python):
        print("❌ 가상환경이 없습니다. 먼저 'python -m venv venv'로 생성하세요.")
        sys.exit(1)
    
    print("✅ 서버가 http://127.0.0.1:8000 에서 실행됩니다")
    subprocess.run([venv_python, manage_py, 'runserver'])

if __name__ == "__main__":
    main()