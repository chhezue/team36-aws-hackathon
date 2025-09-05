# AWS 배포 가이드

## 1. AWS RDS PostgreSQL 인스턴스 생성

### AWS CLI로 생성
```bash
aws rds create-db-instance \
    --db-instance-identifier localbriefing-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password "YourSecurePassword123!" \
    --allocated-storage 20 \
    --db-name localbriefing_db \
    --backup-retention-period 7 \
    --no-multi-az \
    --publicly-accessible \
    --storage-type gp2 \
    --storage-encrypted \
    --region ap-northeast-2
```

### AWS 콘솔에서 생성
1. RDS 콘솔 접속
2. "데이터베이스 생성" 클릭
3. PostgreSQL 선택
4. 프리 티어 템플릿 선택
5. 설정:
   - DB 인스턴스 식별자: `localbriefing-db`
   - 마스터 사용자 이름: `postgres`
   - 마스터 암호: 안전한 암호 설정
   - DB 인스턴스 클래스: `db.t3.micro`
   - 스토리지: 20GB
   - 퍼블릭 액세스: 예

## 2. 보안 그룹 설정

RDS 인스턴스의 보안 그룹에서 PostgreSQL 포트(5432) 허용:
- 유형: PostgreSQL
- 포트: 5432
- 소스: 0.0.0.0/0 (개발용) 또는 특정 IP

## 3. 환경변수 설정

`.env` 파일에 다음 내용 추가:
```env
# AWS RDS 설정
DB_ENGINE=postgresql
DB_NAME=localbriefing_db
DB_USER=postgres
DB_PASSWORD=YourSecurePassword123!
DB_HOST=localbriefing-db.xxxxxxxxx.ap-northeast-2.rds.amazonaws.com
DB_PORT=5432

# AWS 인증 정보
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-northeast-2
```

## 4. 패키지 설치 및 마이그레이션

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# 데이터베이스 연결 테스트
python manage.py setup_aws_db --test

# 마이그레이션 실행
python manage.py setup_aws_db --migrate --load-data
```

## 5. EC2 배포 (선택사항)

### EC2 인스턴스 생성
1. Amazon Linux 2 AMI 선택
2. t2.micro 인스턴스 타입
3. 보안 그룹에서 HTTP(80), HTTPS(443), SSH(22) 포트 열기

### 배포 스크립트
```bash
#!/bin/bash
# EC2 인스턴스에서 실행

# 시스템 업데이트
sudo yum update -y

# Python 3.9 설치
sudo yum install python3 python3-pip git -y

# 프로젝트 클론
git clone https://github.com/your-repo/team36-aws-hackathon.git
cd team36-aws-hackathon

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집 필요

# Django 설정
cd localbriefing
python manage.py setup_aws_db --migrate --load-data
python manage.py collectstatic --noinput

# Gunicorn으로 서버 실행
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 localbriefing.wsgi:application
```

## 6. 데이터 마이그레이션 (SQLite → PostgreSQL)

기존 SQLite 데이터를 PostgreSQL로 이전:

```bash
# 1. SQLite에서 데이터 덤프
python manage.py dumpdata --natural-foreign --natural-primary > data_backup.json

# 2. PostgreSQL 설정으로 변경
# .env 파일에서 DB_ENGINE=postgresql 설정

# 3. PostgreSQL에 마이그레이션
python manage.py migrate

# 4. 데이터 로드
python manage.py loaddata data_backup.json
```

## 7. 모니터링 및 로그

### CloudWatch 로그 설정
```python
# settings.py에 추가
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'cloudwatch': {
            'class': 'watchtower.CloudWatchLogsHandler',
            'log_group': 'localbriefing-logs',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['cloudwatch'],
            'level': 'INFO',
        },
    },
}
```

## 8. 백업 및 복구

### 자동 백업 설정
RDS 인스턴스는 자동으로 7일간 백업 보관

### 수동 스냅샷
```bash
aws rds create-db-snapshot \
    --db-instance-identifier localbriefing-db \
    --db-snapshot-identifier localbriefing-snapshot-$(date +%Y%m%d)
```

## 9. 비용 최적화

- RDS 인스턴스: db.t3.micro (프리티어)
- 스토리지: 20GB (프리티어 한도 내)
- 백업: 7일 (기본값)
- 사용하지 않을 때 인스턴스 중지

## 10. 보안 체크리스트

- [ ] RDS 암호화 활성화
- [ ] 보안 그룹 최소 권한 원칙
- [ ] IAM 역할 기반 액세스
- [ ] SSL/TLS 연결 강제
- [ ] 정기적인 보안 패치
- [ ] 액세스 로그 모니터링