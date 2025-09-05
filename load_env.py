"""
전역 환경변수 로더
프로젝트 어디서든 import해서 사용 가능
"""
import os
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent
GLOBAL_ENV_PATH = PROJECT_ROOT / '.env'

def load_env():
    """전역 .env 파일 로드"""
    if not GLOBAL_ENV_PATH.exists():
        print(f"환경변수 파일을 찾을 수 없습니다: {GLOBAL_ENV_PATH}")
        return False
    
    with open(GLOBAL_ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    return True

def get_env(key, default=None):
    """환경변수 값 가져오기"""
    return os.getenv(key, default)

# 자동 로드
load_env()