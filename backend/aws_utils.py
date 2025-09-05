import os
import boto3
from django.conf import settings

def get_rds_client():
    """AWS RDS 클라이언트 생성"""
    return boto3.client(
        'rds',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION
    )

def create_rds_instance():
    """RDS PostgreSQL 인스턴스 생성"""
    client = get_rds_client()
    
    try:
        response = client.create_db_instance(
            DBInstanceIdentifier='localbriefing-db',
            DBInstanceClass='db.t3.micro',  # 프리티어
            Engine='postgres',
            MasterUsername='postgres',
            MasterUserPassword=os.environ.get('DB_PASSWORD', 'localbriefing123!'),
            AllocatedStorage=20,
            VpcSecurityGroupIds=[
                # 보안 그룹 ID 필요
            ],
            DBName='localbriefing_db',
            BackupRetentionPeriod=7,
            MultiAZ=False,
            PubliclyAccessible=True,
            StorageType='gp2',
            StorageEncrypted=True
        )
        print(f"RDS 인스턴스 생성 시작: {response['DBInstance']['DBInstanceIdentifier']}")
        return response
    except Exception as e:
        print(f"RDS 인스턴스 생성 실패: {str(e)}")
        return None

def get_rds_endpoint(db_instance_identifier='localbriefing-db'):
    """RDS 엔드포인트 조회"""
    client = get_rds_client()
    
    try:
        response = client.describe_db_instances(
            DBInstanceIdentifier=db_instance_identifier
        )
        
        db_instance = response['DBInstances'][0]
        endpoint = db_instance['Endpoint']['Address']
        port = db_instance['Endpoint']['Port']
        status = db_instance['DBInstanceStatus']
        
        print(f"RDS 상태: {status}")
        print(f"엔드포인트: {endpoint}:{port}")
        
        return {
            'endpoint': endpoint,
            'port': port,
            'status': status
        }
    except Exception as e:
        print(f"RDS 정보 조회 실패: {str(e)}")
        return None

def test_db_connection():
    """데이터베이스 연결 테스트"""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"데이터베이스 연결 성공: {result}")
            return True
    except Exception as e:
        print(f"데이터베이스 연결 실패: {str(e)}")
        return False

if __name__ == "__main__":
    # 스크립트 직접 실행 시 RDS 정보 조회
    get_rds_endpoint()