# LocalBriefing 구현 계획서

## 프로젝트 개요

**목표**: AI 기반 지역 뉴스 브리핑 서비스의 단계별 구현
**기간**: 총 6주 (각 Phase당 1주)
**팀 구성**: 백엔드 개발자 2명, DevOps 엔지니어 1명

---

## Phase 1: 프로젝트 설정 및 핵심 모델 (1주차)

### 1.1 Django 프로젝트 초기화
```bash
# 가상환경 생성 및 활성화
python -m venv localbriefing_env
source localbriefing_env/bin/activate  # Linux/Mac
# localbriefing_env\Scripts\activate  # Windows

# Django 프로젝트 생성
pip install django djangorestframework psycopg2-binary
django-admin startproject localbriefing
cd localbriefing
```

### 1.2 Django 앱 생성
```bash
# 핵심 앱들 생성
python manage.py startapp users
python manage.py startapp briefings
python manage.py startapp locations
```

### 1.3 데이터베이스 설정
- `settings.py`에서 PostgreSQL 연결 설정
- `DATABASE.md`에 정의된 모델들을 각 앱에 구현
- 마이그레이션 파일 생성 및 적용

### 1.4 기본 관리자 설정
- Django Admin 인터페이스 설정
- 슈퍼유저 생성 및 모델 등록

**완료 기준**: 
- ✅ 모든 모델이 정의되고 마이그레이션 완료
- ✅ Django Admin에서 데이터 CRUD 가능
- ✅ 기본 테스트 데이터 입력 완료

---

## Phase 2: 데이터 수집 모듈 개발 (2주차)

### 2.1 웹 스크래핑 라이브러리 설치
```bash
pip install requests beautifulsoup4 selenium lxml
```

### 2.2 데이터 수집기 개발
**파일 구조**:
```
briefings/
├── collectors/
│   ├── __init__.py
│   ├── base_collector.py
│   ├── district_collector.py
│   ├── community_collector.py
│   └── weather_collector.py
```

### 2.3 핵심 수집기 구현
- **구청/동사무소 공지사항**: BeautifulSoup 활용
- **네이버 카페 커뮤니티**: Selenium 활용 (로그인 필요시)
- **당근마켓 중고거래**: requests + BeautifulSoup
- **기상청 날씨 API**: 공공데이터 포털 API 연동

### 2.4 데이터 정제 및 저장
- HTML 태그 제거 및 텍스트 추출
- RawData 모델에 수집된 데이터 저장
- 중복 데이터 방지 로직 구현

**완료 기준**:
- ✅ 각 카테고리별 데이터 수집기 완성
- ✅ 수집된 데이터가 RawData 테이블에 정상 저장
- ✅ 데이터 품질 검증 및 오류 처리 완료

---

## Phase 3: AI 요약 모듈 개발 (3주차)

### 3.1 AWS SDK 설치 및 설정
```bash
pip install boto3
```

### 3.2 Amazon Bedrock 연동
**파일**: `briefings/ai/summarizer.py`

```python
import boto3
import json

class BedrockSummarizer:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    def summarize_text(self, text, category):
        prompt = f"""
        다음 텍스트를 {category} 카테고리의 동네 뉴스 형태로 3문장으로 요약해주세요.
        친근하고 이해하기 쉬운 톤으로 작성해주세요.
        
        텍스트: {text}
        """
        
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 300,
            "temperature": 0.7
        })
        
        response = self.bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-v2",
            accept="application/json",
            contentType="application/json"
        )
        
        return json.loads(response.get('body').read())
```

### 3.3 배치 처리 로직 구현
- 미처리 RawData 조회 및 배치 처리
- 카테고리별 요약 결과를 Briefing 모델에 저장
- 오류 처리 및 재시도 로직 구현

### 3.4 요약 품질 검증
- 요약 결과 길이 및 품질 검증
- 부적절한 내용 필터링
- 로깅 및 모니터링 설정

**완료 기준**:
- ✅ Bedrock Claude 모델과 정상 연동
- ✅ 카테고리별 맞춤형 요약 생성
- ✅ 요약 결과가 Briefing 테이블에 저장

---

## Phase 4: API 개발 (4주차)

### 4.1 Django REST Framework 설정
```bash
pip install djangorestframework djangorestframework-simplejwt
```

### 4.2 API 엔드포인트 개발
**파일 구조**:
```
briefings/
├── serializers.py
├── views.py
└── urls.py
```

