import boto3
import os
from django.conf import settings
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class AWSBaseService(ABC):
    """AWS 서비스 기본 클래스"""
    
    def __init__(self):
        self.region = getattr(settings, 'AWS_DEFAULT_REGION', 'ap-northeast-2')
        self.access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        self.secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    
    def get_client(self, service_name: str):
        """AWS 클라이언트 생성"""
        return boto3.client(
            service_name,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

class RDSService(AWSBaseService):
    """RDS 관리 서비스"""
    
    def __init__(self):
        super().__init__()
        self.client = self.get_client('rds')
        self.db_instance_id = 'localbriefing-db'
    
    def create_instance(self, password: str) -> Dict[str, Any]:
        """RDS 인스턴스 생성"""
        try:
            response = self.client.create_db_instance(
                DBInstanceIdentifier=self.db_instance_id,
                DBInstanceClass='db.t3.micro',
                Engine='postgres',
                MasterUsername='postgres',
                MasterUserPassword=password,
                AllocatedStorage=20,
                DBName='localbriefing_db',
                BackupRetentionPeriod=7,
                MultiAZ=False,
                PubliclyAccessible=True,
                StorageType='gp2',
                StorageEncrypted=True
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_endpoint(self) -> Optional[str]:
        """RDS 엔드포인트 조회"""
        try:
            response = self.client.describe_db_instances(
                DBInstanceIdentifier=self.db_instance_id
            )
            instance = response['DBInstances'][0]
            return instance['Endpoint']['Address']
        except Exception as e:
            print(f"RDS 엔드포인트 조회 실패: {e}")
            return None
    
    def get_status(self) -> Dict[str, str]:
        """RDS 상태 조회"""
        try:
            response = self.client.describe_db_instances(
                DBInstanceIdentifier=self.db_instance_id
            )
            instance = response['DBInstances'][0]
            return {
                'status': instance['DBInstanceStatus'],
                'endpoint': instance.get('Endpoint', {}).get('Address', 'N/A'),
                'port': str(instance.get('Endpoint', {}).get('Port', 5432))
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

class ECSService(AWSBaseService):
    """ECS 크롤링 작업 관리"""
    
    def __init__(self):
        super().__init__()
        self.client = self.get_client('ecs')
        self.cluster_name = 'localbriefing-cluster'
        self.task_definition = 'localbriefing-crawler'
    
    def create_cluster(self) -> Dict[str, Any]:
        """ECS 클러스터 생성"""
        try:
            response = self.client.create_cluster(
                clusterName=self.cluster_name,
                capacityProviders=['FARGATE']
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_crawler_task(self, district: str = None) -> Dict[str, Any]:
        """크롤링 작업 실행"""
        try:
            overrides = {
                'containerOverrides': [{
                    'name': 'crawler',
                    'environment': [
                        {'name': 'DISTRICT', 'value': district or 'all'},
                        {'name': 'DB_HOST', 'value': os.getenv('DB_HOST', '')},
                        {'name': 'DB_PASSWORD', 'value': os.getenv('DB_PASSWORD', '')}
                    ]
                }]
            }
            
            response = self.client.run_task(
                cluster=self.cluster_name,
                taskDefinition=self.task_definition,
                launchType='FARGATE',
                overrides=overrides
            )
            return {'success': True, 'task_arn': response['tasks'][0]['taskArn']}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class EventBridgeService(AWSBaseService):
    """EventBridge 스케줄링 서비스"""
    
    def __init__(self):
        super().__init__()
        self.client = self.get_client('events')
        self.rule_name = 'localbriefing-daily-crawl'
    
    def create_schedule(self) -> Dict[str, Any]:
        """매일 자정 크롤링 스케줄 생성"""
        try:
            # 매일 자정 KST (UTC 15:00)
            response = self.client.put_rule(
                Name=self.rule_name,
                ScheduleExpression='cron(0 15 * * ? *)',
                Description='LocalBriefing 일일 크롤링',
                State='ENABLED'
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_target(self, ecs_cluster_arn: str, task_definition_arn: str) -> Dict[str, Any]:
        """ECS 작업을 타겟으로 추가"""
        try:
            response = self.client.put_targets(
                Rule=self.rule_name,
                Targets=[{
                    'Id': '1',
                    'Arn': ecs_cluster_arn,
                    'EcsParameters': {
                        'TaskDefinitionArn': task_definition_arn,
                        'LaunchType': 'FARGATE'
                    }
                }]
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class CloudWatchService(AWSBaseService):
    """CloudWatch 모니터링 서비스"""
    
    def __init__(self):
        super().__init__()
        self.client = self.get_client('cloudwatch')
        self.namespace = 'LocalBriefing/Crawler'
    
    def put_metric(self, metric_name: str, value: float, unit: str = 'Count', 
                   dimensions: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """커스텀 메트릭 전송"""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
            
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            response = self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_alarm(self, alarm_name: str, metric_name: str, threshold: float) -> Dict[str, Any]:
        """CloudWatch 알람 생성"""
        try:
            response = self.client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName=metric_name,
                Namespace=self.namespace,
                Period=300,
                Statistic='Sum',
                Threshold=threshold,
                ActionsEnabled=True,
                AlarmDescription=f'LocalBriefing {alarm_name} 알람'
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class S3Service(AWSBaseService):
    """S3 아카이브 서비스"""
    
    def __init__(self):
        super().__init__()
        self.client = self.get_client('s3')
        self.bucket_name = 'localbriefing-archive'
    
    def create_bucket(self) -> Dict[str, Any]:
        """S3 버킷 생성"""
        try:
            response = self.client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_archive(self, key: str, data: str) -> Dict[str, Any]:
        """데이터 아카이브 업로드"""
        try:
            response = self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType='application/json'
            )
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class AWSManager:
    """AWS 서비스 통합 관리자"""
    
    def __init__(self):
        self.rds = RDSService()
        self.ecs = ECSService()
        self.eventbridge = EventBridgeService()
        self.cloudwatch = CloudWatchService()
        self.s3 = S3Service()
    
    def setup_infrastructure(self, db_password: str) -> Dict[str, Any]:
        """전체 인프라 설정"""
        results = {}
        
        # 1. RDS 생성
        print("RDS 인스턴스 생성 중...")
        rds_result = self.rds.create_instance(db_password)
        results['rds'] = rds_result
        
        # 2. ECS 클러스터 생성
        print("ECS 클러스터 생성 중...")
        ecs_result = self.ecs.create_cluster()
        results['ecs'] = ecs_result
        
        # 3. S3 버킷 생성
        print("S3 버킷 생성 중...")
        s3_result = self.s3.create_bucket()
        results['s3'] = s3_result
        
        # 4. EventBridge 스케줄 생성
        print("EventBridge 스케줄 생성 중...")
        schedule_result = self.eventbridge.create_schedule()
        results['schedule'] = schedule_result
        
        return results
    
    def get_infrastructure_status(self) -> Dict[str, Any]:
        """인프라 상태 조회"""
        return {
            'rds': self.rds.get_status(),
            'timestamp': str(boto3.Session().region_name)
        }
    
    def send_crawl_metrics(self, district: str, count: int, duration: float):
        """크롤링 메트릭 전송"""
        self.cloudwatch.put_metric('IssuesCollected', count, 'Count', 
                                 [{'Name': 'District', 'Value': district}])
        self.cloudwatch.put_metric('CrawlDuration', duration, 'Seconds',
                                 [{'Name': 'District', 'Value': district}])