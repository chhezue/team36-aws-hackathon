# AWS 데이터베이스 아키텍처 설계

## 1. 데이터 특성 분석

### 1.1 데이터 볼륨 예상
- **25개 구 × 일일 20개 이슈 = 500개/일**
- **월간 약 15,000개 데이터**
- **7일 보관 정책 → 최대 3,500개 활성 데이터**

### 1.2 데이터 패턴
- **쓰기**: 매일 자정 1회 대량 INSERT
- **읽기**: 사용자 브리핑 조회 시 실시간
- **삭제**: 7일 이상 된 데이터 자동 삭제

## 2. 권장 AWS 아키텍처

### 2.1 RDS PostgreSQL 설정
```yaml
인스턴스: db.t3.micro (프리티어)
스토리지: 20GB GP2 SSD
백업: 7일 자동 백업
Multi-AZ: 비활성화 (비용 절약)
암호화: 활성화
```

### 2.2 데이터베이스 최적화

#### A. 파티셔닝 전략
```sql
-- 날짜별 파티셔닝으로 성능 향상
CREATE TABLE local_issues_partitioned (
    LIKE local_issues INCLUDING ALL
) PARTITION BY RANGE (collected_at);

-- 일별 파티션 생성 (7일간)
CREATE TABLE local_issues_2025_01_09 PARTITION OF local_issues_partitioned
FOR VALUES FROM ('2025-01-09') TO ('2025-01-10');
```

#### B. 인덱스 최적화
```sql
-- 복합 인덱스로 쿼리 성능 향상
CREATE INDEX idx_location_date ON local_issues (location_id, collected_at DESC);
CREATE INDEX idx_sentiment_location_date ON sentiment_analysis (location_id, analyzed_at DESC);
```

### 2.3 캐싱 전략

#### A. Redis 캐시 (ElastiCache)
```python
# 브리핑 데이터 캐싱 (1시간)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://elasticache-endpoint:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,  # 1시간
    }
}
```

#### B. 캐시 키 전략
```python
# 지역별 브리핑 캐시
cache_key = f"briefing:{district}:{date}"
# 감성 요약 캐시  
cache_key = f"sentiment:{district}:{date}"
```

## 3. 데이터 수집 최적화

### 3.1 배치 처리 전략
```python
# 대량 INSERT 최적화
def bulk_create_issues(issues_data):
    LocalIssue.objects.bulk_create(
        [LocalIssue(**data) for data in issues_data],
        batch_size=100,
        ignore_conflicts=True
    )
```

### 3.2 병렬 처리
```python
# 25개 구 병렬 크롤링
from concurrent.futures import ThreadPoolExecutor

def crawl_district_parallel():
    districts = Location.objects.values_list('gu', flat=True)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(crawl_single_district, district) 
            for district in districts
        ]
```

## 4. 스케줄링 아키텍처

### 4.1 AWS Lambda + EventBridge
```yaml
# serverless.yml
functions:
  dailyCrawl:
    handler: crawl_handler.main
    events:
      - schedule: cron(0 15 * * ? *)  # 매일 자정 KST
    timeout: 900  # 15분
    memory: 1024
```

### 4.2 ECS Fargate (권장)
```yaml
# docker-compose.yml
version: '3.8'
services:
  crawler:
    image: localbriefing-crawler
    environment:
      - DB_HOST=${RDS_ENDPOINT}
    cpu: 256
    memory: 512
```

### 4.3 EventBridge 스케줄
```json
{
  "ScheduleExpression": "cron(0 15 * * ? *)",
  "Target": {
    "Arn": "arn:aws:ecs:ap-northeast-2:account:cluster/crawler",
    "RoleArn": "arn:aws:iam::account:role/ECSTaskRole"
  }
}
```

## 5. 데이터 생명주기 관리

### 5.1 자동 정리 정책
```python
# 7일 이상 된 데이터 삭제
@transaction.atomic
def cleanup_old_data():
    cutoff_date = timezone.now() - timedelta(days=7)
    
    # 배치 삭제로 성능 향상
    LocalIssue.objects.filter(
        collected_at__lt=cutoff_date
    ).delete()
    
    SentimentAnalysis.objects.filter(
        analyzed_at__lt=cutoff_date
    ).delete()
```

### 5.2 아카이브 전략
```python
# S3로 아카이브 (선택사항)
def archive_to_s3(old_data):
    s3_client = boto3.client('s3')
    
    archive_data = {
        'date': old_data.collected_at.date(),
        'data': serialize_data(old_data)
    }
    
    s3_client.put_object(
        Bucket='localbriefing-archive',
        Key=f'archive/{old_data.collected_at.date()}.json',
        Body=json.dumps(archive_data)
    )
```

## 6. 모니터링 및 알림

### 6.1 CloudWatch 메트릭
```python
# 커스텀 메트릭 전송
def send_crawl_metrics(district, count, duration):
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='LocalBriefing/Crawler',
        MetricData=[
            {
                'MetricName': 'IssuesCollected',
                'Dimensions': [{'Name': 'District', 'Value': district}],
                'Value': count,
                'Unit': 'Count'
            }
        ]
    )
```

### 6.2 알림 설정
```yaml
# CloudWatch 알람
CrawlFailureAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: CrawlFailure
    MetricName: Errors
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    AlarmActions:
      - !Ref SNSTopic
```

## 7. 비용 최적화

### 7.1 RDS 최적화
- **인스턴스**: db.t3.micro (월 $13)
- **스토리지**: 20GB ($2.3/월)
- **백업**: 7일 (무료)
- **총 예상 비용**: 월 $15-20

### 7.2 Lambda vs ECS 비교
```
Lambda:
- 실행 시간: 15분/일
- 비용: 월 $1-2
- 장점: 서버리스, 관리 불필요

ECS Fargate:
- 실행 시간: 30분/일  
- 비용: 월 $3-5
- 장점: 더 긴 실행 시간, 복잡한 작업 가능
```

## 8. 구현 우선순위

### Phase 1: 기본 구성
1. RDS PostgreSQL 생성
2. 기본 테이블 마이그레이션
3. 단일 구 크롤링 테스트

### Phase 2: 스케일링
1. 25개 구 병렬 처리
2. Redis 캐싱 적용
3. CloudWatch 모니터링

### Phase 3: 최적화
1. 파티셔닝 적용
2. 아카이브 정책
3. 성능 튜닝

## 9. 실제 구현 코드

### 9.1 최적화된 크롤링 명령어
```python
# users/management/commands/aws_daily_crawl.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # 병렬 처리로 성능 향상
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for location in Location.objects.all():
                future = executor.submit(self.crawl_district, location)
                futures.append(future)
            
            # 결과 수집
            total_collected = sum(f.result() for f in futures)
            
        # CloudWatch 메트릭 전송
        self.send_metrics(total_collected)
```

### 9.2 캐시 적용 뷰
```python
from django.core.cache import cache

def briefing_view(request):
    district = request.session.get('district', '강남구')
    cache_key = f"briefing:{district}:{date.today()}"
    
    # 캐시에서 먼저 조회
    briefing_data = cache.get(cache_key)
    
    if not briefing_data:
        # DB에서 조회 후 캐시 저장
        briefing_data = generate_briefing_data(district)
        cache.set(cache_key, briefing_data, 3600)  # 1시간
    
    return render(request, 'briefing.html', briefing_data)
```

이 아키텍처로 **안정적이고 확장 가능한** 데이터베이스 시스템을 구축할 수 있습니다.