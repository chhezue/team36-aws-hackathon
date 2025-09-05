import requests
from bs4 import BeautifulSoup

# 강남구청 웹사이트 구조 확인
url = "https://www.gangnam.go.kr"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"응답 코드: {response.status_code}")
    print(f"응답 길이: {len(response.text)}")
    print(f"첫 500자: {response.text[:500]}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title')
    print(f"페이지 제목: {title.get_text() if title else 'None'}")
    
except Exception as e:
    print(f"오류: {e}")