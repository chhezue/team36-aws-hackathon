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
        
        # 서울시 전체 구 정보 (좌표 포함)
        self.seoul_districts = {
            '강남구': {'x': '127.0276', 'y': '37.4979'},
            '강동구': {'x': '127.1238', 'y': '37.5301'},
            '강북구': {'x': '127.0277', 'y': '37.6396'},
            '강서구': {'x': '126.8495', 'y': '37.5509'},
            '관악구': {'x': '126.9516', 'y': '37.4784'},
            '광진구': {'x': '127.0845', 'y': '37.5384'},
            '구로구': {'x': '126.8875', 'y': '37.4954'},
            '금천구': {'x': '126.9009', 'y': '37.4569'},
            '노원구': {'x': '127.0563', 'y': '37.6542'},
            '도봉구': {'x': '127.0471', 'y': '37.6688'},
            '동대문구': {'x': '127.0421', 'y': '37.5838'},
            '동작구': {'x': '126.9393', 'y': '37.5124'},
            '마포구': {'x': '126.9084', 'y': '37.5615'},
            '서대문구': {'x': '126.9368', 'y': '37.5794'},
            '서초구': {'x': '127.0276', 'y': '37.4836'},
            '성동구': {'x': '127.0408', 'y': '37.5633'},
            '성북구': {'x': '127.0167', 'y': '37.6023'},
            '송파구': {'x': '127.1059', 'y': '37.5145'},
            '양천구': {'x': '126.8664', 'y': '37.5170'},
            '영등포구': {'x': '126.8956', 'y': '37.5264'},
            '용산구': {'x': '126.9910', 'y': '37.5384'},
            '은평구': {'x': '126.9312', 'y': '37.6176'},
            '종로구': {'x': '126.9794', 'y': '37.5735'},
            '중구': {'x': '126.9979', 'y': '37.5641'},
            '중랑구': {'x': '127.0927', 'y': '37.6063'}
        }
    
    def get_kakao_places(self, district='강남구', page=1):
        """카카오 로컬 API - 지역별 인기 음식점"""
        try:
            kakao_key = get_api_key('KAKAO_API_KEY')
            print(f"카카오 API 키: {kakao_key[:10]}...")
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            
            headers = {
                'Authorization': f'KakaoAK {kakao_key}'
            }
            
            # 지역별 세분화된 검색 쿼리
            district_coords = self.seoul_districts.get(district, self.seoul_districts['강남구'])
            
            # 고도화된 검색 쿼리 (트렌드, 평점, 신규 등)
            advanced_queries = [
                f"{district} 맛집 추천",
                f"{district} 인기 레스토랑", 
                f"{district} 새로 오픈",
                f"{district} 평점 높은 식당",
                f"{district} 핫플레이스"
            ]
            
            all_restaurants = []
            
            for query in advanced_queries:
                params = {
                    'query': query,
                    'category_group_code': 'FD6',  # 음식점 카테고리
                    'x': district_coords['x'],
                    'y': district_coords['y'],
                    'radius': 5000,  # 5km 반경으로 축소 (더 정확한 지역 검색)
                    'page': page,
                    'size': 2,  # 쿼리당 2개씩 수집
                    'sort': 'accuracy'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'documents' in data:
                        for place in data['documents']:
                            # 중복 제거 및 해당 구 필터링
                            place_id = place.get('id')
                            address = place.get('address_name', '')
                            
                            if (district in address and 
                                not any(r.get('kakao_id') == place_id for r in all_restaurants)):
                                all_restaurants.append({
                                    'name': place.get('place_name', ''),
                                    'address': address,
                                    'road_address': place.get('road_address_name', ''),
                                    'phone': place.get('phone', ''),
                                    'category': place.get('category_name', ''),
                                    'x': place.get('x', ''),
                                    'y': place.get('y', ''),
                                    'place_url': place.get('place_url', ''),
                                    'kakao_id': place_id,
                                    'source': 'kakao',
                                    'search_query': query,
                                    'district': district
                                })
                                
                                # 최대 5개까지만 수집
                                if len(all_restaurants) >= 5:
                                    return all_restaurants[:5]
            
            return all_restaurants[:5]  # 최대 5개 반환
            
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
    
    def get_all_new_restaurants(self, district='강남구'):
        """지역별 인기 음식점 정보 수집 (최대 5개)"""
        all_restaurants = []
        
        # 카카오 API
        print(f"{district} 카카오 API 호출 중...")
        kakao_data = self.get_kakao_places(district)
        print(f"카카오에서 {len(kakao_data)}개 발견")
        all_restaurants.extend(kakao_data)
        
        # 중복 제거 및 최대 5개 제한
        unique_restaurants = []
        seen_names = set()
        
        for restaurant in all_restaurants:
            name = restaurant.get('name', '')
            if name not in seen_names:
                seen_names.add(name)
                unique_restaurants.append(restaurant)
                
                if len(unique_restaurants) >= 5:
                    break
        
        return unique_restaurants[:5]
    
    def save_to_json(self, district='강남구', filename='realtime_new_restaurants.json'):
        """지역별 결과를 JSON 파일로 저장"""
        restaurants = self.get_all_new_restaurants(district)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        
        return len(restaurants)
    
    def get_available_districts(self):
        """사용 가능한 서울시 구 목록 반환"""
        return list(self.seoul_districts.keys())

if __name__ == "__main__":
    api = RealtimeRestaurantAPI()
    
    # 사용 가능한 구 목록 출력
    districts = api.get_available_districts()
    print(f"사용 가능한 서울시 구: {len(districts)}개")
    print(f"구 목록: {', '.join(districts)}")
    
    # 기본 강남구로 테스트
    test_district = '강남구'
    restaurants = api.get_all_new_restaurants(test_district)
    
    print(f"\n{test_district} 인기 음식점 {len(restaurants)}개 발견")
    
    # 소스별 통계
    sources = {}
    for r in restaurants:
        source = r.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("소스별 통계:")
    for source, count in sources.items():
        print(f"- {source}: {count}개")
    
    # 발견된 음식점 출력 (최대 5개)
    print(f"\n{test_district} 인기 음식점:")
    for i, r in enumerate(restaurants, 1):
        print(f"{i}. {r.get('name', 'N/A')} ({r.get('category', 'N/A')})")
        print(f"   주소: {r.get('address', 'N/A')}")
        print(f"   소스: {r.get('source', 'N/A')}")
        print()
    
    # JSON 저장
    count = api.save_to_json(test_district)
    print(f"총 {count}개 음식점 정보가 realtime_new_restaurants.json에 저장되었습니다.")