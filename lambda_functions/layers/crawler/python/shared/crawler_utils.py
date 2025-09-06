"""
크롤링 유틸리티 - timeout 및 네트워크 문제 해결
"""
import time
import random
import logging
from functools import wraps
from typing import Callable, Any

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=10):
    """
    지수 백오프를 사용한 재시도 데코레이터
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logging.error(f"최종 실패 after {max_retries} attempts: {e}")
                        raise e
                    
                    # 지수 백오프 + 지터
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, 0.1 * delay)
                    total_delay = delay + jitter
                    
                    logging.warning(f"재시도 {attempt + 1}/{max_retries}, {total_delay:.2f}초 대기: {e}")
                    time.sleep(total_delay)
            
            return None
        return wrapper
    return decorator

class NetworkHealthChecker:
    """네트워크 상태 체크 및 적응형 timeout 설정"""
    
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.total_requests = 0
    
    def record_response(self, response_time: float, success: bool):
        """응답 시간 및 성공/실패 기록"""
        self.response_times.append(response_time)
        self.total_requests += 1
        
        if not success:
            self.error_count += 1
        
        # 최근 100개 기록만 유지
        if len(self.response_times) > 100:
            self.response_times.pop(0)
    
    def get_adaptive_timeout(self, base_timeout=10):
        """적응형 timeout 계산"""
        if not self.response_times:
            return base_timeout
        
        # 평균 응답 시간의 3배를 timeout으로 설정
        avg_response_time = sum(self.response_times) / len(self.response_times)
        adaptive_timeout = max(avg_response_time * 3, base_timeout)
        
        # 에러율이 높으면 timeout 증가
        if self.total_requests > 10:
            error_rate = self.error_count / self.total_requests
            if error_rate > 0.3:  # 30% 이상 에러율
                adaptive_timeout *= 1.5
        
        return min(adaptive_timeout, 60)  # 최대 60초
    
    def get_health_status(self):
        """네트워크 상태 반환"""
        if self.total_requests < 5:
            return "unknown"
        
        error_rate = self.error_count / self.total_requests
        
        if error_rate < 0.1:
            return "good"
        elif error_rate < 0.3:
            return "fair"
        else:
            return "poor"

# 전역 네트워크 체커 인스턴스
network_checker = NetworkHealthChecker()

def get_optimal_user_agents():
    """최신 User-Agent 목록 반환"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]

def get_random_user_agent():
    """랜덤 User-Agent 반환"""
    return random.choice(get_optimal_user_agents())

def calculate_request_delay(error_rate=0.0):
    """에러율에 따른 요청 간격 계산"""
    base_delay = 0.5  # 기본 0.5초
    
    if error_rate > 0.3:
        return base_delay * 4  # 2초
    elif error_rate > 0.1:
        return base_delay * 2  # 1초
    else:
        return base_delay  # 0.5초

def log_crawler_stats(crawler_name: str, success_count: int, error_count: int, duration: float):
    """크롤링 통계 로깅"""
    total = success_count + error_count
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    logging.info(f"""
=== {crawler_name} 크롤링 통계 ===
성공: {success_count}개
실패: {error_count}개
성공률: {success_rate:.1f}%
소요시간: {duration:.2f}초
평균 속도: {total/duration:.2f}개/초
================================
    """)