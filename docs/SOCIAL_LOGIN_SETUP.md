# 소셜 로그인 설정 가이드

## 구현 완료 사항

✅ **네이버 소셜 로그인**
- 네이버 개발자센터 애플리케이션 등록 필요
- 콜백 URL: `http://127.0.0.1:8000/users/naver/callback/`

✅ **카카오 소셜 로그인**  
- 카카오 개발자센터 애플리케이션 등록 필요
- 콜백 URL: `http://127.0.0.1:8000/users/kakao/callback/`

## 환경변수 설정

`.env` 파일에 다음 값들을 설정하세요:

```bash
# 카카오 로그인
KAKAO_CLIENT_ID=your_kakao_client_id

# 네이버 로그인  
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

## 개발자센터 설정

### 1. 카카오 개발자센터
1. https://developers.kakao.com 접속
2. 애플리케이션 추가하기
3. 플랫폼 설정 > Web > 사이트 도메인: `http://127.0.0.1:8000`
4. 카카오 로그인 > Redirect URI: `http://127.0.0.1:8000/users/kakao/callback/`
5. 동의항목 > 이메일, 닉네임 필수 동의로 설정

### 2. 네이버 개발자센터
1. https://developers.naver.com 접속
2. 애플리케이션 등록
3. 사용 API: 네이버 로그인
4. 서비스 URL: `http://127.0.0.1:8000`
5. Callback URL: `http://127.0.0.1:8000/users/naver/callback/`

## 사용 방법

1. 온보딩 페이지에서 "카카오로 시작하기" 또는 "네이버로 시작하기" 클릭
2. 각 플랫폼의 로그인 페이지로 이동
3. 로그인 완료 후 자동으로 브리핑 페이지로 이동
4. 사용자 정보는 자동으로 데이터베이스에 저장

## 구현된 기능

- 소셜 로그인 인증 플로우
- 사용자 자동 생성/로그인
- 세션 관리
- 사용자 정보 저장 (닉네임, 이메일)