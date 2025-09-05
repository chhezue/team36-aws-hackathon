import requests
import os
from datetime import datetime
import json
import sys
sys.path.append('../..')
from load_env import get_env

class SeoulAllDistrictsRestaurants:
    def __init__(self):
        self.api_key = get_env('SEOUL_API_KEY')
        if not self.api_key or self.api_key == 'sample_key':
            raise ValueError("SEOUL_API_KEY 환경변수가 설정되지 않았습니다.")

        self.base_url = f"http://openapi.seoul.go.kr:8088/{self.api_key}/json/CrtfcUpsoInfo"
        self.districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
            '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        self.all_restaurants = []  # 전체 데이터 캐시

    def fetch_all_seoul_data(self, total_count=5000):
        """서울시 전체 음식점 데이터를 한 번에 수집"""
        print(f"서울시 전체 음식점 데이터 {total_count}개 수집 중...")
        
        all_data = []
        batch_size = 1000  # API 한 번에 최대 1000개
        
        for start_idx in range(1, total_count + 1, batch_size):
            end_idx = min(start_idx + batch_size - 1, total_count)
            
            try:
                url = f"{self.base_url}/{start_idx}/{end_idx}"
                print(f"API 호출: {start_idx}~{end_idx}")
                
                response = requests.get(url, timeout=30)
                
                if response.status_code != 200:
                    print(f"API 호출 실패: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                
                if 'CrtfcUpsoInfo' not in data:
                    print(f"데이터 없음: {start_idx}~{end_idx}")
                    break
                
                if 'RESULT' in data['CrtfcUpsoInfo']:
                    result_code = data['CrtfcUpsoInfo']['RESULT']['CODE']
                    if result_code != 'INFO-000':
                        print(f"API 오류: {data['CrtfcUpsoInfo']['RESULT']['MESSAGE']}")
                        break
                
                batch_data = data['CrtfcUpsoInfo']['row']
                all_data.extend(batch_data)
                print(f"수집 완료: {len(batch_data)}개 (총 {len(all_data)}개)")
                
            except Exception as e:
                print(f"배치 {start_idx}~{end_idx} 오류: {e}")
                continue
        
        print(f"전체 데이터 수집 완료: {len(all_data)}개")
        self.all_restaurants = all_data
        return all_data

    def group_restaurants_by_district(self):
        """전체 데이터를 한 번에 구별로 그룹화"""
        district_groups = {district: [] for district in self.districts}
        
        for restaurant in self.all_restaurants:
            # CGG_CODE_NM 필드로 정확한 구 분류
            district = restaurant.get('CGG_CODE_NM', '').strip()
            if district not in self.districts:
                continue
            
            # 일반음식점이고 사용 중인 곳만
            business_type = restaurant.get('COB_CODE_NM', '').strip()
            use_yn = restaurant.get('USE_YN', '').strip()
            
            if business_type == '일반음식점' and use_yn == 'Y':
                license_date = restaurant.get('CRTFC_YMD', '')
                
                if license_date and len(license_date) >= 8:
                    try:
                        # 날짜 형식 검증
                        if len(license_date) == 8:  # YYYYMMDD
                            datetime.strptime(license_date, '%Y%m%d')
                        elif len(license_date) == 10:  # YYYY-MM-DD
                            datetime.strptime(license_date, '%Y-%m-%d')
                        
                        address = restaurant.get('RDN_CODE_NM', '') or restaurant.get('RDN_DETAIL_ADDR', '')
                        district_groups[district].append({
                            'name': restaurant.get('UPSO_NM', '').strip(),
                            'address': address.strip(),
                            'license_date': license_date,
                            'district': district
                        })
                    except ValueError:
                        continue
        
        # 각 구별로 인허가일자 기준 내림차순 정렬 및 상위 5개 선별
        for district in district_groups:
            district_groups[district].sort(key=lambda x: x['license_date'], reverse=True)
            district_groups[district] = district_groups[district][:5]
        
        return district_groups

    def get_restaurants_by_districts(self, target_districts=None):
        """지정된 구들의 최신 개업 음식점 조회"""
        if target_districts is None:
            target_districts = self.districts
        
        # 입력된 구 이름 검증
        invalid_districts = [d for d in target_districts if d not in self.districts]
        if invalid_districts:
            raise ValueError(f"잘못된 구 이름: {invalid_districts}")
        
        # 전체 데이터가 없으면 수집
        if not self.all_restaurants:
            self.fetch_all_seoul_data()
        
        print(f"\n전체 데이터를 구별로 그룹화 중...")
        all_grouped = self.group_restaurants_by_district()
        
        # 요청된 구만 반환
        results = {district: all_grouped[district] for district in target_districts}
        
        for district in target_districts:
            print(f"[{district}] {len(results[district])}개 음식점 발견")
        
        return results

    def format_date(self, date_str):
        """날짜 형식 변환"""
        try:
            if len(date_str) == 8:  # YYYYMMDD
                dt = datetime.strptime(date_str, '%Y%m%d')
                return dt.strftime('%Y-%m-%d')
            elif len(date_str) == 10:  # YYYY-MM-DD
                return date_str
            else:
                return date_str
        except:
            return date_str

    def print_results(self, results):
        """결과 출력"""
        print("\n" + "="*60)
        print("서울시 구별 최신 개업 음식점 TOP 5")
        print("="*60 + "\n")
        
        for district in results.keys():
            restaurants = results[district]
            
            print(f"--- [{district}] 최신 개업 음식점 TOP 5 ---")
            
            if not restaurants:
                print("데이터를 찾을 수 없습니다.\n")
                continue
            
            for i, restaurant in enumerate(restaurants, 1):
                name = restaurant['name'] or '상호명 없음'
                address = restaurant['address'] or '주소 없음'
                date = self.format_date(restaurant['license_date'])
                
                print(f"{i}. {name} | {address} | {date}")
            
            print()

def main():
    try:
        collector = SeoulAllDistrictsRestaurants()
        
        # 예시: 특정 구만 조회 (효율적)
        # target_districts = ['강남구', '서초구', '종로구']
        # results = collector.get_restaurants_by_districts(target_districts)
        
        # 전체 구 조회
        results = collector.get_restaurants_by_districts()
        collector.print_results(results)
        
        # 통계 출력
        total_restaurants = sum(len(restaurants) for restaurants in results.values())
        districts_with_data = sum(1 for restaurants in results.values() if restaurants)
        
        print("="*60)
        print(f"조회 완료: {districts_with_data}/{len(results)}개 구에서 총 {total_restaurants}개 음식점 발견")
        print("="*60)
        
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")

if __name__ == "__main__":
    main()