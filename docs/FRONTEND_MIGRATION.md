# LocalBriefing 프론트엔드 마이그레이션 가이드

## 개요

기존 Django 템플릿 기반 프로젝트를 유지하면서 React/Next.js 프론트엔드를 추가하는 구조입니다.

## 새로운 폴더 구조

```
team36-aws-hackathon/
├── localbriefing/                    # 기존 Django 백엔드 (유지)
│   ├── localbriefing/
│   ├── users/
│   ├── templates/
│   ├── static/
│   └── manage.py
├── frontend/                         # 새로운 React/Next.js 프론트엔드
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/                      # Next.js 13+ App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # 메인 페이지
│   │   │   ├── onboarding/
│   │   │   │   └── page.tsx
│   │   │   ├── briefing/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── components/               # 재사용 컴포넌트
│   │   │   ├── ui/                   # 기본 UI 컴포넌트
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── Toggle.tsx
│   │   │   ├── layout/               # 레이아웃 컴포넌트
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Navigation.tsx
│   │   │   ├── briefing/             # 브리핑 관련 컴포넌트
│   │   │   │   ├── WeatherCard.tsx
│   │   │   │   ├── NewsCard.tsx
│   │   │   │   ├── RestaurantCard.tsx
│   │   │   │   └── SentimentModal.tsx
│   │   │   └── onboarding/           # 온보딩 관련 컴포넌트
│   │   │       ├── StepIndicator.tsx
│   │   │       ├── LocationSelector.tsx
│   │   │       └── CategorySelector.tsx
│   │   ├── hooks/                    # 커스텀 훅
│   │   │   ├── useAuth.ts
│   │   │   ├── useBriefing.ts
│   │   │   └── useLocation.ts
│   │   ├── lib/                      # 유틸리티 및 설정
│   │   │   ├── api.ts                # API 클라이언트
│   │   │   ├── auth.ts               # 인증 관련
│   │   │   ├── utils.ts              # 공통 유틸리티
│   │   │   └── constants.ts          # 상수 정의
│   │   ├── types/                    # TypeScript 타입 정의
│   │   │   ├── auth.ts
│   │   │   ├── briefing.ts
│   │   │   └── api.ts
│   │   └── styles/                   # 스타일 파일
│   │       ├── globals.css
│   │       └── components.css
│   └── public/                       # 정적 파일
│       ├── icons/
│       └── images/
├── docs/                             # 문서 (기존 유지)
├── requirements.txt                  # Python 의존성 (기존)
├── package.json                      # 루트 패키지 관리
└── README.md
```

## API 통신 구조

### Django REST API 엔드포인트
```
localbriefing/api/
├── __init__.py
├── urls.py
├── views/
│   ├── __init__.py
│   ├── auth.py
│   ├── briefing.py
│   ├── location.py
│   └── sentiment.py
└── serializers/
    ├── __init__.py
    ├── auth.py
    ├── briefing.py
    └── location.py
```

### API 엔드포인트 설계
```
/api/v1/
├── auth/
│   ├── login/
│   ├── logout/
│   ├── register/
│   └── profile/
├── briefing/
│   ├── today/
│   ├── history/
│   └── categories/
├── location/
│   ├── districts/
│   └── update/
└── sentiment/
    ├── summary/
    └── details/
```

## 개발 환경 설정

### 1. 백엔드 (Django)
```bash
cd localbriefing
python manage.py runserver 8000
```

### 2. 프론트엔드 (Next.js)
```bash
cd frontend
npm run dev  # 포트 3000
```

### 3. 프록시 설정
Next.js에서 Django API로 프록시 설정:
```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ]
  }
}
```

## 기술 스택

### 프론트엔드
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Animation**: Framer Motion

### 백엔드 (기존 유지)
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL (AWS RDS)
- **API**: Django REST Framework

## 마이그레이션 단계

### Phase 1: API 개발
1. Django REST Framework 설치
2. API 엔드포인트 구현
3. CORS 설정

### Phase 2: 프론트엔드 기본 구조
1. Next.js 프로젝트 초기화
2. 기본 컴포넌트 구현
3. API 클라이언트 설정

### Phase 3: 페이지별 마이그레이션
1. 온보딩 페이지
2. 브리핑 페이지
3. 설정 페이지

### Phase 4: 고급 기능
1. 감성 분석 시각화
2. 실시간 업데이트
3. PWA 기능

## 배포 구조

### 개발 환경
- Django: localhost:8000
- Next.js: localhost:3000

### 프로덕션 환경
- Django API: api.localbriefing.com
- Next.js Frontend: localbriefing.com
- Static Files: AWS S3 + CloudFront

이 구조를 통해 기존 Django 프로젝트를 유지하면서 점진적으로 React/Next.js로 마이그레이션할 수 있습니다.