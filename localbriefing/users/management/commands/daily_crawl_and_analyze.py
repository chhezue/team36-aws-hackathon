from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import Location, LocalIssue, SentimentAnalysis, SentimentSummary
from users.crawlers import LocalIssueCrawler
from users.sentiment_analyzer import SimpleSentimentAnalyzer, update_sentiment_summary

class Command(BaseCommand):
    help = '매일 자정 실행: 7일 이내 데이터 크롤링 및 감성 분석'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=20, help='지역별 수집할 데이터 개수')
    
    def handle(self, *args, **options):
        limit = options['limit']
        
        # 7일 이전 데이터 삭제
        week_ago = timezone.now() - timedelta(days=7)
        deleted_count = LocalIssue.objects.filter(collected_at__lt=week_ago).delete()[0]
        self.stdout.write(f"7일 이전 데이터 {deleted_count}개 삭제")
        
        crawler = LocalIssueCrawler()
        analyzer = SimpleSentimentAnalyzer()
        
        locations = Location.objects.all()
        total_collected = 0
        
        for location in locations:
            self.stdout.write(f"\n=== {location.gu} 크롤링 시작 ===")
            
            # 크롤링 실행 (500개 목표)
            results = crawler.crawl_all(location.gu, 500)
            
            collected_count = 0
            for result in results:
                # 중복 체크 (URL 기준)
                if not LocalIssue.objects.filter(url=result['url']).exists():
                    issue = LocalIssue.objects.create(
                        location=location,
                        source=result['source'],
                        title=result['title'],
                        url=result['url'],
                        view_count=result['view_count'],
                        published_at=result['published_at']
                    )
                    
                    # 즉시 감성 분석
                    sentiment_result = analyzer.analyze_text(result['title'])
                    
                    SentimentAnalysis.objects.get_or_create(
                        content_type='local_issue',
                        content_id=issue.id,
                        defaults={
                            'location': location,
                            'sentiment': sentiment_result['sentiment'],
                            'confidence': sentiment_result['confidence'],
                            'keywords': sentiment_result['keywords']
                        }
                    )
                    
                    collected_count += 1
            
            self.stdout.write(f"{location.gu}: {collected_count}개 수집 완료")
            total_collected += collected_count
            
            # 오늘의 감성 요약 업데이트
            today = timezone.now().date()
            update_sentiment_summary(location, today)
        
        self.stdout.write(
            self.style.SUCCESS(f"\n총 {total_collected}개 데이터 수집 및 분석 완료")
        )