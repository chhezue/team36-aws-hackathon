import requests
import json

# API 응답 확인용 디버그 스크립트
api_key = "sample_key"
url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/LOCALDATA_072404/1/5/"

print(f"요청 URL: {url}")
response = requests.get(url, timeout=10)
print(f"응답 코드: {response.status_code}")
print(f"응답 내용: {response.text[:500]}...")