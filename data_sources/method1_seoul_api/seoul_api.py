import requests
import json
from datetime import datetime, timedelta
import os
import sys
sys.path.append('..')
from load_env import load_env_file, get_api_key

class SeoulRestaurantAPI:
    def __init__(self, api_key=None):
        load_env_file('../.env')
        self.api_key = api_key or get_api_key('SEOUL_API_KEY')
        self.base_url = f"http://openapi.seoul.go.kr:8088/{self.api_key}/json"
    
    def get_new_restaurants(self, days_ago=30):
        """최근 개업한 음식점 정보 조회"""
        try:
            # 일반음식점 정보
            general_url = f"{self.base_url}/LOCALDATA_072404_GN/1/1000/"
            
            response = requests.get(general_url, timeout=10)

            data = response.json()
            
            if 'LOCALDATA_072404_GN' not in data:
                return []
            
            restaurants = data['LOCALDATA_072404_GN']['row']
            print(f"전체 데이터 개수: {len(restaurants)}")
            if restaurants:
                print(f"첫 번째 데이터 필드: {list(restaurants[0].keys())}")
                print(f"첫 번째 데이터 예시: {restaurants[0]}")
            
            # 강남구 필터링 및 최근 개업 필터링
            new_restaurants = []
            cutoff_date = datetime.now() - timedelta(days=days_ago)
            gangnam_count = 0
            
            for restaurant in restaurants:
                address = restaurant.get('SITEWHLADDR', '')
                if '강남구' in address:
                    gangnam_count += 1
                    # 인허가일자로 최근 개업 판단
                    license_date = restaurant.get('APVPERMYMD', '')
                    if license_date:
                        try:
                            rest_date = datetime.strptime(license_date, '%Y-%m-%d')
                            if rest_date >= cutoff_date:
                                new_restaurants.append({
                                    'name': restaurant.get('BPLCNM', ''),
                                    'address': restaurant.get('SITEWHLADDR', ''),
                                    'phone': restaurant.get('SITETEL', ''),
                                    'license_date': license_date,
                                    'business_type': restaurant.get('UPTAENM', ''),
                                    'status': restaurant.get('TRDSTATENM', '')
                                })
                        except ValueError:
                            continue
            
            print(f"강남구 음식점 개수: {gangnam_count}")
            return new_restaurants
            
        except Exception as e:
            print(f"API 호출 오류: {e}")
            return []
    
    def save_to_json(self, filename='new_restaurants.json'):
        """결과를 JSON 파일로 저장"""
        restaurants = self.get_new_restaurants()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        return len(restaurants)

if __name__ == "__main__":
    api = SeoulRestaurantAPI()
    restaurants = api.get_new_restaurants(days_ago=30)  # 최근 30일
    print(f"새로 개업한 음식점 {len(restaurants)}개 발견")
    for r in restaurants[:5]:  # 상위 5개만 출력
        print(f"- {r['name']} ({r['address']})")
    
    if restaurants:
        api.save_to_json()
        print("결과가 new_restaurants.json에 저장되었습니다.")