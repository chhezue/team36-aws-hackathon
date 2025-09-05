import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from urllib.parse import quote
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from data_sources.load_env import get_api_key

class LocalIssueCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # 연결 풀 설정으로 속도 향상
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=1
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def crawl_youtube(self, district_name, limit=5):
        """유튜브에서 7일 이내 해당 구 관련 영상 크롤링"""
        results = []
        queries = [
            f"{district_name} 뉴스 오늘",
            f"{district_name} 이슈 핫이슈",
            f"{district_name} 사건 사고",
            f"{district_name} 개발 공사",
            f"{district_name} 맛집 신규"
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
            f"{district_name} 뉴스 오늘",
            f"{district_name} 핫이슈 이슈",
            f"{district_name} 사건 사고",
            f"{district_name} 공사 공지",
            f"{district_name} 맛집 오픈"
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
            f"{district_name} 뉴스",
            f"{district_name} 사건 사고",
            f"{district_name} 공사 개발",
            f"{district_name} 행사 축제",
            f"{district_name} 맛집 오픈"
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
        """조회수 텍스트를 숫자로 변환"""
        if not view_text:
            return 0
        
        # 숫자만 추출
        numbers = re.findall(r'[\d,]+', str(view_text))
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
        """병렬 처리로 고속 크롤링 (3일 이내 50개)"""
        # 간단한 검색어 생성
        simple_queries = [
            f"{district_name} 뉴스", f"{district_name} 이슈", f"{district_name} 사건",
            f"{district_name} 맛집", f"{district_name} 공사"
        ]
        
        all_results = []
        
        # 병렬 처리로 속도 향상
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            # 네이버 뉴스 작업
            for query in simple_queries:
                future = executor.submit(self.crawl_naver_news_fast, query, 5)
                futures.append(future)
            
            # YouTube 작업
            for query in simple_queries[:3]:
                future = executor.submit(self.crawl_youtube_fast, query, 3)
                futures.append(future)
            
            # 결과 수집
            for future in as_completed(futures):
                try:
                    results = future.result(timeout=5)  # 5초 타임아웃
                    all_results.extend(results)
                    if len(all_results) >= target_count:
                        break
                except Exception:
                    continue
        
        return all_results[:target_count]
    
    def _generate_refined_queries(self, district_name):
        """정교하고 세분화된 검색어 생성"""
        
        # 뉴스 전용 쿼리 (35개)
        news_queries = []
        
        # 1. 사건/사고 관련 (10개)
        incident_keywords = ['사건', '사고', '화재', '범죄', '도난', '교통사고', '산업재해', '안전사고', '응급상황', '신고']
        for keyword in incident_keywords:
            news_queries.append(f"{district_name} {keyword}")
        
        # 2. 행정/정책 관련 (10개)
        admin_keywords = ['구청', '정책', '예산', '사업', '공지', '발표', '계획', '승인', '결정', '시행']
        for keyword in admin_keywords:
            news_queries.append(f"{district_name} {keyword}")
        
        # 3. 개발/공사 관련 (8개)
        development_keywords = ['개발', '공사', '재개발', '신축', '리모델링', '건설', '인프라', '도로공사']
        for keyword in development_keywords:
            news_queries.append(f"{district_name} {keyword}")
        
        # 4. 시간 기반 쿼리 (7개)
        time_based = [f"{district_name} 오늘 뉴스", f"{district_name} 어제 속보", f"{district_name} 최신 이슈", 
                     f"{district_name} 실시간 속보", f"{district_name} 긴급 뉴스", f"{district_name} 핫이슈", f"{district_name} 주요 뉴스"]
        news_queries.extend(time_based)
        
        # YouTube 전용 쿼리 (25개)
        youtube_queries = []
        
        # 1. 맛집/음식 관련 (8개)
        food_keywords = ['맛집', '신규 맛집', '오픈 맛집', '인기 맛집', '숨은 맛집', '맛집 투어', '맛집 리뷰', '맛집 추천']
        for keyword in food_keywords:
            youtube_queries.append(f"{district_name} {keyword}")
        
        # 2. 생활/일상 관련 (8개)
        lifestyle_keywords = ['생활', '일상', '동네 투어', '산책', '카페', '쇼핑', '데이트', '여행']
        for keyword in lifestyle_keywords:
            youtube_queries.append(f"{district_name} {keyword}")
        
        # 3. 이슈/뉴스 관련 (9개)
        issue_keywords = ['이슈', '뉴스', '핫이슈', '사건', '속보', '리포트', '현장', '인터뷰', '다큐멘터리']
        for keyword in issue_keywords:
            youtube_queries.append(f"{district_name} {keyword}")
        
        return {
            'news': news_queries,
            'youtube': youtube_queries
        }
    
    def crawl_naver_news_fast(self, query, limit=5):
        """고속 네이버 뉴스 크롤링"""
        results = []
        
        try:
            news_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1"
            response = self.session.get(news_url, timeout=3)
            
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
        except Exception:
            pass
        
        return results
    
    def crawl_youtube_fast(self, query, limit=3):
        """고속 YouTube 크롤링"""
        results = []
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            response = self.session.get(search_url, timeout=3)
            
            if response.status_code == 200:
                # 정규식으로 빠른 추출
                video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)[:limit]
                titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', response.text)[:limit]
                
                for i, (video_id, title) in enumerate(zip(video_ids, titles)):
                    if i >= limit:
                        break
                    
                    results.append({
                        'source': 'youtube',
                        'title': title.replace('\\', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': 0,
                        'published_at': datetime.now() - timedelta(hours=2)
                    })
        except Exception:
            pass
        
        return results
    
    def _filter_by_date(self, results, days=3):
        """날짜 기준 필터링"""
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        
        for result in results:
            published_at = result.get('published_at')
            if published_at and published_at >= cutoff_date:
                filtered.append(result)
            elif not published_at:  # 날짜 정보 없으면 포함
                filtered.append(result)
        
        return filtered
    
    def _is_within_days(self, published_at, days):
        """지정된 일수 이내 데이터인지 확인"""
        if not published_at:
            return True
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return published_at >= cutoff_date