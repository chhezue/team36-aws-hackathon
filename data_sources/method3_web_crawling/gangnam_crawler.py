import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re

class GangnamCrawler:
    def __init__(self):
        self.base_url = "https://www.gangnam.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def crawl_notice_board(self):
        """강남구청 공지사항에서 음식점 관련 정보 크롤링"""
        try:
            # 공지사항 페이지
            notice_url = f"{self.base_url}/board/list.do?mid=FM090101"
            response = self.session.get(notice_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            notices = []
            # 게시글 목록 파싱
            board_items = soup.find_all('tr', class_='board-item')
            
            for item in board_items:
                title_elem = item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # 음식점 관련 키워드 필터링
                    if any(keyword in title for keyword in ['음식점', '식당', '카페', '인허가', '영업']):
                        date_elem = item.find('td', class_='date')
                        date = date_elem.get_text(strip=True) if date_elem else ''
                        
                        notices.append({
                            'title': title,
                            'date': date,
                            'url': self.base_url + title_elem.get('href', ''),
                            'type': 'notice'
                        })
            
            return notices
            
        except Exception as e:
            print(f"크롤링 오류: {e}")
            return []
    
    def crawl_business_licenses(self):
        """사업자 인허가 정보 크롤링"""
        try:
            # 인허가 정보 페이지 (가상 URL - 실제 구조에 맞게 수정 필요)
            license_url = f"{self.base_url}/business/license"
            response = self.session.get(license_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            licenses = []
            # 테이블 형태의 인허가 정보 파싱
            table = soup.find('table', class_='license-table')
            if table:
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        licenses.append({
                            'business_name': cols[0].get_text(strip=True),
                            'address': cols[1].get_text(strip=True),
                            'business_type': cols[2].get_text(strip=True),
                            'license_date': cols[3].get_text(strip=True),
                            'type': 'license'
                        })
            
            return licenses
            
        except Exception as e:
            print(f"인허가 정보 크롤링 오류: {e}")
            return []
    
    def get_new_restaurants(self):
        """새로운 음식점 정보 수집"""
        print("강남구청 웹사이트 크롤링 시작...")
        
        # 공지사항 크롤링
        notices = self.crawl_notice_board()
        time.sleep(1)  # 서버 부하 방지
        
        # 인허가 정보 크롤링
        licenses = self.crawl_business_licenses()
        
        # 결과 통합
        all_data = notices + licenses
        
        # 최근 30일 데이터 필터링
        recent_data = []
        for item in all_data:
            if self._is_recent_date(item.get('date', '')):
                recent_data.append(item)
        
        return recent_data
    
    def _is_recent_date(self, date_str, days=30):
        """날짜가 최근 30일 이내인지 확인"""
        try:
            # 다양한 날짜 형식 처리
            for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%m/%d']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    if fmt == '%m/%d':  # 년도가 없는 경우 현재 년도 추가
                        date_obj = date_obj.replace(year=datetime.now().year)
                    
                    diff = datetime.now() - date_obj
                    return diff.days <= days
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def save_to_json(self, filename='crawled_restaurants.json'):
        """결과를 JSON 파일로 저장"""
        data = self.get_new_restaurants()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(data)

if __name__ == "__main__":
    crawler = GangnamCrawler()
    restaurants = crawler.get_new_restaurants()
    print(f"크롤링된 음식점 관련 정보 {len(restaurants)}개")
    for r in restaurants[:3]:
        print(f"- {r.get('title', r.get('business_name', 'N/A'))}")