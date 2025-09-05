import os
from pathlib import Path

# 프로젝트 루트 경로 찾기
PROJECT_ROOT = Path(__file__).parent.parent
GLOBAL_ENV_PATH = PROJECT_ROOT / '.env'

def load_env_file():
    """전역 환경변수 파일을 로드하는 함수"""
    if not GLOBAL_ENV_PATH.exists():
        print(f"전역 환경변수 파일을 찾을 수 없습니다: {GLOBAL_ENV_PATH}")
        return False
    
    with open(GLOBAL_ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    print(f"전역 환경변수 로드 완료: {GLOBAL_ENV_PATH}")
    return True

def get_api_key(key_name, default='sample_key'):
    """API 키를 가져오는 함수"""
    return os.getenv(key_name, default)

if __name__ == "__main__":
    load_env_file()
    print(f"SEOUL_API_KEY: {get_api_key('SEOUL_API_KEY')}")
    print(f"KAKAO_API_KEY: {get_api_key('KAKAO_API_KEY')}")