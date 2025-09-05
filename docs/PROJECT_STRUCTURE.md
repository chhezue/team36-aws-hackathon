# LocalBriefing 프로젝트 구조

```
team36-aws-hackathon/
├── .amazonq/                       # Amazon Q 설정
│   └── rules/hackathon.md
│
├── backend/                        # 🌐 Django 백엔드
│   ├── localbriefing/              # Django 프로젝트 설정
│   │   ├── settings.py             # Django 설정
│   │   ├── urls.py                 # URL 라우팅
│   │   └── wsgi.py                 # WSGI 설정
│   │
│   ├── local_data/                 # 📊 데이터 모델 및 처리
│   │   ├── models.py               # 데이터베이스 모델
│   │   ├── crawlers.py             # 동네 이슈 크롤링
│   │   ├── sentiment_analyzer.py   # 감성 분석
│   │   └── management/commands/    # Django 관리 명령어
│   │
│   ├── rest_api/                   # 🚀 REST API
│   │   ├── views/                  # API 뷰
│   │   └── serializers/            # 데이터 직렬화
│   │
│   ├── crawling_scripts/           # 🔍 데이터 수집
│   │   ├── method1_recent_restaurants/
│   │   └── method2_popular_restaurants/
│   │
│   └── manage.py                   # Django 관리 스크립트
│
├── frontend/                       # ⚛️ React/Next.js 프론트엔드
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   ├── components/             # React 컴포넌트
│   │   ├── hooks/                  # 커스텀 훅
│   │   ├── lib/                    # 유틸리티
│   │   └── types/                  # TypeScript 타입
│   │
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
│
├── docs/                           # 📋 프로젝트 문서
│   ├── PROJECT_OVERVIEW.md         # 프로젝트 개요
│   ├── ARCHITECTURE.md             # 시스템 아키텍처
│   ├── DATABASE.md                 # 데이터베이스 설계
│   ├── AWS_INTEGRATION.md          # AWS 서비스 연동
│   ├── REMOVED_FEATURES.md         # 제거된 기능 목록
│   └── RESTAURANT_API_IMPROVEMENTS.md # 맛집 API 개선사항
│
├── .env                            # 🔐 환경변수
├── .env.example                    # 환경변수 템플릿
├── requirements.txt                # 📦 Python 의존성
├── load_env.py                     # 환경변수 로더
└── README.md                       # 📖 프로젝트 설명서
```

## 핵심 디렉토리 설명

### 🌐 backend/
Django 백엔드 애플리케이션
- **local_data/**: 데이터 모델, 크롤링, 감성 분석 기능
- **rest_api/**: Django REST Framework API 엔드포인트
- **crawling_scripts/**: 데이터 수집 스크립트

### ⚛️ frontend/
React/Next.js 프론트엔드 애플리케이션
- **src/app/**: Next.js 13+ App Router 기반 페이지
- **src/components/**: 재사용 가능한 React 컴포넌트
- **TypeScript + Tailwind CSS**: 타입 안전성 및 스타일링

### 📋 docs/
프로젝트 설계 문서 및 가이드
- AWS 아키텍처 설계
- 데이터베이스 스키마
- 기능 개선 사항 및 제거된 기능 기록

## 주요 변경사항

1. **사용자 인증 시스템 제거**: 비회원 서비스로 전환
2. **프론트엔드 추가**: React/Next.js 기반 모던 UI
3. **데이터 모델 강화**: 감성 분석 및 동네 이슈 추가
4. **API 구조 개선**: REST API 엔드포인트 별도 구성