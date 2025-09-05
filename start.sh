#!/bin/bash

# LocalBriefing 서버 시작 스크립트

echo "🚀 LocalBriefing 서버를 시작합니다..."

# 가상환경 활성화
source venv/bin/activate

# Django 서버 시작
cd localbriefing
python manage.py runserver

echo "✅ 서버가 http://127.0.0.1:8000 에서 실행 중입니다"