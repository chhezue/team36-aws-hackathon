# LocalBriefing 크롤링 시스템

## 개요

LocalBriefing의 동네 이슈 수집을 위한 크롤링 시스템입니다. 유튜브, 네이버 검색, 네이버 뉴스에서 지역별 최신 이슈를 자동으로 수집합니다.

## 시스템 구조

### 1. LocalIssueCrawler 클래스

```python
class LocalIssueCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl_youtube(self, district_name, limit=5)
    def crawl_naver_search(self, district_name, limit=5)
    def crawl_naver_news(self, district_name, limit=5)
    def crawl_all(self, district_name)
```

### 2. 데이터 소스별 크롤링 전략

#### 2.1 유튜브 크롤링
- **검색 쿼리**: `{구명} 뉴스 오늘`, `{구명} 이슈 핫이슈`, `{구명} 사건 사고` 등
- **수집 데이터**: 제목, URL, 조회수
- **특징**: JSON 파싱을 통한 비디오 정보 추출

#### 2.2 네이버 검색 크롤링
- **검색 쿼리**: `{구명} 뉴스 오늘`, `{구명} 핫이슈 이슈` 등
- **수집 데이터**: 제목, URL
- **특징**: BeautifulSoup을 이용한 HTML 파싱

#### 2.3 네이버 뉴스 크롤링
- **검색 쿼리**: `{구명} 뉴스`, `{구명} 사건`, `{구명} 개발` 등
- **수집 데이터**: 제목, URL
- **특징**: 최신순 정렬로 신선한 뉴스 수집

## Django 관리 명령어

### crawl_local_issues 명령어

```bash
# 모든 구 크롤링
python manage.py crawl_local_issues

# 특정 구만 크롤링
python manage.py crawl_local_issues --district 강남구
```

### 주요 기능
- **자동 데이터 정리**: 7일 이상 된 데이터 자동 삭제
- **중복 방지**: 동일한 URL의 중복 수집 방지
- **에러 처리**: 크롤링 실패 시 다음 소스로 계속 진행

## 데이터 모델

### LocalIssue 모델

```python
class LocalIssue(models.Model):
    SOURCE_CHOICES = [
        ('youtube', '유튜브'),
        ('naver_search', '네이버 검색'),
        ('naver_news', '네이버 뉴스'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    title = models.TextField()
    url = models.URLField()
    view_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
```

## 크롤링 스케줄링

### 권장 실행 주기
- **일일 크롤링**: 매일 새벽 4시 실행
- **실시간 크롤링**: 중요 이슈 발생 시 수동 실행

### Cron 설정 예시
```bash
# 매일 새벽 4시에 모든 구 크롤링
0 4 * * * cd /path/to/project && python manage.py crawl_local_issues

# 매시간 강남구만 크롤링
0 * * * * cd /path/to/project && python manage.py crawl_local_issues --district 강남구
```

## 성능 최적화

### 1. 요청 제한
- User-Agent 헤더 설정으로 차단 방지
- 요청 간격 조절로 서버 부하 최소화

### 2. 데이터 정리
- 7일 이상 된 데이터 자동 삭제
- 인덱스 최적화로 조회 성능 향상

### 3. 에러 처리
- 네트워크 오류 시 재시도 로직
- 파싱 실패 시 다음 소스로 진행

## 확장 계획

### 추가 데이터 소스
- 인스타그램 해시태그
- 트위터 지역 트렌드
- 지역 커뮤니티 사이트

### AI 분석 연동
- 수집된 데이터의 감정 분석
- 이슈 중요도 자동 분류
- 중복 이슈 자동 병합

## 주의사항

### 법적 고려사항
- 로봇 배제 표준(robots.txt) 준수
- 저작권 침해 방지를 위한 요약 제공
- 개인정보 수집 금지

### 기술적 제약
- 동적 콘텐츠 로딩 사이트 제한
- IP 차단 위험성
- API 사용량 제한