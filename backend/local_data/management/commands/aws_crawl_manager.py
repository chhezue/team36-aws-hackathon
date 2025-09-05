from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from local_data.models import Location, LocalIssue, SentimentAnalysis
from local_data.crawlers import LocalIssueCrawler
from local_data.sentiment_analyzer import SimpleSentimentAnalyzer
from aws_services import AWSManager
from concurrent.futures import ThreadPoolExecutor
import time

class Command(BaseCommand):
    help = 'AWS 환경에서 최적화된 크롤링 및 분석'
    
    def add_arguments(self, parser):
        parser.add_argument('--district', type=str, help='특정 구만 크롤링')
        parser.add_argument('--limit', type=int, default=20, help='구별 수집 개수')
        parser.add_argument('--parallel', type=int, default=5, help='병렬 처리 개수')
        parser.add_argument('--cleanup', action='store_true', help='7일 이전 데이터 삭제')
    
    def handle(self, *args, **options):
        start_time = time.time()
        aws_manager = AWSManager()
        
        self.stdout.write("=== AWS 크롤링 시작 ===")
        
        # 7일 이전 데이터 정리
        if options['cleanup']:
            self.cleanup_old_data()
        
        # 크롤링 실행
        if options['district']:
            # 단일 구 크롤링
            total_collected = self.crawl_single_district(
                options['district'], options['limit'], aws_manager
            )
        else:
            # 전체 구 병렬 크롤링
            total_collected = self.crawl_all_districts_parallel(
                options['limit'], options['parallel'], aws_manager
            )
        
        duration = time.time() - start_time
        
        # 전체 메트릭 전송
        aws_manager.cloudwatch.put_metric('TotalIssuesCollected', total_collected)
        aws_manager.cloudwatch.put_metric('CrawlTotalDuration', duration, 'Seconds')
        
        self.stdout.write(
            self.style.SUCCESS(
                f"크롤링 완료: {total_collected}개 수집, {duration:.1f}초 소요"
            )
        )
    
    def crawl_single_district(self, district: str, limit: int, aws_manager: AWSManager) -> int:
        """단일 구 크롤링"""
        try:
            location = Location.objects.get(gu=district)
        except Location.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"지역 '{district}' 없음"))
            return 0
        
        start_time = time.time()
        collected_count = self.process_district(location, limit)
        duration = time.time() - start_time
        
        # 메트릭 전송
        aws_manager.send_crawl_metrics(district, collected_count, duration)
        
        return collected_count
    
    def crawl_all_districts_parallel(self, limit: int, max_workers: int, aws_manager: AWSManager) -> int:
        """전체 구 병렬 크롤링"""
        locations = Location.objects.all()
        total_collected = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 병렬 작업 제출
            futures = []
            for location in locations:
                future = executor.submit(self.process_district_with_metrics, 
                                       location, limit, aws_manager)
                futures.append(future)
            
            # 결과 수집
            for future in futures:
                try:
                    collected_count = future.result()
                    total_collected += collected_count
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"크롤링 오류: {str(e)}")
                    )
        
        return total_collected
    
    def process_district_with_metrics(self, location: Location, limit: int, aws_manager: AWSManager) -> int:
        """메트릭 포함 구 처리"""
        start_time = time.time()
        collected_count = self.process_district(location, limit)
        duration = time.time() - start_time
        
        # 개별 구 메트릭 전송
        aws_manager.send_crawl_metrics(location.gu, collected_count, duration)
        
        return collected_count
    
    def process_district(self, location: Location, limit: int) -> int:
        """구별 크롤링 및 감성 분석 처리"""
        self.stdout.write(f"처리 중: {location.gu}")
        
        crawler = LocalIssueCrawler()
        analyzer = SimpleSentimentAnalyzer()
        
        # 크롤링 실행
        results = crawler.crawl_all(location.gu, limit)
        collected_count = 0
        
        # 배치 처리를 위한 리스트
        issues_to_create = []
        analyses_to_create = []
        
        for result in results:
            # 중복 체크
            if LocalIssue.objects.filter(url=result['url']).exists():
                continue
            
            # LocalIssue 객체 준비
            issue_data = {
                'location': location,
                'source': result['source'],
                'title': result['title'],
                'url': result['url'],
                'view_count': result['view_count'],
                'published_at': result['published_at']
            }
            issues_to_create.append(LocalIssue(**issue_data))
            collected_count += 1
        
        # 배치 INSERT
        if issues_to_create:
            created_issues = LocalIssue.objects.bulk_create(
                issues_to_create, batch_size=100, ignore_conflicts=True
            )
            
            # 감성 분석 배치 처리
            for issue in created_issues:
                sentiment_result = analyzer.analyze_text(issue.title)
                
                analysis_data = {
                    'location': location,
                    'content_type': 'local_issue',
                    'content_id': issue.id,
                    'sentiment': sentiment_result['sentiment'],
                    'confidence': sentiment_result['confidence'],
                    'keywords': sentiment_result.get('keywords', [])
                }
                analyses_to_create.append(SentimentAnalysis(**analysis_data))
            
            # 감성 분석 배치 INSERT
            if analyses_to_create:
                SentimentAnalysis.objects.bulk_create(
                    analyses_to_create, batch_size=100, ignore_conflicts=True
                )
        
        self.stdout.write(f"{location.gu}: {collected_count}개 수집")
        return collected_count
    
    def cleanup_old_data(self):
        """7일 이전 데이터 삭제"""
        week_ago = timezone.now() - timedelta(days=7)
        
        # LocalIssue 삭제
        deleted_issues = LocalIssue.objects.filter(
            collected_at__lt=week_ago
        ).delete()[0]
        
        # SentimentAnalysis 삭제
        deleted_analyses = SentimentAnalysis.objects.filter(
            analyzed_at__lt=week_ago
        ).delete()[0]
        
        self.stdout.write(
            f"정리 완료: 이슈 {deleted_issues}개, 분석 {deleted_analyses}개 삭제"
        )