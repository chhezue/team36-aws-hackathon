#!/bin/bash

echo "🚀 LocalBriefing Lambda 배포 시작"

# 1. Serverless Framework 설치 확인
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework가 설치되지 않았습니다."
    echo "설치: npm install -g serverless"
    exit 1
fi

# 2. 환경변수 확인
if [ -z "$DB_HOST" ]; then
    echo "❌ 환경변수가 설정되지 않았습니다."
    echo "필요한 환경변수: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, SEOUL_API_KEY, KAKAO_API_KEY"
    exit 1
fi

# 3. 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt -t layers/crawler/python/

# 4. Lambda 배포
echo "🚀 Lambda 함수 배포 중..."
serverless deploy

echo "✅ 배포 완료!"
echo ""
echo "📋 배포된 함수들:"
echo "- crawler: 매일 새벽 4시 자동 실행"
echo "- restaurant: 매주 일요일 새벽 3시 실행"
echo "- API 엔드포인트: POST /crawl, POST /restaurants"
echo ""
echo "🔧 수동 실행 방법:"
echo "serverless invoke -f crawler"
echo "serverless invoke -f restaurant"