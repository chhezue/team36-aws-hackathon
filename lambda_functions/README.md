# 🚀 LocalBriefing Lambda Functions

Django에서 AWS Lambda로 전환된 크롤링 시스템

## 📁 구조

```
lambda_functions/
├── crawler_handler.py      # 메인 크롤링 Lambda
├── restaurant_handler.py   # 음식점 데이터 Lambda
├── serverless.yml         # 배포 설정
├── requirements.txt       # 의존성
├── deploy.sh             # 배포 스크립트
├── test_lambda.py        # 로컬 테스트
└── layers/
    └── crawler/
        └── python/
            └── shared/   # 공통 라이브러리
```

## 🛠️ 설정

### 1. 환경변수 설정
```bash
export DB_HOST="your-rds-endpoint.amazonaws.com"
export DB_NAME="catsavetheworld_db"
export DB_USER="postgres"
export DB_PASSWORD="your-password"
export SEOUL_API_KEY="your-seoul-api-key"
export KAKAO_API_KEY="your-kakao-api-key"
```

### 2. Serverless Framework 설치
```bash
npm install -g serverless
npm install -g serverless-python-requirements
```

## 🚀 배포

```bash
# 한 번에 배포
./deploy.sh

# 또는 수동 배포
serverless deploy
```

## 📅 자동 실행 스케줄

- **크롤링**: 매일 새벽 4시 (KST)
- **음식점**: 매주 일요일 새벽 3시 (KST)

## 🔧 수동 실행

```bash
# 전체 구 크롤링
serverless invoke -f crawler

# 특정 구 크롤링
serverless invoke -f crawler -d '{"district":"강남구","limit":20}'

# 음식점 데이터 수집
serverless invoke -f restaurant
```

## 🌐 API 엔드포인트

배포 후 생성되는 API Gateway 엔드포인트:

```bash
# 크롤링 실행
POST https://your-api-id.execute-api.ap-northeast-2.amazonaws.com/dev/crawl
{
  "district": "강남구",
  "limit": 50
}

# 음식점 데이터 수집
POST https://your-api-id.execute-api.ap-northeast-2.amazonaws.com/dev/restaurants
{
  "district": "강남구"
}
```

## 🧪 로컬 테스트

```bash
python test_lambda.py
```

## 📊 모니터링

- **CloudWatch Logs**: 실행 로그 확인
- **CloudWatch Metrics**: 수집 개수 모니터링
- **X-Ray**: 성능 추적 (옵션)

## 🔄 Django에서 Lambda로 변경사항

### 제거된 파일들
- `management/commands/` 전체
- `scheduler.py`
- `manage.py` 관련 스크립트

### 새로 추가된 기능
- 서버리스 아키텍처
- EventBridge 스케줄링
- API Gateway 연동
- CloudWatch 모니터링

## 💡 장점

1. **비용 절약**: 실행 시간만 과금
2. **자동 스케일링**: 트래픽에 따른 자동 확장
3. **관리 불필요**: 서버 관리 없음
4. **고가용성**: AWS 인프라 활용