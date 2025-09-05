import requests
import json
from datetime import datetime, timedelta
import os
import sys
sys.path.append('..')
from load_env import load_env_file, get_api_key

class RealtimeRestaurantAPI:
    def __init__(self):
        load_env_file()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_kakao_places(self, page=1):
        """카카오 로컬 API - 최근 등록된 음식점"""
        try:
            kakao_key = get_api_key('KAKAO_API_KEY')
            print(f"카카오 API 키: {kakao_key[:10]}...")
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            
            headers = {
                'Authorization': f'KakaoAK {kakao_key}'
            }
            
            # 최근 개업 관련 키워드로 검색
            popular_queries = [
                "강남구 맛집",
                "강남역 인기 술집",
                "신논현역 점심 맛집",
                "강남구 평점 좋은 식당"  # 평점 키워드를 직접 사용
            ]
            
            all_restaurants = []
            
            for query in popular_queries:
                params = {
                    'query': query,
                    'category_group_code': 'FD6',  # 음식점 카테고리
                    'x': '127.0276',  # 강남구 중심 경도
                    'y': '37.4979',   # 강남구 중심 위도
                    'radius': 10000,  # 10km 반경
                    'page': page,
                    'size': 5,
                    'sort': 'accuracy'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'documents' in data:
                        for place in data['documents']:
                            # 중복 제거
                            place_id = place.get('id')
                            if not any(r.get('kakao_id') == place_id for r in all_restaurants):
                                all_restaurants.append({
                                    'name': place.get('place_name', ''),
                                    'address': place.get('address_name', ''),
                                    'road_address': place.get('road_address_name', ''),
                                    'phone': place.get('phone', ''),
                                    'category': place.get('category_name', ''),
                                    'x': place.get('x', ''),
                                    'y': place.get('y', ''),
                                    'place_url': place.get('place_url', ''),
                                    'kakao_id': place.get('id', ''),
                                    'source': 'kakao',
                                    'search_query': query
                                })
            
            return all_restaurants
            
        except Exception as e:
            print(f"카카오 API 오류: {e}")
            return []
    
    def get_naver_places(self):
        """네이버 검색 API - 최근 음식점"""
        try:
            naver_client_id = get_api_key('NAVER_CLIENT_ID')
            naver_client_secret = get_api_key('NAVER_CLIENT_SECRET')
            
            url = "https://openapi.naver.com/v1/search/local.json"
            
            headers = {
                'X-Naver-Client-Id': naver_client_id,
                'X-Naver-Client-Secret': naver_client_secret
            }

            popular_queries = [
                "강남구 맛집",
                "강남역 맛집",
                "신논현역 맛집"
            ]
            
            all_restaurants = []
            
            for query in popular_queries:
                params = {
                    'query': query,
                    'display': 10,
                    'start': 1,
                    'sort': 'comment'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        for item in data['items']:
                            # 강남구 필터링
                            if '강남구' in item.get('address', ''):
                                all_restaurants.append({
                                    'name': item.get('title', '').replace('<b>', '').replace('</b>', ''),
                                    'address': item.get('address', ''),
                                    'road_address': item.get('roadAddress', ''),
                                    'phone': item.get('telephone', ''),
                                    'category': item.get('category', ''),
                                    'link': item.get('link', ''),
                                    'source': 'naver',
                                    'search_query': query
                                })
            
            return all_restaurants
            
        except Exception as e:
            print(f"네이버 API 오류: {e}")
            return []
    
    def get_all_new_restaurants(self):
        """모든 소스에서 신규 음식점 정보 수집"""
        all_restaurants = []
        
        # 카카오 API
        print("카카오 API 호출 중...")
        kakao_data = self.get_kakao_places()
        print(f"카카오에서 {len(kakao_data)}개 발견")
        all_restaurants.extend(kakao_data)
        
        # 네이버 API  
        print("네이버 API 호출 중...")
        naver_data = self.get_naver_places()
        print(f"네이버에서 {len(naver_data)}개 발견")
        all_restaurants.extend(naver_data)
        
        return all_restaurants
    
    def save_to_json(self, filename='realtime_new_restaurants.json'):
        """결과를 JSON 파일로 저장"""
        restaurants = self.get_all_new_restaurants()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        
        return len(restaurants)

if __name__ == "__main__":
    api = RealtimeRestaurantAPI()
    restaurants = api.get_all_new_restaurants()
    
    print(f"실시간 신규 음식점 {len(restaurants)}개 발견")
    
    # 소스별 통계
    sources = {}
    for r in restaurants:
        source = r.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("소스별 통계:")
    for source, count in sources.items():
        print(f"- {source}: {count}개")
    
    # 상위 5개 출력
    print("\n최근 발견된 음식점:")
    for r in restaurants[:5]:
        print(f"- {r.get('name', 'N/A')} ({r.get('address', 'N/A')}) - {r.get('source', 'N/A')}")
    
    # JSON 저장
    count = api.save_to_json()
    print(f"\n총 {count}개 음식점 정보가 realtime_new_restaurants.json에 저장되었습니다.")