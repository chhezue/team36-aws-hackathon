# VibeThermo 문서 가이드

VibeThermo 프로젝트의 전체 문서 모음입니다.

## 📋 핵심 문서

### 프로젝트 개요
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 프로젝트 전체 개요 및 비전
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 프로젝트 폴더 구조 및 구성

### 기술 설계
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 시스템 아키텍처 및 AWS 서비스 구성
- **[DATABASE.md](DATABASE.md)** - 데이터베이스 스키마 및 모델 설계
- **[AWS_INTEGRATION.md](AWS_INTEGRATION.md)** - AWS 서비스 연동 가이드
- **[AWS_TECH_GUIDE.md](AWS_TECH_GUIDE.md)** - AWS 기술 선택 및 구현 가이드

### 기능 구현
- **[CRAWLING_SYSTEM.md](CRAWLING_SYSTEM.md)** - 동네 이슈 크롤링 시스템
- **[RESTAURANT_API_IMPROVEMENTS.md](RESTAURANT_API_IMPROVEMENTS.md)** - 맛집 API 개선사항
- **[UI_UX_DESIGN.md](UI_UX_DESIGN.md)** - 사용자 인터페이스 설계

### 개발 가이드
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - 구현 현황 및 향후 계획
- **[ENV_SETUP.md](ENV_SETUP.md)** - 환경변수 설정 가이드
- **[PLATFORM_CHOICE.md](PLATFORM_CHOICE.md)** - 플랫폼 및 기술 선택 가이드
- **[FRONTEND_MIGRATION.md](FRONTEND_MIGRATION.md)** - 프론트엔드 마이그레이션 가이드

### 변경 이력
- **[REMOVED_FEATURES.md](REMOVED_FEATURES.md)** - 제거된 기능 목록 및 사유

## 🚀 빠른 시작

### 1. 프로젝트 이해
```
PROJECT_OVERVIEW.md → ARCHITECTURE.md → PROJECT_STRUCTURE.md
```

### 2. 개발 환경 설정
```
ENV_SETUP.md → DATABASE.md → AWS_INTEGRATION.md
```

### 3. 기능 구현 이해
```
CRAWLING_SYSTEM.md → RESTAURANT_API_IMPROVEMENTS.md → UI_UX_DESIGN.md
```

## 📊 프로젝트 현황

- ✅ **MVP 구현 완료**: Django 백엔드 + Next.js 프론트엔드
- ✅ **데이터 수집**: 25개 서울시 구 동네 이슈 크롤링
- ✅ **감성 분석**: 한국어 감성 온도 측정 시스템
- ✅ **맛집 API**: 실시간 인기 맛집 TOP 5 수집
- 🔄 **AWS 배포**: RDS, Lambda, EventBridge 설정 중

## 🔧 기술 스택

- **Backend**: Django 4.2.7 + Django REST Framework
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Database**: PostgreSQL (AWS RDS)
- **Infrastructure**: AWS Lambda + EventBridge + Elastic Beanstalk
- **AI/ML**: 자체 구현 한국어 감성 분석 엔진

## 📝 문서 업데이트 이력

- **2025-01-09**: 프로젝트 구조 변경 반영, 중복 문서 정리
- **2025-01-08**: 감성 분석 기능 추가, 사용자 인증 시스템 제거
- **2025-01-07**: Next.js 프론트엔드 추가, API 구조 개선

## 🤝 기여 가이드

문서 수정이나 추가가 필요한 경우:
1. 해당 기능의 구현 상태 확인
2. 관련 문서 업데이트
3. README.md 업데이트 이력 추가