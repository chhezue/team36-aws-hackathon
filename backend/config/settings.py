import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드 (명시적 경로 지정)
env_path = BASE_DIR.parent / '.env'
load_dotenv(env_path)
print(f"ENV 파일 경로: {env_path}")
print(f"ENV 파일 존재: {env_path.exists()}")
print(f"DATA_GO_KR_API_KEY 환경변수: {os.environ.get('DATA_GO_KR_API_KEY', 'None')[:10]}...")

SECRET_KEY = 'django-insecure-prototype-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'local_data',
    'restaurant_api',
    'rest_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Templates removed - using React frontend

WSGI_APPLICATION = 'config.wsgi.application'

# 데이터베이스 설정 - AWS RDS PostgreSQL 사용
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'catsavetheworld_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 20,
        }
    }
}

print(f"DB 설정: {os.environ.get('DB_HOST')[:20]}... 사용 중")

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# API 키 설정
SEOUL_API_KEY = os.environ.get('SEOUL_API_KEY')
KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY')
WEATHER_API_KEY = os.environ.get('DATA_GO_KR_API_KEY')

# 디버깅용 API 키 확인
print(f"WEATHER_API_KEY: {WEATHER_API_KEY[:10] if WEATHER_API_KEY else 'None'}...")



# 테마 설정
DEFAULT_THEME = 'b'  # B안 테마를 기본값으로 설정
THEME_COLORS = {
    'primary': '#6A7954',
    'secondary': '#8FA876',
    'background': '#F5F3F0',
    'card': '#EAE0D5'
}

# AWS 설정
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = DEBUG  # 개발 환경에서만 모든 오리진 허용

# 프로덕션 환경에서 보안 설정
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    ALLOWED_HOSTS = ['*']  # 실제 도메인으로 변경 필요

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}