from django.core.management.base import BaseCommand
from local_data.scheduler import crawler_scheduler
import signal
import sys

class Command(BaseCommand):
    help = '크롤링 스케줄러 시작'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='테스트 모드 (10분마다 실행)'
        )
    
    def handle(self, *args, **options):
        def signal_handler(sig, frame):
            self.stdout.write('\n스케줄러 종료 중...')
            crawler_scheduler.stop_scheduler()
            sys.exit(0)
        
        # Ctrl+C 처리
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # 스케줄러 시작
            crawler_scheduler.start_scheduler()
            
            next_run = crawler_scheduler.get_next_run_time()
            if next_run:
                self.stdout.write(
                    self.style.SUCCESS(f'스케줄러 시작됨 - 다음 실행: {next_run}')
                )
            
            # 메인 스레드 유지
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stdout.write('\n스케줄러 종료')
            crawler_scheduler.stop_scheduler()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'스케줄러 오류: {str(e)}')
            )
            crawler_scheduler.stop_scheduler()