### 4.3 핵심 API 엔드포인트
- `POST /api/auth/register/`: 사용자 회원가입
- `POST /api/auth/login/`: 로그인 및 JWT 토큰 발급
- `GET /api/briefing/today/`: 오늘의 브리핑 조회
- `GET /api/briefing/history/`: 브리핑 히스토리 조회
- `PUT /api/user/location/`: 사용자 거주지 설정

### 4.4 인증 및 권한 설정
- JWT 토큰 기반 인증 구현
- 사용자별 데이터 접근 권한 제어
- API 문서화 (DRF Spectacular)

### 4.5 API 테스트
- 단위 테스트 작성
- Postman 컬렉션 생성
- API 응답 시간 최적화

**완료 기준**:
- ✅ 모든 API 엔드포인트 정상 동작
- ✅ JWT 인증 및 권한 제어 완료
- ✅ API 문서화 및 테스트 완료

---

## Phase 5: 백그라운드 작업 자동화 (5주차)

### 5.1 AWS Lambda 함수 개발
**함수 구조**:
```
lambda_functions/
├── data_collector/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── collectors/
└── ai_processor/
    ├── lambda_function.py
    ├── requirements.txt
    └── summarizer.py
```

### 5.2 데이터 수집 Lambda 함수
```python
import json
from collectors.district_collector import DistrictCollector

def lambda_handler(event, context):
    collector = DistrictCollector()
    
    # 모든 지역에 대해 데이터 수집
    locations = get_all_locations()
    
    for location in locations:
        try:
            raw_data = collector.collect_data(location)
            save_to_database(raw_data)
        except Exception as e:
            print(f"Error collecting data for {location}: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data collection completed')
    }
```

### 5.3 AI 처리 Lambda 함수
- 미처리 RawData 조회
- Bedrock 호출하여 요약 생성
- Briefing 테이블에 결과 저장

### 5.4 EventBridge 스케줄링 설정
- 매일 새벽 4시 데이터 수집 트리거
- 수집 완료 후 AI 처리 트리거
- CloudWatch 로그 모니터링 설정

**완료 기준**:
- ✅ Lambda 함수 배포 및 정상 동작
- ✅ EventBridge 스케줄링 설정 완료
- ✅ 자동화된 일일 브리핑 생성 확인

---

## Phase 6: 배포 및 CI/CD (6주차)

### 6.1 Elastic Beanstalk 배포 준비
```bash
pip install awsebcli
eb init localbriefing
```

**파일**: `requirements.txt`
```
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.7
boto3==1.29.7
requests==2.31.0
beautifulsoup4==4.12.2
```

### 6.2 환경 설정 파일
**파일**: `.ebextensions/django.config`
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: localbriefing.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: localbriefing.settings.production
```

### 6.3 프로덕션 설정
- 환경변수 기반 설정 분리
- RDS PostgreSQL 연결 설정
- Static 파일 S3 배포 설정

### 6.4 CI/CD 파이프라인 구축
**파일**: `.github/workflows/deploy.yml`
```yaml
name: Deploy to Elastic Beanstalk
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to EB
      uses: einaregilsson/beanstalk-deploy@v20
      with:
        aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        application_name: localbriefing
        environment_name: localbriefing-env
        version_label: ${{ github.sha }}
        region: ap-northeast-2
```

### 6.5 모니터링 및 로깅
- CloudWatch 대시보드 설정
- 애플리케이션 로그 모니터링
- 알람 및 알림 설정

**완료 기준**:
- ✅ Elastic Beanstalk 배포 완료
- ✅ CI/CD 파이프라인 정상 동작
- ✅ 프로덕션 환경 모니터링 설정

---

## 최종 검증 체크리스트

### 기능 검증
- [ ] 사용자 회원가입 및 로그인
- [ ] 거주지 설정 및 변경
- [ ] 일일 브리핑 자동 생성
- [ ] API를 통한 브리핑 조회
- [ ] 모든 카테고리 데이터 수집

### 성능 검증
- [ ] API 응답 시간 < 2초
- [ ] 일일 데이터 처리 완료 시간 < 30분
- [ ] 동시 사용자 100명 처리 가능

### 운영 검증
- [ ] 자동 배포 파이프라인 동작
- [ ] 로그 모니터링 및 알람 설정
- [ ] 백업 및 복구 절차 확인

**프로젝트 완료**: 모든 체크리스트 항목 완료 시