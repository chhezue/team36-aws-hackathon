from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from local_data.models import Location, RestaurantInfo
import requests
import json
import os
import sys

class Command(BaseCommand):
    help = '모든 구의 음식점 데이터 크롤링 및 AWS DB 저장'
    
    def handle(self, *args, **options):
        self.stdout.write("=== 전체 구 음식점 데이터 수집 시작 ===")
        
        total_saved = 0
        
        # Method 1: 서울시 API 전체 구 데이터 수집
        total_saved += self.crawl_all_seoul_api()
        
        # Method 2: 카카오 API 구별 데이터 수집
        total_saved += self.crawl_all_kakao_api()
        
        self.stdout.write(
            self.style.SUCCESS(f"\n총 {total_saved}개 음식점 데이터 저장 완료")
        )
    
    def crawl_all_seoul_api(self):
        """서울시 API에서 모든 구의 신규 개업 음식점 데이터 수집"""
        api_key = os.getenv('SEOUL_API_KEY')
        if not api_key:
            self.stdout.write(self.style.WARNING("SEOUL_API_KEY 없음 - 서울시 API 스킵"))
            return 0
        
        self.stdout.write("\n=== Method 1: 서울시 API 전체 구 데이터 수집 ===")
        
        # 직접 API 호출
        try:
            base_url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CrtfcUpsoInfo"
            
            # 전체 데이터 수집
            all_restaurants = []
            for start_idx in range(1, 1001, 1000):
                url = f"{base_url}/{start_idx}/{start_idx + 999}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'CrtfcUpsoInfo' in data and 'row' in data['CrtfcUpsoInfo']:
                        all_restaurants.extend(data['CrtfcUpsoInfo']['row'])
            
            # 구별로 그룹화
            district_groups = {}
            for restaurant in all_restaurants:
                district = restaurant.get('CGG_CODE_NM', '').strip()
                business_type = restaurant.get('COB_CODE_NM', '').strip()
                use_yn = restaurant.get('USE_YN', '').strip()
                
                if business_type == '일반음식점' and use_yn == 'Y':
                    if district not in district_groups:
                        district_groups[district] = []
                    
                    license_date = restaurant.get('CRTFC_YMD', '')
                    if license_date and len(license_date) >= 8:
                        district_groups[district].append({
                            'name': restaurant.get('UPSO_NM', '').strip(),
                            'address': restaurant.get('RDN_CODE_NM', '') or restaurant.get('RDN_DETAIL_ADDR', ''),
                            'license_date': license_date,
                            'management_number': restaurant.get('MGTNO', '')
                        })
            
            # 각 구별로 정렬 및 상위 5개 선별
            for district in district_groups:
                district_groups[district].sort(key=lambda x: x['license_date'], reverse=True)
                district_groups[district] = district_groups[district][:5]
            
            results = district_groups
            
            total_saved = 0
            
            for district_name, restaurants in results.items():
                if not restaurants:
                    continue
                
                try:
                    location = Location.objects.get(gu=district_name)
                    saved_count = 0
                    
                    for restaurant in restaurants:
                        # 이미 중복 체크를 아래에서 하므로 삭제
                        
                        # 날짜 변환
                        license_date_str = restaurant['license_date']
                        if len(license_date_str) == 8:  # YYYYMMDD
                            license_date = datetime.strptime(license_date_str, '%Y%m%d').date()
                        else:
                            license_date = datetime.strptime(license_date_str, '%Y-%m-%d').date()
                        
                        # 관리번호 생성
                        management_number = restaurant.get('management_number')
                        if not management_number:
                            management_number = f"seoul_{district_name}_{restaurant['name']}_{license_date_str}"
                        
                        # 중복 체크
                        if RestaurantInfo.objects.filter(management_number=management_number).exists():
                            continue
                        
                        # 데이터베이스에 저장
                        RestaurantInfo.objects.create(
                            location=location,
                            management_number=management_number,
                            business_type='general',
                            license_date=license_date,
                            business_status_code='01',
                            business_status_name='영업',
                            business_name=restaurant['name'],
                            road_address=restaurant['address'],
                            collected_at=timezone.now()
                        )
                        
                        saved_count += 1
                    
                    if saved_count > 0:
                        self.stdout.write(f"  {district_name}: {saved_count}개 저장")
                    total_saved += saved_count
                    
                except Location.DoesNotExist:
                    continue
            
            self.stdout.write(f"서울시 API 총 {total_saved}개 저장")
            return total_saved
            
        except Exception as e:
            self.stdout.write(f"서울시 API 오류: {e}")
            return 0
    
    def crawl_all_kakao_api(self):
        """카카오 API에서 모든 구의 핫플 음식점 데이터 수집"""
        kakao_key = os.getenv('KAKAO_API_KEY')
        if not kakao_key:
            self.stdout.write(self.style.WARNING("KAKAO_API_KEY 없음 - 카카오 API 스킵"))
            return 0
        
        self.stdout.write("\n=== Method 2: 카카오 API 전체 구 데이터 수집 ===")
        
        # 카카오 API 직접 호출
        try:
            districts = [
                '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
            ]
            
            # 구별 좌표 정보
            district_coords = {
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
            
            total_saved = 0
            
            for district_name in districts:
                try:
                    location = Location.objects.get(gu=district_name)
                    
                    # 카카오 API로 해당 구 인기 음식점 수집
                    coords = district_coords.get(district_name, district_coords['강남구'])
                    restaurants = self.get_kakao_restaurants(kakao_key, district_name, coords)
                    saved_count = 0
                    
                    for restaurant in restaurants:
                        # 관리번호 생성 및 중복 체크
                        kakao_id = restaurant.get('kakao_id', '')
                        management_number = f"kakao_{kakao_id}"
                        
                        if not kakao_id or RestaurantInfo.objects.filter(management_number=management_number).exists():
                            continue
                        
                        # 해당 구 필터링
                        address = restaurant.get('address', '')
                        if district_name not in address:
                            continue
                        
                        # 데이터베이스에 저장
                        RestaurantInfo.objects.create(
                            location=location,
                            management_number=management_number,
                            business_type='general',
                            license_date=timezone.now().date(),  # 카카오는 개업일 정보 없음
                            business_status_code='01',
                            business_status_name='영업',
                            business_name=restaurant.get('name', ''),
                            phone_number=restaurant.get('phone', ''),
                            road_address=restaurant.get('road_address', ''),
                            lot_address=address,
                            coordinate_x=float(restaurant.get('x', 0)) if restaurant.get('x') else None,
                            coordinate_y=float(restaurant.get('y', 0)) if restaurant.get('y') else None,
                            collected_at=timezone.now()
                        )
                        
                        saved_count += 1
                    
                    if saved_count > 0:
                        self.stdout.write(f"  {district_name}: {saved_count}개 저장")
                    total_saved += saved_count
                    
                except Location.DoesNotExist:
                    continue
                except Exception as e:
                    self.stdout.write(f"{district_name} 오류: {e}")
                    continue
            
            self.stdout.write(f"카카오 API 총 {total_saved}개 저장")
            return total_saved
            
        except Exception as e:
            self.stdout.write(f"카카오 API 오류: {e}")
            return 0
    
    def get_kakao_restaurants(self, kakao_key, district_name, coords):
        """카카오 API로 해당 구의 인기 음식점 수집"""
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {'Authorization': f'KakaoAK {kakao_key}'}
        
        restaurants = []
        queries = [f"{district_name} 맛집", f"{district_name} 인기 레스토랑"]
        
        for query in queries:
            params = {
                'query': query,
                'category_group_code': 'FD6',
                'x': coords['x'],
                'y': coords['y'],
                'radius': 3000,
                'size': 3,
                'sort': 'accuracy'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for place in data.get('documents', []):
                    if district_name in place.get('address_name', ''):
                        restaurants.append({
                            'kakao_id': place.get('id'),
                            'name': place.get('place_name', ''),
                            'address': place.get('address_name', ''),
                            'road_address': place.get('road_address_name', ''),
                            'phone': place.get('phone', ''),
                            'x': place.get('x', ''),
                            'y': place.get('y', '')
                        })
        
        return restaurants[:5]  # 최대 5개