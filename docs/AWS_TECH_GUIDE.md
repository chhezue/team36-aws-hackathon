# LocalBriefing AWS 기술 선택 및 구현 가이드

## 1. AWS 서비스 설명

### 1.1 Amazon Bedrock
**정의**: AWS의 완전 관리형 생성형 AI 서비스
- **기능**: Anthropic Claude, Amazon Titan 등 파운데이션 모델 API 제공
- **특징**: 서버리스, 사용량 기반 과금, 한국어 지원 우수
- **용도**: 텍스트 요약, 번역, 질의응답 등

### 1.2 AWS Elastic Beanstalk
**정의**: 웹 애플리케이션 배포 및 관리 서비스
- **기능**: EC2, 로드밸런서, 오토스케일링 자동 구성
- **특징**: 코드만 업로드하면 인프라 자동 관리
- **용도**: Django 웹 애플리케이션 배포

### 1.3 Amazon RDS
**정의**: 완전 관리형 관계형 데이터베이스 서비스
- **기능**: PostgreSQL, MySQL 등 DB 엔진 지원
- **특징**: 자동 백업, 패치, 모니터링
- **용도**: 사용자 데이터, 브리핑 데이터 저장

### 1.4 AWS Lambda
**정의**: 서버리스 컴퓨팅 서비스
- **기능**: 이벤트 기반 코드 실행
- **특징**: 사용한 만큼만 과금, 자동 스케일링
- **용도**: 데이터 수집, AI 처리 등 백그라운드 작업

### 1.5 Amazon EventBridge
**정의**: 서버리스 이벤트 버스 서비스
- **기능**: 스케줄링, 이벤트 라우팅
- **특징**: cron 표현식 지원, 다양한 AWS 서비스 연동
- **용도**: 매일 새벽 4시 데이터 수집 트리거

---

## 2. 기술별 사용 시점 및 제약사항

### 2.1 즉시 사용 가능한 기술

#### ✅ Amazon RDS PostgreSQL
**사용 시점**: 프로젝트 시작부터
- 별도 승인 불필요
- Django 개발 환경에서 바로 연결 가능
- 로컬 개발 → RDS 마이그레이션 순서로 진행

#### ✅ AWS Lambda + EventBridge
**사용 시점**: 백엔드 API 완성 후
- 기본 AWS 계정으로 바로 사용 가능
- 데이터 수집 로직 완성 후 Lambda로 이전
- EventBridge 스케줄링은 Lambda 함수 준비 후 설정

#### ✅ Elastic Beanstalk
**사용 시점**: Django 앱 완성 후 배포 단계
- 즉시 사용 가능
- 로컬 개발 완료 후 프로덕션 배포용

### 2.2 사용 제한이 있는 기술

#### ⚠️ Amazon Bedrock (사용 제한 있음)
**제약사항**:
- **지역 제한**: us-east-1, us-west-2 등 특정 리전에서만 사용 가능
- **모델 액세스 요청**: Claude 모델 사용 전 AWS 콘솔에서 액세스 요청 필요
- **승인 시간**: 보통 24-48시간 소요
- **대안 필요**: 초기 개발 시 OpenAI API 또는 로컬 요약 로직 사용

**사용 시점**: 
1. AWS 콘솔에서 Bedrock 모델 액세스 요청
2. 승인 완료 후 API 연동 테스트
3. 승인 전까지는 더미 데이터나 간단한 텍스트 처리로 대체

### 2.3 단계별 기술 도입 전략

#### Phase 1: MVP 개발 (Bedrock 없이)
```
로컬 Django + PostgreSQL + 간단한 텍스트 요약
```
- Bedrock 대신 텍스트 길이 제한이나 키워드 추출로 임시 구현
- 핵심 기능(데이터 수집, 저장, API) 먼저 완성

#### Phase 2: 클라우드 배포
```
Elastic Beanstalk + RDS + Lambda (수집만)
```
- AI 요약 없이 원시 데이터 수집 및 표시
- 사용자 피드백 수집 및 서비스 검증

#### Phase 3: AI 기능 추가 (Bedrock 승인 후)
```
기존 구조 + Bedrock (AI 요약)
```
- Bedrock 액세스 승인 후 AI 요약 기능 추가
- 기존 원시 데이터를 AI로 재처리

### 2.4 Bedrock 대안 기술

#### 즉시 사용 가능한 대안들
1. **OpenAI API**: GPT-3.5/4 사용, 즉시 사용 가능
2. **Google Cloud Translation API**: 요약 기능 제한적
3. **로컬 처리**: 키워드 추출, 문장 길이 제한
4. **Hugging Face API**: 오픈소스 모델 활용

```python
# Bedrock 대신 OpenAI 사용 예시
import openai

def summarize_with_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"다음을 3문장으로 요약: {text}"}
        ]
    )
    return response.choices[0].message.content
```

### 2.5 최종 권장 개발 순서

