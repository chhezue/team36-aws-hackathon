from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'AWS RDS 데이터베이스 초기 설정'
    
    def add_arguments(self, parser):
        parser.add_argument('--migrate', action='store_true', help='마이그레이션 실행')
        parser.add_argument('--test', action='store_true', help='연결 테스트만 실행')
        parser.add_argument('--load-data', action='store_true', help='초기 데이터 로드')
    
    def handle(self, *args, **options):
        self.stdout.write("=== AWS RDS 데이터베이스 설정 ===")
        
        # 연결 테스트
        if self.test_connection():
            self.stdout.write(self.style.SUCCESS("✓ 데이터베이스 연결 성공"))
        else:
            self.stdout.write(self.style.ERROR("✗ 데이터베이스 연결 실패"))
            return
        
        if options['test']:
            return
            
        # 마이그레이션 실행
        if options['migrate']:
            self.stdout.write("마이그레이션 실행 중...")
            try:
                call_command('makemigrations')
                call_command('migrate')
                self.stdout.write(self.style.SUCCESS("✓ 마이그레이션 완료"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 마이그레이션 실패: {str(e)}"))
                return
        
        # 초기 데이터 로드
        if options['load_data']:
            self.stdout.write("초기 데이터 로드 중...")
            self.load_initial_locations()
            self.stdout.write(self.style.SUCCESS("✓ 초기 데이터 로드 완료"))
    
    def test_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                result = cursor.fetchone()
                self.stdout.write(f"PostgreSQL 버전: {result[0]}")
                return True
        except Exception as e:
            self.stdout.write(f"연결 오류: {str(e)}")
            return False
    
    def load_initial_locations(self):
        """서울시 구 데이터 로드"""
        from local_data.models import Location
        
        seoul_districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
            '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        created_count = 0
        for district in seoul_districts:
            location, created = Location.objects.get_or_create(gu=district)
            if created:
                created_count += 1
                self.stdout.write(f"  - {district} 생성")
        
        self.stdout.write(f"총 {created_count}개 지역 생성됨")