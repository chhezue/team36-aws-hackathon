import os
from pathlib import Path

def load_env_file(env_path='.env'):
    """환경변수 파일을 로드하는 함수"""
    env_file = Path(__file__).parent / env_path
    
    if not env_file.exists():
        print(f"환경변수 파일 {env_file}이 존재하지 않습니다.")
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    print("환경변수 로드 완료")

def get_api_key(key_name, default='sample_key'):
    """API 키를 가져오는 함수"""
    return os.getenv(key_name, default)

if __name__ == "__main__":
    load_env_file()
    print(f"SEOUL_API_KEY: {get_api_key('SEOUL_API_KEY')}")
    print(f"KAKAO_API_KEY: {get_api_key('KAKAO_API_KEY')}")