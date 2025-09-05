import os
from pathlib import Path

def load_env_file(env_path='.env'):
    """환경변수 파일을 로드하는 함수"""
    # 여러 경로에서 .env 파일 찾기
    possible_paths = [
        Path(env_path),  # 직접 지정된 경로
        Path(__file__).parent / env_path,  # load_env.py 기준
        Path('.env'),  # 현재 디렉토리
        Path('../.env'),  # 상위 디렉토리
        Path('../../.env')  # 2단계 상위
    ]
    
    env_file = None
    for path in possible_paths:
        if path.exists():
            env_file = path
            break
    
    if not env_file:
        print(f"환경변수 파일을 찾을 수 없습니다. 찾은 경로: {[str(p) for p in possible_paths]}")
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