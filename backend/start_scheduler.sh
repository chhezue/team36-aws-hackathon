#!/bin/bash

# LocalBriefing 크롤링 스케줄러 시작 스크립트

echo "LocalBriefing 크롤링 스케줄러 시작..."

# 가상환경 활성화 (필요시)
# source venv/bin/activate

# Django 환경변수 설정
export DJANGO_SETTINGS_MODULE=localbriefing.settings

# 스케줄러 시작
python manage.py start_scheduler

echo "스케줄러가 종료되었습니다."