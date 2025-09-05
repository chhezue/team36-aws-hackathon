# LocalBriefing AWS 서비스 연동 가이드

## 개요

이 문서는 LocalBriefing Django 백엔드와 핵심 AWS 서비스들을 연동하는 방법을 제공합니다. 각 서비스별로 목적, 필요 라이브러리, 그리고 실제 구현 코드를 포함합니다.

---

## 1. Amazon Bedrock (AI 텍스트 요약)

### 목적
수집된 원시 텍스트 데이터를 Claude 모델을 사용하여 친근한 톤의 동네 뉴스 형태로 요약합니다.

### 필요 라이브러리
```bash
pip install boto3
```

### Django 설정 (settings.py)
```python
# AWS 설정
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = 'us-east-1'  # Bedrock 지원 리전
```

### 샘플 코드
```python
# briefings/services/bedrock_service.py
import boto3
import json
from django.conf import settings

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    def summarize_text(self, text, category):
        prompt = f"""
        다음 텍스트를 {category} 카테고리의 동네 뉴스로 3문장 요약:
        친근하고 이해하기 쉬운 톤으로 작성해주세요.
        
        {text}
        """
        
        body = json.dumps({
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.7
        })
        
        response = self.client.invoke_model(
            body=body,
            modelId="anthropic.claude-v2",
            accept="application/json",
            contentType="application/json"
        )
        
        result = json.loads(response.get('body').read())
        return result.get('completion', '').strip()

# Django 뷰에서 사용 예시
from .services.bedrock_service import BedrockService

def process_briefing(request):
    bedrock = BedrockService()
    summary = bedrock.summarize_text("원시 텍스트 데이터", "구청 공지사항")
    return JsonResponse({'summary': summary})
```

---

## 2. Amazon RDS for PostgreSQL (데이터베이스)

### 목적
사용자 정보, 수집된 원시 데이터, AI 요약 결과를 안전하고 확장 가능한 관리형 데이터베이스에 저장합니다.

### 필요 라이브러리
```bash
pip install psycopg2-binary
```

### Django 설정 (settings.py)
```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('RDS_DB_NAME', 'localbriefing'),
        'USER': os.environ.get('RDS_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('RDS_PASSWORD'),
        'HOST': os.environ.get('RDS_HOSTNAME', 'localhost'),
        'PORT': os.environ.get('RDS_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
    }
}

# 프로덕션 환경에서 SSL 연결 강제
if os.environ.get('DJANGO_ENV') == 'production':
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'
```

### 환경변수 설정 예시
```bash
# .env 파일
RDS_HOSTNAME=localbriefing.xxxxx.ap-northeast-2.rds.amazonaws.com
RDS_DB_NAME=localbriefing
RDS_USERNAME=dbadmin
RDS_PASSWORD=your_secure_password
RDS_PORT=5432
```

### 연결 테스트 코드
```python
# management/commands/test_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                result = cursor.fetchone()
                self.stdout.write(f"PostgreSQL 연결 성공: {result[0]}")
        except Exception as e:
            self.stdout.write(f"데이터베이스 연결 실패: {e}")
```

---

## 3. AWS Lambda (백그라운드 작업)

### 목적
매일 새벽 4시에 자동으로 실행되어 웹 스크래핑과 AI 요약 작업을 수행합니다.

### 필요 라이브러리
```bash
pip install boto3 requests beautifulsoup4
```

