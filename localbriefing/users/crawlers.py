import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from urllib.parse import quote
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from load_env import get_env

class LocalIssueCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_youtube(self, district_name, limit=5):
        """유튜브에서 해당 구 관련 최신 영상 크롤링"""
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
                                results.append({
                                    'source': 'youtube',
                                    'title': video.get('title', ''),
                                    'url': f"https://www.youtube.com/watch?v={video.get('videoId', '')}",
                                    'view_count': self._parse_view_count(video.get('viewCount', '0')),
                                    'published_at': None
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
    
    def crawl_naver_news(self, district_name, limit=5):
        """네이버 뉴스에서 해당 구 관련 최신 뉴스 크롤링"""
        results = []
        queries = [
            f"{district_name} 뉴스",
            f"{district_name} 사건",
            f"{district_name} 공사",
            f"{district_name} 개발",
            f"{district_name} 행사"
        ]
        
        for query in queries:
            if len(results) >= limit:
                break
            try:
                news_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1&pd=4&ds=&de="
                response = requests.get(news_url, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    news_items = soup.select('.list_news .bx')[:2]
                    for item in news_items:
                        if len(results) >= limit:
                            break
                        title_elem = item.select_one('.news_tit')
                        url_elem = item.select_one('.news_tit')
                        
                        if title_elem and url_elem:
                            results.append({
                                'source': 'naver_news',
                                'title': title_elem.get_text(strip=True),
                                'url': url_elem.get('href', ''),
                                'view_count': 0,
                                'published_at': None
                            })
            except Exception:
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
                            'viewCount': video.get('viewCountText', {}).get('simpleText', '0')
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
    
    def crawl_all(self, district_name):
        """모든 소스에서 동네 이슈 크롤링"""
        all_results = []
        
        # YouTube 크롤링
        youtube_results = self.crawl_youtube(district_name)
        all_results.extend(youtube_results)
        
        # 네이버 검색 크롤링
        naver_search_results = self.crawl_naver_search(district_name)
        all_results.extend(naver_search_results)
        
        # 네이버 뉴스 크롤링
        naver_news_results = self.crawl_naver_news(district_name)
        all_results.extend(naver_news_results)
        
        return all_results