import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from urllib.parse import quote
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class LocalIssueCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 재시도 전략 개선
        from urllib3.util.retry import Retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def crawl_youtube(self, district_name, limit=5):
        """유튜브에서 7일 이내 해당 구 관련 영상 크롤링"""
        results = []
        queries = [
            f"{district_name}",
            f"{district_name} 소식",
            f"{district_name} 이슈",
            f"{district_name} 생활",
            f"{district_name} 동네",
            f"{district_name} 지역"
        ]
        
        for query in queries:
            if len(results) >= limit:
                break
            try:
                search_url = f"https://www.youtube.com/results?search_query={quote(query)}&sp=CAI%253D"
                response = requests.get(search_url, headers=self.headers)
                if response.status_code == 200:
                    content = response.text
                    start = content.find('var ytInitialData = ') + len('var ytInitialData = ')
                    end = content.find(';</script>', start)
                    if start > 20 and end > start:
                        json_str = content[start:end]
                        try:
                            data = json.loads(json_str)
                            videos = self._extract_youtube_videos(data, 2)
                            for video in videos:
                                if len(results) >= limit:
                                    break
                                # 7일 이내 영상만 필터링
                                published_at = self._parse_youtube_date(video.get('publishedTimeText', ''))
                                if self._is_within_week(published_at):
                                    results.append({
                                        'source': 'youtube',
                                        'title': video.get('title', ''),
                                        'url': f"https://www.youtube.com/watch?v={video.get('videoId', '')}",
                                        'view_count': self._parse_view_count(video.get('viewCount', '0')),
                                        'published_at': published_at
                                    })
                        except json.JSONDecodeError:
                            pass
            except Exception:
                continue
        
        return results
    
    def crawl_naver_search(self, district_name, limit=5):
        """네이버 검색에서 해당 구 관련 최신 검색 결과 크롤링"""
        results = []
        queries = [
            f"{district_name}",
            f"{district_name} 소식",
            f"{district_name} 이슈",
            f"{district_name} 생활정보",
            f"{district_name} 커뮤니티",
            f"{district_name} 동네소식"
        ]
        
        for query in queries:
            if len(results) >= limit:
                break
            try:
                search_url = f"https://search.naver.com/search.naver?query={quote(query)}&where=nexearch&sm=top_hty&fbm=0&ie=utf8"
                response = requests.get(search_url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    search_items = soup.select('.lst_total .bx')[:2]
                    for item in search_items:
                        if len(results) >= limit:
                            break
                        title_elem = item.select_one('.news_tit, .sh_blog_title, .elss.etc_dsc_inner')
                        url_elem = item.select_one('a')
                        
                        if title_elem and url_elem:
                            results.append({
                                'source': 'naver_search',
                                'title': title_elem.get_text(strip=True),
                                'url': url_elem.get('href', ''),
                                'view_count': 0,
                                'published_at': None
                            })
            except Exception:
                continue
        
        return results
    
    def crawl_naver_news(self, district_name, limit=10):
        """네이버 뉴스에서 7일 이내 해당 구 관련 뉴스 크롤링"""
        results = []
        
        # 7일 이내 뉴스만 검색
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        queries = [
            f"{district_name}",
            f"{district_name} 소식",
            f"{district_name} 이슈",
            f"{district_name} 생활",
            f"{district_name} 지역소식",
            f"{district_name} 동네"
        ]
        
        for query in queries:
            if len(results) >= limit:
                break
            try:
                # 7일 이내 뉴스 검색
                ds = start_date.strftime('%Y.%m.%d')
                de = end_date.strftime('%Y.%m.%d')
                news_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1&pd=3&ds={ds}&de={de}"
                
                response = requests.get(news_url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    news_items = soup.select('.list_news .bx')[:3]
                    
                    for item in news_items:
                        if len(results) >= limit:
                            break
                        
                        title_elem = item.select_one('.news_tit')
                        date_elem = item.select_one('.info_group .info')
                        
                        if title_elem:
                            # 날짜 파싱
                            published_at = None
                            if date_elem:
                                date_text = date_elem.get_text(strip=True)
                                published_at = self._parse_date(date_text)
                            
                            results.append({
                                'source': 'naver_news',
                                'title': title_elem.get_text(strip=True),
                                'url': title_elem.get('href', ''),
                                'view_count': 0,
                                'published_at': published_at
                            })
            except Exception as e:
                continue
        
        return results
    
    def _extract_youtube_videos(self, data, limit):
        """YouTube JSON 데이터에서 비디오 정보 추출"""
        videos = []
        try:
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
            
            for section in contents:
                items = section.get('itemSectionRenderer', {}).get('contents', [])
                for item in items:
                    if 'videoRenderer' in item:
                        video = item['videoRenderer']
                        videos.append({
                            'videoId': video.get('videoId', ''),
                            'title': video.get('title', {}).get('runs', [{}])[0].get('text', ''),
                            'viewCount': video.get('viewCountText', {}).get('simpleText', '0'),
                            'publishedTimeText': video.get('publishedTimeText', {}).get('simpleText', '')
                        })
                        if len(videos) >= limit:
                            break
                if len(videos) >= limit:
                    break
        except Exception:
            pass
        
        return videos
    
    def _parse_view_count(self, view_text):
        """조회수 텍스트를 숫자로 변환 (만, 억 단위 처리)"""
        if not view_text:
            return 0
        
        view_text = str(view_text).lower()
        
        # "만" 단위 처리
        if '만' in view_text:
            numbers = re.findall(r'([\d.]+)', view_text)
            if numbers:
                try:
                    return int(float(numbers[0]) * 10000)
                except ValueError:
                    return 0
        
        # "억" 단위 처리  
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
    
    def _parse_date(self, date_text):
        """날짜 텍스트를 datetime으로 변환"""
        try:
            # "오전 10:30" 같은 형식 처리
            if '오전' in date_text or '오후' in date_text:
                return datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            # "어제" 처리
            elif '어제' in date_text:
                return datetime.now() - timedelta(days=1)
            # "오늘" 처리
            elif '오늘' in date_text:
                return datetime.now()
            # "일 전" 처리
            elif '일 전' in date_text:
                days = int(date_text.split('일')[0])
                return datetime.now() - timedelta(days=days)
        except:
            pass
        return datetime.now()
    
    def crawl_all(self, district_name, target_count=50):
        """실제 크롤링 실행"""
        all_results = []
        
        # 네이버 뉴스 크롤링
        news_results = self.crawl_naver_news_fast(f"{district_name} 뉴스", 10)
        all_results.extend(news_results)
        
        # 유튜브 크롤링
        youtube_results = self.crawl_youtube_fast(f"{district_name} 이슈", 5)
        all_results.extend(youtube_results)
        
        return all_results[:target_count]
    

    
    def crawl_naver_news_fast(self, query, limit=5):
        """고속 네이버 뉴스 크롤링 (timeout 개선)"""
        results = []
        
        for attempt in range(3):  # 최대 3회 재시도
            try:
                news_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1"
                response = self.session.get(
                    news_url, 
                    timeout=(10, 30),  # (연결 timeout, 읽기 timeout)
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
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
                    break  # 성공하면 루프 종료
                    
            except requests.exceptions.Timeout:
                print(f"네이버 뉴스 timeout (시도 {attempt + 1}/3): {query}")
                if attempt < 2:  # 마지막 시도가 아니면 대기
                    import time
                    time.sleep(2 ** attempt)  # 지수 백오프
            except Exception as e:
                print(f"네이버 뉴스 크롤링 오류: {e}")
                break
        
        return results
    
    def crawl_youtube_fast(self, query, limit=3):
        """고속 YouTube 크롤링 (timeout 개선)"""
        results = []
        
        for attempt in range(3):  # 최대 3회 재시도
            try:
                search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
                response = self.session.get(
                    search_url, 
                    timeout=(15, 45),  # YouTube는 더 긴 timeout 필요
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    # 정규식으로 빠른 추출
                    video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)[:limit]
                    titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', response.text)[:limit]
                    view_counts = re.findall(r'"viewCountText":{"simpleText":"([^"]+)"', response.text)[:limit]
                    
                    for i, (video_id, title) in enumerate(zip(video_ids, titles)):
                        if i >= limit:
                            break
                        
                        # 조회수 추출
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
                    break  # 성공하면 루프 종료
                    
            except requests.exceptions.Timeout:
                print(f"YouTube timeout (시도 {attempt + 1}/3): {query}")
                if attempt < 2:  # 마지막 시도가 아니면 대기
                    import time
                    time.sleep(3 ** attempt)  # YouTube는 더 긴 대기
            except Exception as e:
                print(f"YouTube 크롤링 오류: {e}")
                break
        
        return results
    