### Lambda 함수 코드
```python
# lambda_function.py
import json
import boto3
import requests
from bs4 import BeautifulSoup
import psycopg2
import os

def lambda_handler(event, context):
    """데이터 수집 및 처리 Lambda 함수"""
    
    try:
        # 1. 웹 스크래핑 수행
        scraped_data = scrape_district_news()
        
        # 2. RDS에 원시 데이터 저장
        save_raw_data(scraped_data)
        
        # 3. Bedrock으로 요약 생성
        summaries = process_with_bedrock(scraped_data)
        
        # 4. 요약 결과 저장
        save_briefings(summaries)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '데이터 처리 완료',
                'processed_items': len(scraped_data)
            })
        }
        
    except Exception as e:
        print(f"Lambda 실행 오류: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def scrape_district_news():
    """구청 웹사이트 스크래핑"""
    url = "https://www.gangnam.go.kr/board/B0000005/list.do"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for item in soup.select('.board-list tr')[:5]:  # 최신 5개
        title_elem = item.select_one('.title a')
        if title_elem:
            articles.append({
                'title': title_elem.get_text().strip(),
                'url': title_elem.get('href'),
                'category': 'district_news'
            })
    
    return articles

def save_raw_data(data):
    """RDS에 원시 데이터 저장"""
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        for item in data:
            cursor.execute("""
                INSERT INTO raw_data (title, source_url, category, content, location_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (item['title'], item['url'], item['category'], item['title'], 1))
    
    conn.commit()
    conn.close()

def process_with_bedrock(data):
    """Bedrock으로 텍스트 요약"""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    summaries = []
    for item in data:
        body = json.dumps({
            "prompt": f"\n\nHuman: 다음을 3문장으로 요약: {item['title']}\n\nAssistant:",
            "max_tokens_to_sample": 200,
            "temperature": 0.7
        })
        
        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-v2",
            accept="application/json",
            contentType="application/json"
        )
        
        result = json.loads(response.get('body').read())
        summaries.append({
            'original': item,
            'summary': result.get('completion', '').strip()
        })
    
    return summaries

def save_briefings(summaries):
    """요약 결과를 브리핑 테이블에 저장"""
    # 구현 생략 - RDS 연결하여 briefings 테이블에 저장
    pass
```

### EventBridge 스케줄 설정
```json
{
  "Rules": [
    {
      "Name": "DailyBriefingSchedule",
      "ScheduleExpression": "cron(0 4 * * ? *)",
      "State": "ENABLED",
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:lambda:ap-northeast-2:123456789012:function:localbriefing-collector"
        }
      ]
    }
  ]
}
```

---

## 4. Amazon S3 (정적 파일 및 데이터 저장)

### 목적
Django 정적 파일 서빙과 대용량 스크래핑 데이터의 백업 저장소로 활용합니다.

### 필요 라이브러리
```bash
pip install boto3 django-storages
```

### Django 설정 (settings.py)
```python
# S3 설정
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', 'localbriefing-static')
AWS_S3_REGION_NAME = 'ap-northeast-2'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

# 정적 파일 설정
if os.environ.get('USE_S3') == 'TRUE':
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# S3 권한 설정
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
```

### S3 활용 샘플 코드
```python
# utils/s3_utils.py
import boto3
from django.conf import settings
import json
from datetime import datetime

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def backup_raw_data(self, data, location):
        """수집된 원시 데이터를 S3에 백업"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f'raw_data_backup/{location}/{timestamp}.json'
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False),
            ContentType='application/json'
        )
        
        return f's3://{self.bucket_name}/{key}'
    
    def get_backup_data(self, key):
        """S3에서 백업 데이터 조회"""
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=key
        )
        
        return json.loads(response['Body'].read().decode('utf-8'))

# Django 뷰에서 사용 예시
from .utils.s3_utils import S3Service

def backup_scraped_data(request):
    s3_service = S3Service()
    data = {'articles': ['article1', 'article2']}
    backup_url = s3_service.backup_raw_data(data, 'gangnam-gu')
    
    return JsonResponse({'backup_url': backup_url})
```

---

## 환경변수 설정 가이드

### .env 파일 예시
```bash
# AWS 인증
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=ap-northeast-2

# RDS 설정
RDS_HOSTNAME=localbriefing.xxxxx.ap-northeast-2.rds.amazonaws.com
RDS_DB_NAME=localbriefing
RDS_USERNAME=dbadmin
RDS_PASSWORD=your_secure_password
RDS_PORT=5432

# S3 설정
AWS_S3_BUCKET_NAME=localbriefing-static
USE_S3=TRUE

# Django 환경
DJANGO_ENV=production
DEBUG=False
```

### AWS IAM 권한 정책 예시
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::localbriefing-static/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBInstances"
            ],
            "Resource": "*"
        }
    ]
}
```