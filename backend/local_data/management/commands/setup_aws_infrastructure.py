from django.core.management.base import BaseCommand
from aws_services import AWSManager
import os

class Command(BaseCommand):
    help = 'AWS 인프라 전체 설정'
    
    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, required=True, help='RDS 마스터 암호')
        parser.add_argument('--status', action='store_true', help='인프라 상태만 조회')
    
    def handle(self, *args, **options):
        aws_manager = AWSManager()
        
        if options['status']:
            self.show_status(aws_manager)
            return
        
        password = options['password']
        
        self.stdout.write("=== AWS 인프라 설정 시작 ===")
        
        # 전체 인프라 설정
        results = aws_manager.setup_infrastructure(password)
        
        # 결과 출력
        for service, result in results.items():
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {service.upper()} 설정 완료")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ {service.upper()} 설정 실패: {result['error']}")
                )
        
        # RDS 엔드포인트 대기
        if results['rds']['success']:
            self.stdout.write("RDS 인스턴스 생성 중... (5-10분 소요)")
            self.stdout.write("완료 후 다음 명령어로 엔드포인트 확인:")
            self.stdout.write("python manage.py setup_aws_infrastructure --status")
    
    def show_status(self, aws_manager):
        """인프라 상태 조회"""
        self.stdout.write("=== AWS 인프라 상태 ===")
        
        status = aws_manager.get_infrastructure_status()
        rds_status = status['rds']
        
        self.stdout.write(f"RDS 상태: {rds_status['status']}")
        if 'endpoint' in rds_status:
            self.stdout.write(f"RDS 엔드포인트: {rds_status['endpoint']}")
            self.stdout.write(f"포트: {rds_status['port']}")
            
            # .env 파일 업데이트 안내
            if rds_status['status'] == 'available':
                self.stdout.write(self.style.SUCCESS("✓ RDS 사용 가능"))
                self.stdout.write("다음 단계:")
                self.stdout.write(f"1. .env 파일에서 DB_HOST={rds_status['endpoint']} 설정")
                self.stdout.write("2. DB_ENGINE=postgresql 주석 해제")
                self.stdout.write("3. python manage.py setup_aws_db --migrate --load-data 실행")