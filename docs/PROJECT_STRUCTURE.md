# LocalBriefing 프로젝트 구조 (정리 완료)

```
team36-aws-hackathon/
├── docs/                           # 📋 프로젝트 문서
│   ├── PROJECT_OVERVIEW.md         # 프로젝트 개요
│   ├── ARCHITECTURE.md             # 시스템 아키텍처
│   ├── DATABASE.md                 # 데이터베이스 설계
│   ├── AWS_INTEGRATION.md          # AWS 서비스 연동
│   ├── SOCIAL_LOGIN_SETUP.md       # 소셜 로그인 설정 가이드
│   └── IMPLEMENTATION_PLAN.md      # 구현 계획
│
├── localbriefing/                  # 🌐 Django 웹 애플리케이션
│   ├── localbriefing/              # Django 프로젝트 설정
│   │   ├── settings.py             # Django 설정
│   │   ├── urls.py                 # URL 라우팅
│   │   └── wsgi.py                 # WSGI 설정
│   │
│   ├── users/                      # 👤 사용자 관리 앱
│   │   ├── models.py               # 사용자 모델 (소셜 로그인)
│   │   ├── views.py                # 소셜 로그인 뷰
│   │   └── urls.py                 # 사용자 URL 패턴
│   │
│   ├── restaurants/                # 🍽️ 맛집 정보 앱
│   │   └── views.py                # 맛집 API 뷰
│   │
│   ├── templates/                  # 🎨 HTML 템플릿
│   │   ├── base.html               # 기본 템플릿
│   │   ├── onboarding.html         # 온보딩 페이지
│   │   ├── briefing.html           # 브리핑 페이지
│   │   └── settings.html           # 설정 페이지
│   │
│   ├── static/                     # 📁 정적 파일
│   │   ├── css/style.css           # 스타일시트
│   │   └── js/app.js               # JavaScript
│   │
│   ├── .env                        # 🔐 환경변수 (소셜 로그인 키)
│   └── manage.py                   # Django 관리 스크립트
│
├── data_sources/                   # 📊 데이터 수집 모듈
│   ├── method1_recent_restaurants/ # 최신 음식점 데이터
│   ├── method2_popular_restaurants/# 인기 음식점 데이터
│   └── load_env.py                 # 환경변수 로더
│
├── scripts/                        # 🔧 유틸리티 스크립트
│   ├── main.py                     # 메인 실행 스크립트
│   ├── test_all_districts.py       # 전체 구 테스트
│   └── test_districts.py           # 구별 테스트
│
├── config/                         # ⚙️ 개발 도구 설정
│   ├── .editorconfig               # 에디터 설정
│   ├── .prettierrc                 # 코드 포맷터 설정
│   └── eslint.config.js            # 린터 설정
│
├── requirements.txt                # 📦 Python 패키지 의존성
├── README.md                       # 📖 프로젝트 설명서
└── .gitignore                      # 🚫 Git 제외 파일
```

## 핵심 디렉토리 설명

### 🌐 localbriefing/
Django 웹 애플리케이션의 메인 디렉토리
- **users/**: 소셜 로그인 기능 구현
- **restaurants/**: 맛집 정보 API
- **templates/**: 모바일 최적화 UI 템플릿
- **static/**: CSS/JS 정적 파일

### 📊 data_sources/
데이터 수집 및 처리 모듈
- 서울시 음식점 API 연동
- 구청 공지사항 크롤링 준비

### 📋 docs/
프로젝트 설계 문서 및 가이드
- AWS 아키텍처 설계
- 데이터베이스 스키마
- 소셜 로그인 설정 가이드

### 🔧 scripts/
테스트 및 유틸리티 스크립트

### ⚙️ config/
개발 도구 설정 파일들