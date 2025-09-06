import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from urllib.parse import quote
import time

class LocalIssueCrawler:
    """간단한 동기 크롤러"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_naver_news_fast(self, query, limit=5):
        """네이버 뉴스 크롤링"""
        results = []
        
        try:
            news_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1"
            response = self.session.get(news_url, timeout=15)
            
            if response.status_code == 200:
                # 정규식으로 빠른 추출
                title_pattern = r'<a[^>]*class="news_tit"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
                matches = re.findall(title_pattern, response.text)
                
                for i, (url_match, title) in enumerate(matches[:limit]):
                    if i >= limit:
                        break
                    results.append({
                        'source': 'naver_news',
                        'title': title.strip(),
                        'url': url_match,
                        'view_count': 0,
                        'published_at': datetime.now() - timedelta(hours=1)
                    })
                
                # 정규식으로 충분하지 않으면 BeautifulSoup 사용
                if not results:
                    soup = BeautifulSoup(response.text, 'html.parser')
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
            print(f"네이버 뉴스 크롤링 오류: {e}")
        
        return results
    
    def crawl_youtube_fast(self, query, limit=3):
        """유튜브 크롤링"""
        results = []
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            response = self.session.get(search_url, timeout=20)
            
            if response.status_code == 200:
                # 정규식으로 빠른 추출
                video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)[:limit]
                titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', response.text)[:limit]
                view_counts = re.findall(r'"viewCountText":{"simpleText":"([^"]+)"', response.text)[:limit]
                
                for i, (video_id, title) in enumerate(zip(video_ids, titles)):
                    if i >= limit:
                        break
                    
                    view_count = 0
                    if i < len(view_counts):
                        view_count = self._parse_view_count(view_counts[i])
                    
                    results.append({
                        'source': 'youtube',
                        'title': title.replace('\\', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': view_count,
                        'published_at': datetime.now() - timedelta(hours=2)
                    })
                    
        except Exception as e:
            print(f"유튜브 크롤링 오류: {e}")
        
        return results
    
    def _parse_view_count(self, view_text):
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
    
    def crawl_all(self, district_name, target_count=50):
        """모든 소스에서 크롤링"""
        all_results = []
        
        # 네이버 뉴스 크롤링
        news_results = self.crawl_naver_news_fast(f"{district_name} 뉴스", target_count//2)
        all_results.extend(news_results)
        
        # 유튜브 크롤링
        youtube_results = self.crawl_youtube_fast(f"{district_name} 이슈", target_count//4)
        all_results.extend(youtube_results)
        
        # 추가 쿼리
        additional_queries = [
            f"{district_name} 소식",
            f"{district_name} 생활정보"
        ]
        
        for query in additional_queries:
            if len(all_results) >= target_count:
                break
            news_data = self.crawl_naver_news_fast(query, 5)
            all_results.extend(news_data)
        
        return all_results[:target_count]