#!/bin/bash

echo "LocalBriefing 프로젝트에 Prettier와 ESLint 설정 중..."

# Node.js 설치 확인
if ! command -v node &> /dev/null; then
    echo "Node.js가 설치되어 있지 않습니다. Node.js를 먼저 설치해주세요."
    echo "https://nodejs.org에서 다운로드할 수 있습니다."
    exit 1
fi

# npm 패키지 설치
echo "npm 패키지 설치 중..."
npm install

echo ""
echo "설정 완료! 다음 명령어들을 사용할 수 있습니다:"
echo ""
echo "📝 코드 포맷팅:"
echo "  npm run format        # 모든 JS/HTML 파일 포맷팅"
echo "  npm run format:check  # 포맷팅 확인만"
echo ""
echo "🔍 코드 검사:"
echo "  npm run lint          # ESLint로 코드 검사"
echo "  npm run lint:fix      # ESLint 자동 수정"
echo ""
echo "PyCharm 설정:"
echo "1. File > Settings > Languages & Frameworks > JavaScript > Prettier"
echo "2. Prettier package 경로: $(pwd)/node_modules/prettier"
echo "3. 'On code reformat' 및 'On save' 체크"
echo ""