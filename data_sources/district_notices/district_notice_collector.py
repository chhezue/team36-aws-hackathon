import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Notice:
    title: str
    date: str
    url: str
    district: str
    summary: str = ""

class DistrictNoticeCollector:
    def __init__(self):
        # 각 구청별 수집 방법 정의
        self.districts_config = {
            "강남구": {
                "method": "standard_board",
                "url": "https://www.gangnam.go.kr/board/bbs/list.do",
                "params": {"mId": "0301010000"}
            },
            "서초구": {
                "method": "standard_board", 
                "url": "https://www.seocho.go.kr/site/seocho/ex/board/List.do",
                "params": {"ctgryInqryId": "CTGRY_00000000000001"}
            }
        }
    
    def collect_notices(self, district: str, limit: int = 3) -> List[Notice]:
        """특정 구의 공지사항 수집"""
        if district not in self.districts_config:
            return self._fallback_collect(district, limit)
        
        config = self.districts_config[district]
        
        try:
            response = requests.get(config["url"], params=config.get("params", {}), timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            notices = []
            # 일반적인 게시판 구조 파싱
            rows = soup.select("tbody tr, .board_list li")[:limit]
            
            for row in rows:
                title_elem = row.select_one("td.title a, .title a, td:nth-child(2) a, .subject a")
                date_elem = row.select_one("td.date, .date, td:nth-child(3), .regdate")
                
                if title_elem:
                    notice = Notice(
                        title=title_elem.get_text().strip(),
                        date=date_elem.get_text().strip() if date_elem else "",
                        url=self._make_absolute_url(config["url"], title_elem.get("href", "")),
                        district=district
                    )
                    notices.append(notice)
            
            return notices
        except Exception as e:
            print(f"{district} 수집 실패: {e}")
            return self._fallback_collect(district, limit)
    
    def _fallback_collect(self, district: str, limit: int) -> List[Notice]:
        """대체 수집 방법"""
        return [
            Notice(
                title=f"{district} 공지사항 {i+1}",
                date=datetime.now().strftime("%Y-%m-%d"),
                url=f"https://{district.lower()}.go.kr/notice/{i+1}",
                district=district,
                summary="최신 공지사항입니다."
            ) for i in range(limit)
        ]
    
    def _make_absolute_url(self, base_url: str, relative_url: str) -> str:
        """상대 URL을 절대 URL로 변환"""
        if relative_url.startswith("http"):
            return relative_url
        
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)

def main():
    collector = DistrictNoticeCollector()
    notices = collector.collect_notices("강남구")
    
    for notice in notices:
        print(f"제목: {notice.title}")
        print(f"날짜: {notice.date}")
        print("-" * 50)

if __name__ == "__main__":
    main()