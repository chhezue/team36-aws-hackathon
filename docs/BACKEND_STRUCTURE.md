# LocalBriefing 백엔드 구조 설명

## 📁 폴더 구조 및 역할

```
backend/
├── config/                    # Django 프로젝트 설정
│   ├── settings.py           # 메인 설정 파일
│   ├── urls.py              # 루트 URL 설정
│   └── wsgi.py              # WSGI 애플리케이션
│
├── local_data/               # 지역 데이터 & 감성 분석 시스템
│   ├── models.py            # 핵심 데이터 모델들
│   ├── views.py             # 브리핑 뷰 & 감성 대시보드
│   ├── crawlers.py          # 데이터 크롤링 로직
│   ├── sentiment_analyzer.py # 감성 분석 엔진
│   ├── weather_service.py   # 날씨 API 서비스
│   └── management/commands/ # Django 관리 명령어들
│
├── restaurant_api/          # 음식점 데이터 API
│   └── views.py            # 음식점 관련 API 엔드포인트
│
├── rest_api/               # REST API 엔드포인트
│   ├── views/             # API 뷰들
│   │   ├── briefing.py    # 브리핑 API
│   │   ├── sentiment.py   # 감성 분석 API
│   │   └── location.py    # 지역 정보 API
│   └── serializers/       # API 직렬화
│
├── crawling_scripts/       # 외부 데이터 수집 스크립트
│   ├── method1_recent_restaurants/  # 최신 음식점 크롤링
│   └── method2_popular_restaurants/ # 인기 음식점 크롤링
│
├── aws_services.py         # AWS 서비스 연동
├── aws_utils.py           # AWS 유틸리티 함수
└── manage.py              # Django 관리 스크립트
```

## 🎯 핵심 앱별 기능

### 1. local_data (지역 데이터 & 감성 분석)
**주요 모델:**
- `Location` - 서울시 구 단위 지역 정보
- `RawData` - 크롤링된 원시 데이터
- `LocalIssue` - YouTube, 네이버 뉴스에서 수집한 동네 이슈
- `SentimentAnalysis` - 감성 분석 결과 (-10~+10 점수)
- `SentimentSummary` - 일별 지역 감성 온도 요약
- `DistrictAnnouncement` - 구청 공지사항
- `RestaurantInfo` - 음식점 정보

**주요 기능:**
- 지역별 브리핑 데이터 생성
- 감성 온도계 시스템 (지역별 감성 지수 계산)
- YouTube/네이버 뉴스 크롤링
- 실시간 날씨 정보 제공

### 2. restaurant_api (음식점 API)
- 서울시 공공데이터 기반 음식점 정보 제공
- 신규 개업 음식점 필터링
- 인기 음식점 추천 알고리즘

### 3. rest_api (REST API)
- 프론트엔드용 JSON API 제공
- 브리핑 데이터 API
- 감성 분석 결과 API
- 지역 정보 API

### 4. crawling_scripts (크롤링 스크립트)
- 독립적으로 실행 가능한 데이터 수집 스크립트
- 음식점 데이터 수집 (공공데이터 API)
- 배치 작업용 스크립트

## 🔄 데이터 플로우

1. **데이터 수집**
   ```
   크롤링 스크립트 → RawData 저장 → 감성 분석 → SentimentAnalysis 저장
   ```

2. **브리핑 생성**
   ```
   지역 선택 → 감성 요약 계산 → 날씨/뉴스/음식점 데이터 조합 → 브리핑 출력
   ```

3. **감성 온도계**
   ```
   일별 감성 분석 → 감성 온도 계산 → SentimentSummary 업데이트 → 대시보드 표시
   ```

## 🛠 주요 Django 관리 명령어

```bash
# 감성 분석 실행
python manage.py analyze_sentiment

# 일일 크롤링 및 분석
python manage.py daily_crawl_and_analyze

# 동네 이슈 크롤링
python manage.py crawl_local_issues

# AWS 인프라 설정
python manage.py setup_aws_infrastructure

# 데이터베이스 데이터 확인
python manage.py show_db_data
```

## 🌐 AWS 연동

- **RDS**: PostgreSQL 데이터베이스
- **ECS**: 컨테이너 배포
- **CloudWatch**: 로그 및 모니터링
- **S3**: 정적 파일 저장

## 📊 감성 온도계 시스템

LocalBriefing의 핵심 기능으로, 지역별 감성 지수를 실시간으로 계산합니다:

- **수집**: YouTube, 네이버 뉴스에서 지역 관련 콘텐츠 크롤링
- **분석**: 한국어 감성 분석으로 긍정/부정/중립 분류
- **계산**: 조회수, 댓글수 등을 가중치로 감성 온도 산출
- **시각화**: -100°(매우 부정) ~ +100°(매우 긍정) 온도계로 표시

이 시스템을 통해 사용자는 자신이 거주하는 지역의 실시간 감성 상태를 한눈에 파악할 수 있습니다.