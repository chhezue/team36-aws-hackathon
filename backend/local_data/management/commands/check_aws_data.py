from django.core.management.base import BaseCommand
from django.db import connection
from local_data.models import Location, LocalIssue, SentimentAnalysis
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'AWS 데이터베이스 데이터 확인'
    
    def handle(self, *args, **options):
        self.stdout.write("=== AWS 데이터베이스 상태 확인 ===")
        
        # 1. 연결 테스트
        self.test_connection()
        
        # 2. 테이블 존재 확인
        self.check_tables()
        
        # 3. 데이터 개수 확인
        self.check_data_counts()
        
        # 4. 최근 크롤링 데이터 확인
        self.check_recent_crawl_data()
    
    def test_connection(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                result = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f"✓ DB 연결 성공: {result[0][:50]}..."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ DB 연결 실패: {str(e)}"))
    
    def check_tables(self):
        with connection.cursor() as cursor:
            # 모든 테이블 조회
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            all_tables = cursor.fetchall()
            
            # Django 앱 테이블만 필터링
            app_tables = [t for t in all_tables if any(prefix in t[0] for prefix in ['local_data_', 'django_'])]
            
            self.stdout.write(f"\n전체 테이블 목록 ({len(all_tables)}개):")
            for table in all_tables:
                self.stdout.write(f"  - {table[0]}")
                
            self.stdout.write(f"\nDjango 앱 테이블 ({len(app_tables)}개):")
            for table in app_tables:
                self.stdout.write(f"  - {table[0]}")
    
    def check_data_counts(self):
        self.stdout.write("\n=== 데이터 개수 확인 ===")
        
        # Location 개수
        location_count = Location.objects.count()
        self.stdout.write(f"Location: {location_count}개")
        
        # 실제 테이블명 확인
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM locations")
            actual_location_count = cursor.fetchone()[0]
            self.stdout.write(f"실제 locations 테이블: {actual_location_count}개")
            
            cursor.execute("SELECT COUNT(*) FROM local_issues")
            actual_issue_count = cursor.fetchone()[0]
            self.stdout.write(f"실제 local_issues 테이블: {actual_issue_count}개")
            
            cursor.execute("SELECT COUNT(*) FROM sentiment_analysis")
            actual_sentiment_count = cursor.fetchone()[0]
            self.stdout.write(f"실제 sentiment_analysis 테이블: {actual_sentiment_count}개")
        
        # LocalIssue 개수
        issue_count = LocalIssue.objects.count()
        self.stdout.write(f"LocalIssue: {issue_count}개")
        
        # SentimentAnalysis 개수
        sentiment_count = SentimentAnalysis.objects.count()
        self.stdout.write(f"SentimentAnalysis: {sentiment_count}개")
        
        if location_count == 0:
            self.stdout.write(self.style.WARNING("⚠ Location 데이터가 없습니다. 초기 데이터를 로드하세요."))
        
        if issue_count == 0:
            self.stdout.write(self.style.WARNING("⚠ LocalIssue 데이터가 없습니다. 크롤링을 실행하세요."))
    
    def check_recent_crawl_data(self):
        self.stdout.write("\n=== 최근 크롤링 데이터 확인 ===")
        
        # 오늘 크롤링된 데이터
        today = datetime.now().date()
        today_issues = LocalIssue.objects.filter(collected_at__date=today)
        self.stdout.write(f"오늘 크롤링된 이슈: {today_issues.count()}개")
        
        # 최근 7일 데이터
        week_ago = datetime.now() - timedelta(days=7)
        recent_issues = LocalIssue.objects.filter(collected_at__gte=week_ago)
        self.stdout.write(f"최근 7일 이슈: {recent_issues.count()}개")
        
        # 구별 데이터 분포
        self.stdout.write("\n구별 이슈 개수:")
        for location in Location.objects.all():
            count = LocalIssue.objects.filter(location=location).count()
            if count > 0:
                self.stdout.write(f"  {location.gu}: {count}개")
        
        # 최근 이슈 샘플 (5개)
        recent_samples = LocalIssue.objects.order_by('-collected_at')[:5]
        if recent_samples:
            self.stdout.write("\n최근 이슈 샘플:")
            for issue in recent_samples:
                self.stdout.write(f"  - [{issue.location.gu}] {issue.title[:50]}... ({issue.source})")
        else:
            self.stdout.write(self.style.ERROR("✗ 크롤링된 데이터가 없습니다!"))