1. **1주차**: Django + 로컬 PostgreSQL + 기본 기능
2. **2주차**: 데이터 수집 모듈 + OpenAI API 임시 연동
3. **3주차**: RDS 연결 + Elastic Beanstalk 배포
4. **4주차**: Lambda 함수 + EventBridge 스케줄링
5. **5주차**: Bedrock 액세스 요청 및 대기
6. **6주차**: Bedrock 승인 후 AI 요약 기능 교체

**핵심**: Bedrock 승인을 기다리는 동안 다른 모든 기능을 완성하여 시간 낭비 방지

---

## 3. 실제 구현 순서 (Bedrock 제약 고려)

### Phase 1: 로컬 개발 환경 구축 (1주)

#### 1.1 Django 프로젝트 초기화
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# Django 설치 및 프로젝트 생성
pip install django djangorestframework psycopg2-binary boto3
django-admin startproject localbriefing
cd localbriefing
python manage.py startapp briefings
```

#### 1.2 로컬 PostgreSQL 연결
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'localbriefing_dev',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 1.3 기본 모델 정의
```python
# briefings/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Location(models.Model):
    gu = models.CharField(max_length=50)
    dong = models.CharField(max_length=50)

class User(AbstractUser):
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

class RawData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    content = models.TextField()
    collected_at = models.DateTimeField(auto_now_add=True)

class Briefing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.JSONField()
```

### Phase 2: AI 요약 서비스 구현 (Bedrock 대안 포함) (1주)

#### 2.1 AWS 자격증명 설정 + Bedrock 액세스 요청
```bash
# AWS CLI 설치 및 설정
pip install awscli openai
aws configure
```

**중요**: AWS 콘솔에서 Bedrock 모델 액세스 요청 (24-48시간 소요)

#### 2.2 AI 서비스 구현 (Bedrock + 대안)
```python
# briefings/services/ai_service.py
import boto3
import json
import openai
import os
from django.conf import settings

class AIService:
    def __init__(self):
        self.use_bedrock = getattr(settings, 'USE_BEDROCK', False)
        if self.use_bedrock:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        else:
            openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    def summarize_text(self, text, category):
        if self.use_bedrock:
            return self._summarize_with_bedrock(text, category)
        else:
            return self._summarize_with_openai(text, category)
    
    def _summarize_with_bedrock(self, text, category):
        try:
            prompt = f"다음 {category} 관련 텍스트를 3문장으로 요약해주세요: {text}"
            
            body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 300,
                "temperature": 0.7
            })
            
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId="anthropic.claude-v2",
                accept="application/json",
                contentType="application/json"
            )
            
            result = json.loads(response.get('body').read())
            return result.get('completion', '').strip()
        except Exception as e:
            print(f"Bedrock 오류, OpenAI로 대체: {e}")
            return self._summarize_with_openai(text, category)
    
    def _summarize_with_openai(self, text, category):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"다음 {category} 관련 텍스트를 3문장으로 요약: {text}"}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # 최후의 수단: 간단한 텍스트 처리
            return self._simple_summarize(text)
    
    def _simple_summarize(self, text):
        # 첫 200자 + "..." 형태로 간단 요약
        return text[:200] + "..." if len(text) > 200 else text
```

#### 2.3 설정 파일 업데이트
```python
# settings.py
USE_BEDROCK = os.environ.get('USE_BEDROCK', 'False').lower() == 'true'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
```

#### 2.4 테스트 명령어
```python
# management/commands/test_ai.py
from django.core.management.base import BaseCommand
from briefings.services.ai_service import AIService

class Command(BaseCommand):
    def handle(self, *args, **options):
        service = AIService()
        result = service.summarize_text("강남구청에서 새로운 도서관을 개관합니다.", "구청소식")
        print(f"요약 결과: {result}")
        print(f"사용 중인 AI: {'Bedrock' if service.use_bedrock else 'OpenAI/Simple'}")
```

### Phase 3: 데이터 수집 모듈 개발 (1주)

#### 3.1 웹 스크래핑 구현
```python
# briefings/collectors/district_collector.py
import requests
from bs4 import BeautifulSoup

class DistrictCollector:
    def collect_gangnam_news(self):
        url = "https://www.gangnam.go.kr/board/B0000005/list.do"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        for item in soup.select('.board-list tr')[:5]:
            title_elem = item.select_one('.title a')
            if title_elem:
                articles.append({
                    'title': title_elem.get_text().strip(),
                    'category': 'district_news'
                })
        return articles
```

#### 3.2 배치 처리 로직
```python
# briefings/services/batch_service.py
from .ai_service import AIService
from ..collectors.district_collector import DistrictCollector
from ..models import RawData, Briefing

