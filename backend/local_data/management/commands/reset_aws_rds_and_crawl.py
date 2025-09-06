from django.core.management.base import BaseCommand
from django.db import transaction
from local_data.models import Location, LocalIssue, RestaurantInfo, SentimentAnalysis, SentimentSummary
from local_data.optimized_crawler import AsyncCrawlerWrapper as LocalIssueCrawler
from local_data.sentiment_analyzer import SimpleSentimentAnalyzer
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'AWS RDS 전체 데이터 삭제 후 모든 구 크롤링 재실행'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='데이터 삭제 확인')
        parser.add_argument('--limit', type=int, default=30, help='구별 수집 개수')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  이 명령어는 AWS RDS의 모든 데이터를 삭제합니다.\n'
                    '계속하려면 --confirm 옵션을 추가하세요.'
                )
            )
            return

        self.stdout.write('=== AWS RDS 전체 초기화 및 재크롤링 시작 ===')
        
        # 1. 데이터베이스 완전 초기화
        self.clear_all_data()
        
        # 2. 서울시 25개 구 기본 데이터 생성
        self.setup_locations()
        
        # 3. 전체 구 크롤링 실행
        self.crawl_all_districts(options['limit'])
        
        # 4. 음식점 데이터 크롤링
        self.crawl_restaurants()
        
        # 5. 감성 분석 실행
        self.analyze_sentiments()
        
        self.stdout.write(
            self.style.SUCCESS('=== AWS RDS 초기화 및 크롤링 완료 ===')
        )

    def clear_all_data(self):
        """모든 테이블 데이터 삭제"""
        self.stdout.write('🗑️  모든 데이터 삭제 중...')
        
        with transaction.atomic():
            # 외래키 제약조건 순서에 따라 삭제
            deleted_sentiment = SentimentAnalysis.objects.all().delete()[0]
            deleted_summary = SentimentSummary.objects.all().delete()[0]
            deleted_issues = LocalIssue.objects.all().delete()[0]
            deleted_restaurants = RestaurantInfo.objects.all().delete()[0]
            deleted_locations = Location.objects.all().delete()[0]
            
            self.stdout.write(
                f'삭제된 데이터: 감성분석 {deleted_sentiment}개, '
                f'요약 {deleted_summary}개, 이슈 {deleted_issues}개, '
                f'음식점 {deleted_restaurants}개, 지역 {deleted_locations}개'
            )
        
        self.stdout.write(self.style.SUCCESS('✅ 모든 데이터 삭제 완료'))

    def setup_locations(self):
        """서울시 25개 구 기본 데이터 생성"""
        self.stdout.write('📍 지역 데이터 생성 중...')
        
        districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        locations_to_create = []
        for district in districts:
            locations_to_create.append(Location(gu=district))
        
        Location.objects.bulk_create(locations_to_create)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(districts)}개 구 데이터 생성 완료')
        )

    def crawl_all_districts(self, limit):
        """전체 구 크롤링 실행"""
        self.stdout.write(f'🕷️  전체 구 크롤링 시작 (구별 {limit}개)')
        
        crawler = LocalIssueCrawler(max_concurrent=5)
        locations = Location.objects.all()
        total_collected = 0
        
        for location in locations:
            self.stdout.write(f'처리 중: {location.gu}')
            
            try:
                # 크롤링 실행 (더 많은 쿼리로 시도)
                results = []
                
                # 크롤링 실행
                results = crawler.crawl_single_district(location.gu, limit)
                
                # 중복 제거
                seen_urls = set()
                unique_results = []
                for result in results:
                    if result['url'] not in seen_urls:
                        seen_urls.add(result['url'])
                        unique_results.append(result)
                
                results = unique_results[:limit]
                
                # 배치 저장
                issues_to_create = []
                for result in results:
                    # 중복 체크
                    if LocalIssue.objects.filter(url=result['url']).exists():
                        continue
                    
                    issues_to_create.append(LocalIssue(
                        location=location,
                        source=result['source'],
                        title=result['title'],
                        url=result['url'],
                        view_count=result['view_count'],
                        published_at=result.get('published_at') or timezone.now(),
                        collected_at=timezone.now()
                    ))
                
                # 배치 INSERT
                if issues_to_create:
                    LocalIssue.objects.bulk_create(
                        issues_to_create, 
                        batch_size=100, 
                        ignore_conflicts=True
                    )
                    saved_count = len(issues_to_create)
                    total_collected += saved_count
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ {location.gu}: {saved_count}개 저장')
                    )
                else:
                    self.stdout.write(f'  ⚠️  {location.gu}: 새로운 데이터 없음')
                
                # 서버 부하 방지
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ {location.gu} 크롤링 실패: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 전체 크롤링 완료: 총 {total_collected}개 수집')
        )

    def crawl_restaurants(self):
        """음식점 데이터 크롤링"""
        self.stdout.write('🍽️  음식점 데이터 크롤링 시작...')
        
        try:
            from django.core.management import call_command
            call_command('crawl_all_restaurants')
            self.stdout.write(self.style.SUCCESS('✅ 음식점 데이터 크롤링 완료'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 음식점 크롤링 실패: {str(e)}')
            )

    def analyze_sentiments(self):
        """수집된 데이터 감성 분석"""
        self.stdout.write('🧠 감성 분석 시작...')
        
        # 감성 분석이 없는 이슈들 조회
        analyzed_ids = SentimentAnalysis.objects.filter(
            content_type='local_issue'
        ).values_list('content_id', flat=True)
        
        issues = LocalIssue.objects.exclude(
            id__in=analyzed_ids
        )[:1000]  # 최대 1000개
        
        if not issues.exists():
            self.stdout.write('분석할 새로운 이슈가 없습니다.')
            return
        
        analyzer = SimpleSentimentAnalyzer()
        analyses_to_create = []
        
        for issue in issues:
            try:
                result = analyzer.analyze_text(issue.title)
                
                analyses_to_create.append(SentimentAnalysis(
                    location=issue.location,
                    content_type='local_issue',
                    content_id=issue.id,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    keywords=result.get('keywords', [])
                ))
                
                # 배치 크기 제한
                if len(analyses_to_create) >= 100:
                    SentimentAnalysis.objects.bulk_create(
                        analyses_to_create, 
                        ignore_conflicts=True
                    )
                    analyses_to_create = []
                    
            except Exception as e:
                continue
        
        # 남은 데이터 저장
        if analyses_to_create:
            SentimentAnalysis.objects.bulk_create(
                analyses_to_create, 
                ignore_conflicts=True
            )
        
        analyzed_count = SentimentAnalysis.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'✅ 감성 분석 완료: {analyzed_count}개 분석')
        )