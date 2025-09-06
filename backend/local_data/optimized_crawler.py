import asyncio
import aiohttp
import re
import json
from datetime import datetime, timedelta
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging

class OptimizedLocalIssueCrawler:
    """성능 최적화된 비동기 크롤러"""
    
    def __init__(self, max_concurrent=10, timeout=30):
        self.max_concurrent = max_concurrent
        self.timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=10,  # 연결 timeout
            sock_read=20  # 읽기 timeout
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        connector = aiohttp.TCPConnector(
            limit=50,  # 전체 연결 풀 크기 감소
            limit_per_host=10,  # 호스트당 연결 수 감소
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,  # keep-alive timeout
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def _fetch_with_retry(self, url: str, max_retries=3) -> Optional[str]:
        """개선된 재시도 로직이 포함된 HTTP 요청"""
        async with self.semaphore:
            for attempt in range(max_retries + 1):
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:  # Rate limit
                            wait_time = min(2 ** attempt, 10)  # 최대 10초
                            logging.info(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                        elif response.status >= 500:  # 서버 오류
                            logging.warning(f"Server error {response.status} for {url}")
                            await asyncio.sleep(1 * (attempt + 1))
                            continue
                        else:
                            logging.warning(f"HTTP {response.status} for {url}")
                            return None
                            
                except asyncio.TimeoutError:
                    logging.warning(f"Timeout attempt {attempt + 1}/{max_retries + 1} for {url}")
                    if attempt < max_retries:
                        await asyncio.sleep(2 * (attempt + 1))
                except aiohttp.ClientError as e:
                    logging.warning(f"Client error attempt {attempt + 1}/{max_retries + 1} for {url}: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(1 * (attempt + 1))
                except Exception as e:
                    logging.error(f"Unexpected error for {url}: {e}")
                    break
                    
        return None
    
    async def crawl_youtube_async(self, district_name: str, limit=5) -> List[Dict]:
        """비동기 YouTube 크롤링"""
        results = []
        queries = [f"{district_name} 뉴스", f"{district_name} 이슈", f"{district_name} 소식"]
        
        # 병렬로 여러 쿼리 처리
        tasks = []
        for query in queries[:2]:  # 처음 2개 쿼리만 사용
            url = f"https://www.youtube.com/results?search_query={quote(query)}"
            tasks.append(self._crawl_single_youtube_query(url, query, limit//2))
        
        query_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in query_results:
            if isinstance(result, list):
                results.extend(result)
                if len(results) >= limit:
                    break
        
        return results[:limit]
    
    async def _crawl_single_youtube_query(self, url: str, query: str, limit: int) -> List[Dict]:
        """단일 YouTube 쿼리 처리"""
        content = await self._fetch_with_retry(url)
        if not content:
            return []
        
        results = []
        try:
            # 정규식으로 빠른 데이터 추출
            video_pattern = r'"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)".*?"viewCountText":{"simpleText":"([^"]*)"'
            matches = re.findall(video_pattern, content, re.DOTALL)
            
            for i, (video_id, title, view_count) in enumerate(matches[:limit]):
                if i >= limit:
                    break
                
                results.append({
                    'source': 'youtube',
                    'title': title.replace('\\', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'view_count': self._parse_view_count(view_count),
                    'published_at': datetime.now() - timedelta(hours=2)
                })
        except Exception as e:
            logging.warning(f"YouTube parsing error for {query}: {e}")
        
        return results
    
    async def crawl_naver_news_async(self, district_name: str, limit=10) -> List[Dict]:
        """비동기 네이버 뉴스 크롤링"""
        queries = [f"{district_name} 뉴스", f"{district_name} 소식"]
        
        # 병렬로 여러 쿼리 처리
        tasks = []
        for query in queries:
            url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1"
            tasks.append(self._crawl_single_naver_query(url, limit//2))
        
        query_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for result in query_results:
            if isinstance(result, list):
                results.extend(result)
        
        return results[:limit]
    
    async def _crawl_single_naver_query(self, url: str, limit: int) -> List[Dict]:
        """단일 네이버 뉴스 쿼리 처리"""
        content = await self._fetch_with_retry(url)
        if not content:
            return []
        
        results = []
        try:
            # 정규식으로 빠른 제목 추출 시도
            title_pattern = r'<a[^>]*class="news_tit"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(title_pattern, content)
            
            if matches:
                for i, (url_match, title) in enumerate(matches[:limit]):
                    results.append({
                        'source': 'naver_news',
                        'title': title.strip(),
                        'url': url_match,
                        'view_count': 0,
                        'published_at': datetime.now() - timedelta(hours=1)
                    })
            else:
                # 정규식 실패시 BeautifulSoup 사용
                soup = BeautifulSoup(content, 'lxml')
                news_items = soup.select('.list_news .bx')[:limit]
                
                for item in news_items:
                    title_elem = item.select_one('.news_tit')
                    if title_elem:
                        results.append({
                            'source': 'naver_news',
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem.get('href', ''),
                            'view_count': 0,
                            'published_at': datetime.now() - timedelta(hours=1)
                        })
        except Exception as e:
            logging.warning(f"Naver news parsing error: {e}")
        
        return results
    
    async def crawl_district_async(self, district_name: str, target_count=50) -> List[Dict]:
        """단일 구 비동기 크롤링"""
        # 병렬로 모든 소스 크롤링
        tasks = [
            self.crawl_naver_news_async(district_name, target_count//2),
            self.crawl_youtube_async(district_name, target_count//2)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
        
        return all_results[:target_count]
    
    async def crawl_all_districts_async(self, districts: List[str], target_count=50) -> Dict[str, List[Dict]]:
        """모든 구 병렬 크롤링"""
        tasks = []
        for district in districts:
            tasks.append(self.crawl_district_async(district, target_count))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        district_results = {}
        for i, result in enumerate(results):
            if isinstance(result, list):
                district_results[districts[i]] = result
            else:
                district_results[districts[i]] = []
                logging.error(f"Error crawling {districts[i]}: {result}")
        
        return district_results
    
    def _parse_view_count(self, view_text: str) -> int:
        """조회수 텍스트를 숫자로 변환"""
        if not view_text:
            return 0
        
        view_text = str(view_text).lower()
        
        # 만 단위 처리
        if '만' in view_text:
            numbers = re.findall(r'([\d.]+)', view_text)
            if numbers:
                try:
                    return int(float(numbers[0]) * 10000)
                except ValueError:
                    return 0
        
        # 억 단위 처리
        elif '억' in view_text:
            numbers = re.findall(r'([\d.]+)', view_text)
            if numbers:
                try:
                    return int(float(numbers[0]) * 100000000)
                except ValueError:
                    return 0
        
        # 일반 숫자 처리
        else:
            numbers = re.findall(r'[\d,]+', view_text)
            if numbers:
                try:
                    return int(numbers[0].replace(',', ''))
                except ValueError:
                    return 0
        
        return 0


# 동기 인터페이스 래퍼
class AsyncCrawlerWrapper:
    """기존 동기 코드와의 호환성을 위한 래퍼"""
    
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
    
    def crawl_all_districts(self, districts: List[str], target_count=50) -> Dict[str, List[Dict]]:
        """동기 인터페이스로 모든 구 크롤링"""
        return asyncio.run(self._crawl_all_async(districts, target_count))
    
    def crawl_single_district(self, district: str, target_count=50) -> List[Dict]:
        """동기 인터페이스로 단일 구 크롤링"""
        return asyncio.run(self._crawl_single_async(district, target_count))
    
    async def _crawl_all_async(self, districts: List[str], target_count: int) -> Dict[str, List[Dict]]:
        """내부 비동기 구현"""
        async with OptimizedLocalIssueCrawler(self.max_concurrent) as crawler:
            return await crawler.crawl_all_districts_async(districts, target_count)
    
    async def _crawl_single_async(self, district: str, target_count: int) -> List[Dict]:
        """내부 비동기 구현"""
        async with OptimizedLocalIssueCrawler(self.max_concurrent) as crawler:
            return await crawler.crawl_district_async(district, target_count)


# 성능 테스트 함수
async def performance_test():
    """성능 테스트"""
    districts = ['강남구', '강동구', '강북구', '강서구', '관악구']
    
    print("=== 성능 테스트 시작 ===")
    
    # 비동기 크롤러 테스트
    start_time = time.time()
    async with OptimizedLocalIssueCrawler(max_concurrent=10) as crawler:
        results = await crawler.crawl_all_districts_async(districts, 20)
    
    async_duration = time.time() - start_time
    total_items = sum(len(items) for items in results.values())
    
    print(f"비동기 크롤링: {async_duration:.2f}초, {total_items}개 수집")
    print(f"구별 평균: {async_duration/len(districts):.2f}초")
    
    # 결과 출력
    for district, items in results.items():
        print(f"  {district}: {len(items)}개")


if __name__ == "__main__":
    # 성능 테스트 실행
    asyncio.run(performance_test())