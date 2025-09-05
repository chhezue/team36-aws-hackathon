# 새로운 음식점 정보 수집 방법들

## Method 1: 서울시 공공데이터 API
- **폴더**: `method1_seoul_api/`
- **설명**: 서울시 열린데이터광장 API 활용
- **장점**: 공식 데이터, 실시간 업데이트
- **사용법**:
```bash
cd method1_seoul_api
pip install -r requirements.txt
python seoul_api.py
```

## Method 2: 웹 크롤링
- **폴더**: `method2_web_crawling/`
- **설명**: 강남구청 홈페이지 크롤링
- **장점**: 최신 공지사항 정보
- **주의**: robots.txt 준수 필요
- **사용법**:
```bash
cd method3_web_crawling
pip install -r requirements.txt
python gangnam_crawler.py
```

## Method 3: CSV + API 조합
- **폴더**: `method3_csv_api_combo/`
- **설명**: 기존 CSV 데이터 + 카카오 API 보강
- **장점**: 정확한 데이터 + 추가 정보
- **사용법**:
```bash
cd method4_csv_api_combo
pip install -r requirements.txt
python csv_api_processor.py
```

## 환경변수 설정
```bash
export SEOUL_API_KEY="your_seoul_api_key"
export KAKAO_API_KEY="your_kakao_api_key"
```

## 추천 순서
1. **Method 1** (서울시 API) - 가장 신뢰할 수 있는 공식 데이터
2. **Method 3** (CSV + API) - 현실적이고 실용적
3. **Method 2** (웹 크롤링) - 보조적 정보 수집용
