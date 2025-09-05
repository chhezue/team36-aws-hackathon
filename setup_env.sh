#!/bin/bash
# LocalBriefing 전역 환경변수 설정 스크립트

echo "=== LocalBriefing 전역 환경변수 설정 ==="

# 프로젝트 루트로 이동
cd "$(dirname "$0")"

# .env 파일이 있는지 확인
if [ ! -f ".env" ]; then
    echo ".env 파일이 없습니다. .env.example을 복사합니다."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env 파일을 생성했습니다. API 키를 입력해주세요."
    else
        echo ".env.example 파일을 찾을 수 없습니다."
        exit 1
    fi
fi

# 환경변수 로드
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "전역 환경변수 로드 완료"
else
    echo ".env 파일을 찾을 수 없습니다."
    exit 1
fi

# 현재 설정된 환경변수 확인
echo ""
echo "=== 현재 API 키 설정 ==="
echo "SEOUL_API_KEY: ${SEOUL_API_KEY:-'설정되지 않음'}"
echo "KAKAO_API_KEY: ${KAKAO_API_KEY:-'설정되지 않음'}"
echo "NAVER_CLIENT_ID: ${NAVER_CLIENT_ID:-'설정되지 않음'}"
echo "DATA_GO_KR_API_KEY: ${DATA_GO_KR_API_KEY:-'설정되지 않음'}"

echo ""
echo "=== 사용법 ==="
echo "1. .env 파일에서 실제 API 키로 변경"
echo "2. source setup_env.sh 실행"
echo "3. 각 스크립트 실행"
echo ""
echo "전역 환경변수 파일 위치: $(pwd)/.env"