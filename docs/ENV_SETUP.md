# 환경변수 설정 가이드

## 파일 구조
```
data_sources/
├── .env.example          # 환경변수 템플릿
├── .env                  # 실제 환경변수 (git에 포함되지 않음)
├── load_env.py          # Python 환경변수 로더
├── setup_env.sh         # 환경변수 설정 스크립트
└── ENV_SETUP.md         # 이 파일
```

## 설정 방법

### 1. 자동 설정
```bash
cd data_sources
./setup_env.sh
```

### 2. 수동 설정
```bash
# .env 파일 생성
cp .env.example .env

# API 키 입력 (실제 키로 변경)
vi .env

# 환경변수 로드
source setup_env.sh
```

### 3. Python에서 사용
```python
from load_env import load_env_file, get_api_key

# 환경변수 로드
load_env_file()

# API 키 사용
seoul_key = get_api_key('SEOUL_API_KEY')
kakao_key = get_api_key('KAKAO_API_KEY')
```

## API 키 발급처

### 서울시 열린데이터광장
- URL: https://data.seoul.go.kr/
- 회원가입 → 데이터셋 신청 → API 키 발급

### 카카오 개발자
- URL: https://developers.kakao.com/
- 앱 생성 → REST API 키 복사

### 네이버 개발자 (선택)
- URL: https://developers.naver.com/
- 애플리케이션 등록 → Client ID/Secret 발급

### 공공데이터포털 (선택)
- URL: https://www.data.go.kr/
- 회원가입 → 활용신청 → 인증키 발급

## 보안 주의사항
- `.env` 파일은 git에 커밋하지 마세요
- API 키는 외부에 노출되지 않도록 주의하세요
- 정기적으로 API 키를 갱신하세요