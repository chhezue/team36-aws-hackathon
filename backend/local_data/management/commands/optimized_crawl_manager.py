from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from local_data.models import Location, LocalIssue, SentimentAnalysis
from local_data.optimized_crawler import AsyncCrawlerWrapper
from local_data.sentiment_analyzer import SimpleSentimentAnalyzer
from aws_services import AWSManager
import time
import asyncio
from typing import List, Dict

class Command(BaseCommand):
    help = '최적화된 비동기 크롤링 및 분석'
    
    def add_arguments(self, parser):
        parser.add_argument('--district', type=str, help='특정 구만 크롤링')
        parser.add_argument('--limit', type=int, default=50, help='구별 수집 개수')
        parser.add_argument('--concurrent', type=int, default=15, help='동시 처리 개수')
        parser.add_argument('--cleanup', action='store_true', help='7일 이전 데이터 삭제')
        parser.add_argument('--benchmark', action='store_true', help='성능 벤치마크 실행')
    
    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['benchmark']:
            self.run_benchmark(options)
            return
        
        aws_manager = AWSManager()
        self.stdout.write("=== 최적화된 크롤링 시작 ===")
        
        # 7일 이전 데이터 정리
        if options['cleanup']:
            self.cleanup_old_data()
        
        # 크롤링 실행
        if options['district']:
            total_collected = self.crawl_single_district_optimized(
                options['district'], options['limit'], options['concurrent']
            )
        else:
            total_collected = self.crawl_all_districts_optimized(
                options['limit'], options['concurrent']
            )
        
        duration = time.time() - start_time
        
        # AWS 메트릭 전송
        aws_manager.cloudwatch.put_metric('OptimizedTotalIssuesCollected', total_collected)
        aws_manager.cloudwatch.put_metric('OptimizedCrawlDuration', duration, 'Seconds')
        
        self.stdout.write(
            self.style.SUCCESS(
                f"최적화된 크롤링 완료: {total_collected}개 수집, {duration:.1f}초 소요"
            )
        )
    
    def crawl_single_district_optimized(self, district: str, limit: int, concurrent: int) -> int:
        """최적화된 단일 구 크롤링"""
        try:
            location = Location.objects.get(gu=district)
        except Location.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"지역 '{district}' 없음"))
            return 0
        
        crawler = AsyncCrawlerWrapper(max_concurrent=concurrent)
        results = crawler.crawl_single_district(district, limit)
        
        return self.save_crawl_results({district: results})
    
    def crawl_all_districts_optimized(self, limit: int, concurrent: int) -> int:
        """최적화된 전체 구 크롤링"""
        # 모든 구 목록 가져오기
        districts = list(Location.objects.values_list('gu', flat=True))
        
        self.stdout.write(f"총 {len(districts)}개 구 병렬 크롤링 시작 (동시 처리: {concurrent})")
        
        # 비동기 크롤링 실행
        crawler = AsyncCrawlerWrapper(max_concurrent=concurrent)
        all_results = crawler.crawl_all_districts(districts, limit)
        
        # 결과 저장
        return self.save_crawl_results(all_results)
    
    def save_crawl_results(self, district_results: Dict[str, List[Dict]]) -> int:
        """크롤링 결과를 데이터베이스에 배치 저장"""
        analyzer = SimpleSentimentAnalyzer()
        total_saved = 0
        
        # 구별로 처리
        for district_name, results in district_results.items():
            try:
                location = Location.objects.get(gu=district_name)
            except Location.DoesNotExist:
                continue
            
            if not results:
                continue
            
            # 배치 처리를 위한 리스트
            issues_to_create = []
            analyses_to_create = []
            
            # 중복 URL 체크를 위한 기존 URL 세트
            existing_urls = set(
                LocalIssue.objects.filter(
                    location=location,
                    collected_at__date=timezone.now().date()
                ).values_list('url', flat=True)
            )
            
            for result in results:
                # 중복 체크
                if result['url'] in existing_urls:
                    continue
                
                # LocalIssue 객체 준비
                issue = LocalIssue(
                    location=location,
                    source=result['source'],
                    title=result['title'],
                    url=result['url'],
                    view_count=result['view_count'],
                    published_at=result['published_at'],
                    collected_at=timezone.now()
                )
                issues_to_create.append(issue)
                existing_urls.add(result['url'])  # 중복 방지
            
            # 배치 INSERT (ignore_conflicts=True로 중복 처리)
            if issues_to_create:
                created_issues = LocalIssue.objects.bulk_create(
                    issues_to_create, 
                    batch_size=200, 
                    ignore_conflicts=True
                )
                
                # 실제 생성된 이슈들에 대해 감성 분석 준비
                for issue in created_issues:
                    if issue.id:  # 실제로 생성된 경우만
                        sentiment_result = analyzer.analyze_text(issue.title)
                        
                        analysis = SentimentAnalysis(
                            location=location,
                            content_type='local_issue',
                            content_id=issue.id,
                            sentiment=sentiment_result['sentiment'],
                            confidence=sentiment_result['confidence'],
                            keywords=sentiment_result.get('keywords', [])
                        )
                        analyses_to_create.append(analysis)
                
                # 감성 분석 배치 INSERT
                if analyses_to_create:
                    SentimentAnalysis.objects.bulk_create(
                        analyses_to_create, 
                        batch_size=200, 
                        ignore_conflicts=True
                    )
                
                saved_count = len([issue for issue in created_issues if issue.id])
                total_saved += saved_count
                
                self.stdout.write(f"  {district_name}: {saved_count}개 저장")
        
        return total_saved
    
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
    
    def run_benchmark(self, options):
        """성능 벤치마크 실행"""
        self.stdout.write("=== 성능 벤치마크 시작 ===")
        
        # 테스트용 구 목록 (5개)
        test_districts = ['강남구', '강동구', '강북구', '강서구', '관악구']
        limit = 20
        
        # 기존 방식 (순차 처리) 시뮬레이션
        self.stdout.write("1. 순차 처리 방식 테스트...")
        start_time = time.time()
        
        from local_data.optimized_crawler import AsyncCrawlerWrapper
        old_crawler = AsyncCrawlerWrapper(max_concurrent=1)  # 순차 처리 시뮬레이션
        old_results = {}
        
        for district in test_districts:
            district_results = old_crawler.crawl_single_district(district, limit)
            old_results[district] = district_results
        
        old_duration = time.time() - start_time
        old_total = sum(len(results) for results in old_results.values())
        
        # 새로운 방식 (비동기 병렬 처리)
        self.stdout.write("2. 비동기 병렬 처리 방식 테스트...")
        start_time = time.time()
        
        crawler = AsyncCrawlerWrapper(max_concurrent=options['concurrent'])
        new_results = crawler.crawl_all_districts(test_districts, limit)
        
        new_duration = time.time() - start_time
        new_total = sum(len(results) for results in new_results.values())
        
        # 결과 비교
        self.stdout.write("\n=== 벤치마크 결과 ===")
        self.stdout.write(f"순차 처리:")
        self.stdout.write(f"  - 소요 시간: {old_duration:.2f}초")
        self.stdout.write(f"  - 수집 개수: {old_total}개")
        self.stdout.write(f"  - 구별 평균: {old_duration/len(test_districts):.2f}초")
        
        self.stdout.write(f"\n비동기 병렬 처리:")
        self.stdout.write(f"  - 소요 시간: {new_duration:.2f}초")
        self.stdout.write(f"  - 수집 개수: {new_total}개")
        self.stdout.write(f"  - 구별 평균: {new_duration/len(test_districts):.2f}초")
        
        if old_duration > 0:
            improvement = ((old_duration - new_duration) / old_duration) * 100
            speedup = old_duration / new_duration if new_duration > 0 else float('inf')
            
            self.stdout.write(f"\n성능 개선:")
            self.stdout.write(f"  - 속도 향상: {improvement:.1f}%")
            self.stdout.write(f"  - 배속 개선: {speedup:.1f}x")
        
        # 구별 상세 결과
        self.stdout.write(f"\n구별 수집 결과:")
        for district in test_districts:
            old_count = len(old_results.get(district, []))
            new_count = len(new_results.get(district, []))
            self.stdout.write(f"  {district}: {old_count} → {new_count}")