#!/bin/bash

echo "🚀 LocalBriefing Lambda 배포 (Python 3.9)"

# pyenv 환경 설정
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Python 3.9 사용 확인
python --version

# 환경변수 설정
export DB_HOST="aws-hackerton-catsavetheworld.c4huy4i6sor5.us-east-1.rds.amazonaws.com"
export DB_NAME="catsavetheworld_db"
export DB_USER="postgres"
export DB_PASSWORD="catsavetheworld!"
export SEOUL_API_KEY="6547735274616e6438376e53524e4f"
export KAKAO_API_KEY="22b44c41a71b28ea149f0251c973f326"

echo "✅ 환경변수 설정 완료"

# 의존성 재설치
echo "📦 의존성 재설치 중..."
rm -rf layers/crawler/python/*
pip install -r requirements_fixed.txt -t layers/crawler/python/ --quiet

echo "🚀 Serverless 배포 시작..."
serverless deploy --config serverless_fixed.yml --verbose

echo "✅ 배포 완료!"