from django.core.management.base import BaseCommand
from local_data.scheduler import crawler_scheduler
import time

class Command(BaseCommand):
    help = '스케줄러 테스트 (1분마다 실행)'
    
    def handle(self, *args, **options):
        import schedule
        
        def test_job():
            self.stdout.write("테스트 크롤링 실행 중...")
            from django.core.management import call_command
            call_command('daily_crawl_and_analyze', limit=5)
        
        # 1분마다 실행 (테스트용)
        schedule.every(1).minutes.do(test_job)
        
        self.stdout.write("테스트 스케줄러 시작 - 1분마다 실행")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(10)
        except KeyboardInterrupt:
            self.stdout.write("\n테스트 스케줄러 종료")
            schedule.clear()