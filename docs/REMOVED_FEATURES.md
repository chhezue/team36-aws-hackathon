# 제거된 기능 목록

## 소셜 로그인 및 사용자 인증 시스템 완전 제거

### 제거된 모델
- `User` (AbstractUser 기반 커스텀 사용자 모델)
- `Briefing` (사용자별 브리핑 데이터)

### 제거된 뷰 및 URL
- `kakao_login` - 카카오 소셜 로그인
- `naver_login` - 네이버 소셜 로그인  
- `kakao_callback` - 카카오 로그인 콜백
- `naver_callback` - 네이버 로그인 콜백
- `email_login` - 이메일 로그인

### 제거된 설정
- `AUTH_USER_MODEL` - 커스텀 사용자 모델 설정
- `django.contrib.auth` - Django 인증 앱
- `django.contrib.admin` - Django 관리자 페이지
- `AuthenticationMiddleware` - 인증 미들웨어
- 소셜 로그인 API 키 설정들

### 제거된 템플릿 요소
- 온보딩 페이지의 카카오/네이버 로그인 버튼
- 설정 페이지의 사용자 이메일 표시

### 제거된 환경변수
- `KAKAO_CLIENT_ID`
- `NAVER_CLIENT_ID` 
- `NAVER_CLIENT_SECRET`
- `NAVER_LOGIN_CLIENT_ID`
- `NAVER_LOGIN_CLIENT_SECRET`

### 제거된 파일
- `docs/SOCIAL_LOGIN_SETUP.md` - 소셜 로그인 설정 가이드
- `users/admin.py` - Django 관리자 설정

## 현재 상태

이제 LocalBriefing은 **완전한 비회원 서비스**로 동작합니다:

- 사용자 등록/로그인 없이 바로 사용 가능
- 세션 기반으로 사용자 설정 저장 (거주지, 카테고리 선택 등)
- 모든 브리핑 데이터는 지역 기반으로 제공
- 개인화된 데이터 저장 없음

## 영향받는 기능

1. **브리핑 개인화**: 사용자별 브리핑 히스토리 저장 불가
2. **설정 영속성**: 브라우저 세션이 끝나면 설정 초기화
3. **관리자 페이지**: Django admin 접근 불가
4. **사용자 분석**: 개별 사용자 추적 불가

## 대안 방안

- 브라우저 localStorage를 활용한 클라이언트 사이드 설정 저장
- 쿠키 기반 사용자 선호도 저장
- 지역별 통계 데이터 활용