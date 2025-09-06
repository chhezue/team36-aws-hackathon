from django.core.management.base import BaseCommand
from local_data.models import Location, LocalIssue, RestaurantInfo, SentimentAnalysis, SentimentSummary
from local_data.crawlers import LocalIssueCrawler
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'AWS DB 초기화 후 모든 구 크롤링 재실행'

    def handle(self, *args, **options):
        self.stdout.write('=== AWS DB 초기화 시작 ===')
        
        # 1. 모든 데이터 삭제
        LocalIssue.objects.all().delete()
        RestaurantInfo.objects.all().delete()
        SentimentAnalysis.objects.all().delete()
        SentimentSummary.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('DB 초기화 완료'))
        
        # 2. 서울시 25개 구 목록
        districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        # 3. Location 테이블에 구 정보 생성
        for district in districts:
            location, created = Location.objects.get_or_create(gu=district)
            if created:
                self.stdout.write(f'{district} 생성')
        
        # 4. 각 구별 크롤링 실행
        crawler = LocalIssueCrawler()
        
        for district in districts:
            self.stdout.write(f'\n=== {district} 크롤링 시작 ===')
            
            try:
                location = Location.objects.get(gu=district)
                
                # 크롤링 실행 (각 구당 50개)
                results = crawler.crawl_all(district, target_count=50)
                
                # DB 저장
                saved_count = 0
                for result in results:
                    try:
                        LocalIssue.objects.create(
                            location=location,
                            source=result['source'],
                            title=result['title'],
                            url=result['url'],
                            view_count=result['view_count'],
                            published_at=result.get('published_at') or timezone.now(),
                            collected_at=timezone.now()
                        )
                        saved_count += 1
                    except Exception as e:
                        continue
                
                self.stdout.write(
                    self.style.SUCCESS(f'{district}: {saved_count}개 저장 완료')
                )
                
                # 과부하 방지를 위한 대기
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'{district} 크롤링 실패: {str(e)}')
                )
        
        self.stdout.write('\n=== 전체 크롤링 완료 ===')
        
        # 5. 음식점 데이터 크롤링
        self.stdout.write('\n=== 음식점 데이터 크롤링 시작 ===')
        from django.core.management import call_command
        try:
            call_command('crawl_all_restaurants')
            self.stdout.write(self.style.SUCCESS('음식점 데이터 크롤링 완료'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'음식점 크롤링 실패: {str(e)}'))