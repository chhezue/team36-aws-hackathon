from django.core.management.base import BaseCommand
from local_data.models import Location, LocalIssue, SentimentAnalysis, SentimentSummary

class Command(BaseCommand):
    help = '데이터베이스 현황 조회'
    
    def add_arguments(self, parser):
        parser.add_argument('--district', type=str, help='특정 구 데이터만 조회')
        parser.add_argument('--table', type=str, choices=['locations', 'issues', 'sentiment', 'all'], 
                          default='all', help='조회할 테이블')
    
    def handle(self, *args, **options):
        district = options.get('district')
        table = options['table']
        
        if table in ['locations', 'all']:
            self.show_locations(district)
        
        if table in ['issues', 'all']:
            self.show_local_issues(district)
            
        if table in ['sentiment', 'all']:
            self.show_sentiment_data(district)
    
    def show_locations(self, district=None):
        self.stdout.write("\n=== 지역 데이터 ===")
        locations = Location.objects.all()
        if district:
            locations = locations.filter(gu=district)
            
        for loc in locations:
            issue_count = LocalIssue.objects.filter(location=loc).count()
            self.stdout.write(f"• {loc.gu} (ID: {loc.id}) - 이슈 {issue_count}개")
    
    def show_local_issues(self, district=None):
        self.stdout.write("\n=== 동네 이슈 데이터 ===")
        issues = LocalIssue.objects.select_related('location').order_by('-collected_at')
        if district:
            issues = issues.filter(location__gu=district)
            
        for issue in issues[:10]:  # 최신 10개만
            self.stdout.write(f"• [{issue.location.gu}] {issue.title[:50]}... ({issue.source})")
    
    def show_sentiment_data(self, district=None):
        self.stdout.write("\n=== 감성 분석 데이터 ===")
        analyses = SentimentAnalysis.objects.select_related('location').order_by('-analyzed_at')
        if district:
            analyses = analyses.filter(location__gu=district)
            
        for analysis in analyses[:10]:  # 최신 10개만
            self.stdout.write(f"• [{analysis.location.gu}] {analysis.sentiment} ({analysis.confidence:.2f})")