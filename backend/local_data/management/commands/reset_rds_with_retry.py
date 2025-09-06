from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.utils import OperationalError
from local_data.models import Location, LocalIssue, RestaurantInfo, SentimentAnalysis, SentimentSummary
from local_data.simple_crawler import LocalIssueCrawler
from local_data.sentiment_analyzer import SimpleSentimentAnalyzer
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'AWS RDS 연결 재시도를 포함한 데이터 초기화 및 크롤링'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='데이터 삭제 확인')
        parser.add_argument('--limit', type=int, default=20, help='구별 수집 개수')
        parser.add_argument('--retry', type=int, default=3, help='연결 재시도 횟수')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  이 명령어는 AWS RDS의 모든 데이터를 삭제합니다.\n'
                    '계속하려면 --confirm 옵션을 추가하세요.'
                )
            )
            return

        self.stdout.write('=== AWS RDS 연결 재시도 포함 초기화 시작 ===')
        
        # 1. 데이터베이스 연결 테스트 및 초기화
        if self.test_and_clear_database(options['retry']):
            # 2. 기본 데이터 생성
            self.setup_locations()
            
            # 3. 크롤링 실행
            self.crawl_with_retry(options['limit'], options['retry'])
            
            self.stdout.write(
                self.style.SUCCESS('=== 모든 작업 완료 ===')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ 데이터베이스 연결 실패')
            )

    def test_and_clear_database(self, max_retries):
        """데이터베이스 연결 테스트 및 데이터 삭제"""
        for attempt in range(max_retries):
            try:
                self.stdout.write(f'🔄 데이터베이스 연결 시도 {attempt + 1}/{max_retries}')
                
                # 연결 테스트
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                self.stdout.write('✅ 데이터베이스 연결 성공')
                
                # 데이터 삭제
                self.stdout.write('🗑️  데이터 삭제 중...')
                with transaction.atomic():
                    deleted_sentiment = SentimentAnalysis.objects.all().delete()[0]
                    deleted_summary = SentimentSummary.objects.all().delete()[0]
                    deleted_issues = LocalIssue.objects.all().delete()[0]
                    deleted_restaurants = RestaurantInfo.objects.all().delete()[0]
                    deleted_locations = Location.objects.all().delete()[0]
                    
                    self.stdout.write(
                        f'삭제 완료: 감성분석 {deleted_sentiment}개, '
                        f'요약 {deleted_summary}개, 이슈 {deleted_issues}개, '
                        f'음식점 {deleted_restaurants}개, 지역 {deleted_locations}개'
                    )
                
                return True
                
            except OperationalError as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  연결 실패 (시도 {attempt + 1}): {str(e)[:100]}...')
                )
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    self.stdout.write(f'⏳ {wait_time}초 대기 후 재시도...')
                    time.sleep(wait_time)
                    
                    # 연결 재설정
                    connection.close()
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ 예상치 못한 오류: {str(e)}')
                )
                return False
        
        return False

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
        
        try:
            Location.objects.bulk_create(locations_to_create)
            self.stdout.write(
                self.style.SUCCESS(f'✅ {len(districts)}개 구 데이터 생성 완료')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 지역 데이터 생성 실패: {str(e)}')
            )

    def crawl_with_retry(self, limit, max_retries):
        """재시도 로직을 포함한 크롤링"""
        self.stdout.write(f'🕷️  크롤링 시작 (구별 {limit}개)')
        
        crawler = LocalIssueCrawler()
        locations = Location.objects.all()
        total_collected = 0
        
        for location in locations:
            self.stdout.write(f'처리 중: {location.gu}')
            
            for attempt in range(max_retries):
                try:
                    # 크롤링 실행
                    results = []
                    
                    # 네이버 뉴스 크롤링
                    news_results = crawler.crawl_naver_news_fast(f"{location.gu} 뉴스", 8)
                    results.extend(news_results)
                    
                    # 추가 쿼리로 더 많은 데이터 수집
                    additional_queries = [
                        f"{location.gu} 소식",
                        f"{location.gu} 이슈", 
                        f"{location.gu} 생활정보"
                    ]
                    
                    for query in additional_queries:
                        if len(results) >= limit:
                            break
                        news_data = crawler.crawl_naver_news_fast(query, 4)
                        results.extend(news_data)
                    
                    # 중복 제거
                    seen_urls = set()
                    unique_results = []
                    for result in results:
                        if result['url'] not in seen_urls and result['url']:
                            seen_urls.add(result['url'])
                            unique_results.append(result)
                    
                    results = unique_results[:limit]
                    
                    # 데이터베이스 저장
                    if results:
                        issues_to_create = []
                        for result in results:
                            issues_to_create.append(LocalIssue(
                                location=location,
                                source=result['source'],
                                title=result['title'][:500],  # 제목 길이 제한
                                url=result['url'][:200],  # URL 길이 제한
                                view_count=result['view_count'],
                                published_at=result.get('published_at') or timezone.now(),
                                collected_at=timezone.now()
                            ))
                        
                        # 배치 저장
                        LocalIssue.objects.bulk_create(
                            issues_to_create, 
                            batch_size=50, 
                            ignore_conflicts=True
                        )
                        
                        saved_count = len(issues_to_create)
                        total_collected += saved_count
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ {location.gu}: {saved_count}개 저장')
                        )
                    else:
                        self.stdout.write(f'  ⚠️  {location.gu}: 데이터 없음')
                    
                    break  # 성공하면 재시도 루프 종료
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  {location.gu} 시도 {attempt + 1} 실패: {str(e)[:50]}...')
                    )
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ {location.gu} 최종 실패')
                        )
            
            # 서버 부하 방지
            time.sleep(1)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 전체 크롤링 완료: 총 {total_collected}개 수집')
        )
        
        # 음식점 데이터 크롤링
        self.crawl_restaurants()

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