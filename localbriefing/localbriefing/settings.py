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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'restaurants',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'localbriefing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'localbriefing.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 커스텀 사용자 모델
AUTH_USER_MODEL = 'users.User'

# API 키 설정
SEOUL_API_KEY = os.environ.get('SEOUL_API_KEY')
KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY')
WEATHER_API_KEY = os.environ.get('DATA_GO_KR_API_KEY')

# 디버깅용 API 키 확인
print(f"WEATHER_API_KEY: {WEATHER_API_KEY[:10] if WEATHER_API_KEY else 'None'}...")

# 소셜 로그인 설정
KAKAO_CLIENT_ID = os.environ.get('KAKAO_API_KEY')
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

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