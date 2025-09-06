#!/bin/bash

echo "🚀 LocalBriefing Lambda 간단 배포"

# 환경변수 설정
export DB_HOST="aws-hackerton-catsavetheworld.c4huy4i6sor5.us-east-1.rds.amazonaws.com"
export DB_NAME="catsavetheworld_db"
export DB_USER="postgres"
export DB_PASSWORD="catsavetheworld!"
export SEOUL_API_KEY="6547735274616e6438376e53524e4f"
export KAKAO_API_KEY="22b44c41a71b28ea149f0251c973f326"

echo "✅ 환경변수 설정 완료"

# 의존성 설치
echo "📦 의존성 설치 중..."
pip3 install -r requirements.txt -t layers/crawler/python/ --quiet

echo "🚀 Serverless 배포 시작..."

# Serverless 배포 (오프라인 모드)
serverless deploy --verbose

echo "✅ 배포 완료!"