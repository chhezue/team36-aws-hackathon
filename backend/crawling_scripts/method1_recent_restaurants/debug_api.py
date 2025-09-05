import requests
import json
import sys
sys.path.append('..')
from load_env import load_env_file, get_api_key

def debug_api():
    load_env_file('../.env')
    api_key = get_api_key('SEOUL_API_KEY')
    
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CrtfcUpsoInfo/1/5"
    
    print(f"API URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"응답 구조: {list(data.keys())}")
            
            if 'CrtfcUpsoInfo' in data:
                print(f"CrtfcUpsoInfo 구조: {list(data['CrtfcUpsoInfo'].keys())}")
                
                if 'row' in data['CrtfcUpsoInfo']:
                    restaurants = data['CrtfcUpsoInfo']['row']
                    print(f"데이터 개수: {len(restaurants)}")
                    
                    if restaurants:
                        first_restaurant = restaurants[0]
                        print(f"\n첫 번째 음식점 필드들:")
                        for key, value in first_restaurant.items():
                            print(f"  {key}: {value}")
                        
                        print(f"\n구 관련 필드 찾기:")
                        for key, value in first_restaurant.items():
                            if '구' in str(value) or 'GU' in key.upper() or 'SIGUN' in key.upper():
                                print(f"  {key}: {value}")
                else:
                    print("row 필드 없음")
            else:
                print("CrtfcUpsoInfo 필드 없음")
                print(f"전체 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"오류 응답: {response.text}")
            
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    debug_api()