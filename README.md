# LocalBriefing 프로토타입

UI/UX 디자인 문서를 기반으로 구현한 Django 템플릿 목업입니다.

## 실행 방법

### 1. 가상환경 생성 및 활성화
```bash
cd /Users/sesil/PycharmProjects/team36-aws-hackathon
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Django 프로젝트 실행
```bash
cd localbriefing
python manage.py migrate
python manage.py runserver
```

### 4. 브라우저에서 확인
- 온보딩: http://127.0.0.1:8000/
- 브리핑: http://127.0.0.1:8000/briefing/
- 설정: http://127.0.0.1:8000/settings/

## 구현된 화면

1. **온보딩 화면** (`/`)
   - 4단계 온보딩 프로세스
   - 이메일/카카오 로그인 선택
   - 거주지 설정 (구/동 선택)
   - 관심 카테고리 선택
   - 완료 화면

2. **메인 브리핑 화면** (`/briefing/`)
   - 사용자 인사말 및 위치 정보
   - 날씨 정보 카드
   - 구청 소식, 동네 이슈, 중고거래, 맛집 정보 카드
   - 이전 브리핑/설정 버튼

3. **설정 화면** (`/settings/`)
   - 계정 정보 관리
   - 거주지 변경
   - 브리핑 카테고리 토글
   - 알림 설정
   - 기타 메뉴

## 기술 스택

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Design**: 모바일 우선 반응형 디자인
- **Icons**: 이모지 활용

## 주요 특징

- 모바일 최적화 (최대 너비 400px)
- 직관적인 UI/UX
- 부드러운 애니메이션 효과
- 카테고리별 색상 구분
- 토글 스위치 인터랙션