class BatchService:
    def process_daily_briefing(self):
        # 1. 데이터 수집
        collector = DistrictCollector()
        raw_articles = collector.collect_gangnam_news()
        
        # 2. 원시 데이터 저장
        for article in raw_articles:
            RawData.objects.create(
                location_id=1,  # 강남구
                category=article['category'],
                content=article['title']
            )
        
        # 3. AI 요약 (Bedrock 또는 대안 사용)
        ai_service = AIService()
        summaries = []
        for article in raw_articles:
            try:
                summary = ai_service.summarize_text(
                    article['title'], 
                    article['category']
                )
                summaries.append(summary)
            except Exception as e:
                print(f"요약 실패: {e}")
                summaries.append(article['title'])  # 원본 제목 사용
        
        # 4. 브리핑 저장
        briefing_content = {
            'district_news': summaries
        }
        # Briefing 객체 생성 로직...
```

### Phase 4: AWS Lambda 함수 개발 (1주)

#### 4.1 Lambda 함수 구조
```
lambda_functions/
├── data_collector/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── collectors/
└── deployment/
    └── deploy.sh
```

#### 4.2 Lambda 함수 코드
```python
# lambda_functions/data_collector/lambda_function.py
import json
import psycopg2
import boto3
import os

def lambda_handler(event, context):
    try:
        # 데이터 수집
        articles = collect_district_news()
        
        # RDS 저장
        save_to_rds(articles)
        
        # AI 처리 Lambda 트리거
        trigger_ai_processing()
        
        return {
            'statusCode': 200,
            'body': json.dumps('수집 완료')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'오류: {str(e)}')
        }

def collect_district_news():
    # 웹 스크래핑 로직
    pass

def save_to_rds(articles):
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    # 데이터 저장 로직
    pass
```

#### 4.3 배포 스크립트
```bash
# deployment/deploy.sh
#!/bin/bash
cd lambda_functions/data_collector
zip -r function.zip .
aws lambda update-function-code \
    --function-name localbriefing-collector \
    --zip-file fileb://function.zip
```

### Phase 5: Amazon RDS 설정 (1주)

#### 5.1 RDS 인스턴스 생성
```bash
# AWS CLI로 RDS 생성
aws rds create-db-instance \
    --db-instance-identifier localbriefing-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username dbadmin \
    --master-user-password your-password \
    --allocated-storage 20
```

#### 5.2 Django 설정 업데이트
```python
# settings/production.py
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('RDS_DB_NAME'),
        'USER': os.environ.get('RDS_USERNAME'),
        'PASSWORD': os.environ.get('RDS_PASSWORD'),
        'HOST': os.environ.get('RDS_HOSTNAME'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

### Phase 6: EventBridge 스케줄링 설정 (1주)

#### 6.1 EventBridge 규칙 생성
```json
{
  "Name": "DailyBriefingSchedule",
  "ScheduleExpression": "cron(0 4 * * ? *)",
  "State": "ENABLED",
  "Targets": [
    {
      "Id": "1",
      "Arn": "arn:aws:lambda:ap-northeast-2:account:function:localbriefing-collector"
    }
  ]
}
```

#### 6.2 CloudWatch 모니터링 설정
```python
# Lambda 함수에 로깅 추가
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("데이터 수집 시작")
    # 처리 로직
    logger.info("데이터 수집 완료")
```

### Phase 7: Elastic Beanstalk 배포 (1주)

#### 7.1 Beanstalk 애플리케이션 생성
```bash
# EB CLI 설치 및 초기화
pip install awsebcli
eb init localbriefing
eb create localbriefing-env
```

#### 7.2 환경 설정
```yaml
# .ebextensions/django.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: localbriefing.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: localbriefing.settings.production
    RDS_HOSTNAME: your-rds-endpoint
    RDS_DB_NAME: localbriefing
```

#### 7.3 배포
```bash
eb deploy
```

---

## 4. 예상 비용 및 성능

### 4.1 월간 예상 비용 (사용자 1,000명 기준)
- **AI 서비스**: 
  - Bedrock: $10-20 (승인 후)
  - OpenAI: $15-30 (대안 사용시)
- **Lambda**: $1-5 (실행 시간)
- **RDS**: $15-25 (db.t3.micro)
- **Beanstalk**: $10-20 (t3.small)
- **총 예상 비용**: $41-80/월

### 4.2 성능 목표
- **API 응답시간**: < 500ms
- **일일 처리량**: 10,000건 이상
- **가용성**: 99.9% 이상

## 5. 중요 체크리스트

### Bedrock 사용 전 필수 확인사항
- [ ] AWS 콘솔에서 Bedrock 서비스 액세스 요청
- [ ] Claude 모델 액세스 승인 대기 (24-48시간)
- [ ] us-east-1 리전 사용 설정
- [ ] 대안 AI 서비스 (OpenAI) 준비

### 개발 우선순위
1. **먼저 구현**: Django 기본 기능, 데이터 수집, RDS 연결
2. **나중에 추가**: AI 요약 기능 (Bedrock 승인 후)
3. **최종 배포**: Beanstalk + Lambda 자동화

이 가이드를 따라 구현하면 Bedrock 제약사항을 고려한 현실적인 LocalBriefing 서비스를 구축할 수 있습니다.