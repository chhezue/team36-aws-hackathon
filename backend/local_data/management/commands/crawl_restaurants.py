from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from local_data.models import Location, RestaurantInfo
import requests
import json
import os
import sys

class Command(BaseCommand):
    help = '음식점 데이터 크롤링 및 AWS DB 저장'
    
    def add_arguments(self, parser):
        parser.add_argument('--district', type=str, help='특정 구만 크롤링')
        parser.add_argument('--source', type=str, choices=['seoul_api', 'kakao_api'], default='both', help='데이터 소스 선택')
    
    def handle(self, *args, **options):
        district = options.get('district')
        source = options.get('source', 'both')
        
        if district:
            try:
                location = Location.objects.get(gu=district)
                locations = [location]
            except Location.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"'{district}' 지역을 찾을 수 없습니다."))
                return
        else:
            locations = Location.objects.all()
        
        total_saved = 0
        
        for location in locations:
            self.stdout.write(f"\\n=== {location.gu} 음식점 데이터 수집 ===")
            
            saved_count = 0
            
            # 서울시 API 데이터 수집
            if source in ['seoul_api', 'both']:
                saved_count += self.crawl_seoul_api(location)
            
            # 카카오 API 데이터 수집 (핫플 음식점)
            if source in ['kakao_api', 'both']:
                saved_count += self.crawl_kakao_api(location)
            
            self.stdout.write(f"{location.gu}: {saved_count}개 저장 완료")
            total_saved += saved_count
        
        self.stdout.write(
            self.style.SUCCESS(f"\\n총 {total_saved}개 음식점 데이터 저장 완료")
        )
    
    def crawl_seoul_api(self, location):
        """서울시 API에서 신규 개업 음식점 데이터 수집"""
        api_key = os.getenv('SEOUL_API_KEY')
        if not api_key:
            self.stdout.write(self.style.WARNING("SEOUL_API_KEY 없음 - 서울시 API 스킵"))
            return 0
        
        base_url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CrtfcUpsoInfo"
        saved_count = 0
        
        try:
            # 최대 1000개 데이터 수집
            url = f"{base_url}/1/1000"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.stdout.write(f"서울시 API 호출 실패: HTTP {response.status_code}")
                return 0
            
            data = response.json()
            
            if 'CrtfcUpsoInfo' not in data or 'row' not in data['CrtfcUpsoInfo']:
                return 0
            
            restaurants = data['CrtfcUpsoInfo']['row']
            
            for restaurant in restaurants:
                district = restaurant.get('CGG_CODE_NM', '').strip()
                business_type = restaurant.get('COB_CODE_NM', '').strip()
                use_yn = restaurant.get('USE_YN', '').strip()
                
                # 해당 구의 일반음식점만 필터링
                if (district == location.gu and 
                    business_type == '일반음식점' and 
                    use_yn == 'Y'):
                    
                    management_number = restaurant.get('MGTNO', '')
                    
                    # 중복 체크
                    if RestaurantInfo.objects.filter(management_number=management_number).exists():
                        continue
                    
                    license_date_str = restaurant.get('CRTFC_YMD', '')
                    if not license_date_str or len(license_date_str) < 8:
                        continue
                    
                    try:
                        # 날짜 변환
                        if len(license_date_str) == 8:  # YYYYMMDD
                            license_date = datetime.strptime(license_date_str, '%Y%m%d').date()
                        else:
                            license_date = datetime.strptime(license_date_str, '%Y-%m-%d').date()
                        
                        # 데이터베이스에 저장
                        RestaurantInfo.objects.create(
                            location=location,
                            management_number=management_number,
                            business_type='general',
                            license_date=license_date,
                            business_status_code=restaurant.get('TRDSTATEGBN', '01'),
                            business_status_name='영업',
                            business_name=restaurant.get('UPSO_NM', '').strip(),
                            phone_number=restaurant.get('TELNO', ''),
                            road_address=restaurant.get('RDN_CODE_NM', '') or restaurant.get('RDN_DETAIL_ADDR', ''),
                            collected_at=timezone.now()
                        )
                        
                        saved_count += 1
                        
                    except ValueError:
                        continue
            
            self.stdout.write(f"  서울시 API: {saved_count}개 저장")
            return saved_count
            
        except Exception as e:
            self.stdout.write(f"서울시 API 오류: {e}")
            return 0
    
    def crawl_kakao_api(self, location):
        """카카오 API에서 핫플 음식점 데이터 수집"""
        kakao_key = os.getenv('KAKAO_API_KEY')
        if not kakao_key:
            self.stdout.write(self.style.WARNING("KAKAO_API_KEY 없음 - 카카오 API 스킵"))
            return 0
        
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
        
        coords = district_coords.get(location.gu, district_coords['강남구'])
        saved_count = 0
        
        try:
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            headers = {'Authorization': f'KakaoAK {kakao_key}'}
            
            # 검색 쿼리
            queries = [f"{location.gu} 맛집", f"{location.gu} 인기 레스토랑"]
            
            for query in queries:
                params = {
                    'query': query,
                    'category_group_code': 'FD6',  # 음식점
                    'x': coords['x'],
                    'y': coords['y'],
                    'radius': 3000,
                    'size': 5,
                    'sort': 'accuracy'
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for place in data.get('documents', []):
                        place_id = place.get('id')
                        
                        # 중복 체크 (카카오 ID로)
                        if RestaurantInfo.objects.filter(management_number=f"kakao_{place_id}").exists():
                            continue
                        
                        # 해당 구 필터링
                        address = place.get('address_name', '')
                        if location.gu not in address:
                            continue
                        
                        # 데이터베이스에 저장
                        RestaurantInfo.objects.create(
                            location=location,
                            management_number=f"kakao_{place_id}",
                            business_type='general',
                            license_date=timezone.now().date(),  # 카카오는 개업일 정보 없음
                            business_status_code='01',
                            business_status_name='영업',
                            business_name=place.get('place_name', ''),
                            phone_number=place.get('phone', ''),
                            road_address=place.get('road_address_name', ''),
                            lot_address=address,
                            coordinate_x=float(place.get('x', 0)),
                            coordinate_y=float(place.get('y', 0)),
                            collected_at=timezone.now()
                        )
                        
                        saved_count += 1
            
            self.stdout.write(f"  카카오 API: {saved_count}개 저장")
            return saved_count
            
        except Exception as e:
            self.stdout.write(f"카카오 API 오류: {e}")
            return 0