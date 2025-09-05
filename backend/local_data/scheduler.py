import schedule
import time
import threading
from django.core.management import call_command
from django.utils import timezone
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

class CrawlScheduler:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
    
    def daily_crawl_job(self):
        """매일 자정 실행되는 크롤링 작업"""
        try:
            logging.info("=== 일일 크롤링 작업 시작 ===")
            start_time = datetime.now()
            
            # 1. 동네 이슈 크롤링 및 감성 분석
            call_command('daily_crawl_and_analyze', limit=50)
            
            # 2. 음식점 데이터 크롤링
            call_command('crawl_all_restaurants')
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logging.info(f"일일 크롤링 완료 - 소요시간: {duration:.1f}초")
            
        except Exception as e:
            logging.error(f"크롤링 작업 실패: {str(e)}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.is_running:
            logging.warning("스케줄러가 이미 실행 중입니다")
            return
        
        # 매일 자정(00:00)에 실행
        schedule.every().day.at("00:00").do(self.daily_crawl_job)
        
        # 테스트용: 매 10분마다 실행 (개발 시에만 사용)
        # schedule.every(10).minutes.do(self.daily_crawl_job)
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logging.info("크롤링 스케줄러 시작됨 - 매일 자정 실행")
    
    def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        schedule.clear()
        logging.info("크롤링 스케줄러 중지됨")
    
    def get_next_run_time(self):
        """다음 실행 시간 반환"""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None

# 전역 스케줄러 인스턴스
crawler_scheduler = CrawlScheduler()