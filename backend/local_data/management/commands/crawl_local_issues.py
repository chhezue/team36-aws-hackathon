from django.core.management.base import BaseCommand
from local_data.models import Location, LocalIssue
from local_data.optimized_crawler import AsyncCrawlerWrapper as LocalIssueCrawler
from datetime import datetime

class Command(BaseCommand):
    help = '동네 이슈 크롤링'

    def add_arguments(self, parser):
        parser.add_argument('--district', type=str, help='특정 구만 크롤링')

    def handle(self, *args, **options):
        crawler = LocalIssueCrawler(max_concurrent=5)
        
        if options['district']:
            locations = Location.objects.filter(gu=options['district'])
        else:
            locations = Location.objects.all()
        
        for location in locations:
            self.stdout.write(f"{location.gu} 크롤링 시작...")
            
            # 7일 이상 된 데이터 삭제
            from datetime import timedelta
            from django.utils import timezone
            seven_days_ago = timezone.now() - timedelta(days=7)
            LocalIssue.objects.filter(location=location, collected_at__lt=seven_days_ago).delete()
            
            # 크롤링 실행
            results = crawler.crawl_single_district(location.gu, 50)
            
            # 데이터베이스에 저장
            from django.utils import timezone
            for result in results:
                LocalIssue.objects.create(
                    location=location,
                    source=result['source'],
                    title=result['title'],
                    url=result['url'],
                    view_count=result['view_count'],
                    published_at=result.get('published_at') or timezone.now()
                )
            
            self.stdout.write(
                self.style.SUCCESS(f"{location.gu}: {len(results)}개 이슈 수집 완료")
            )