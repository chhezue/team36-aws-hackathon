import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings

class WeatherService:
    """기상청 API를 활용한 날씨 정보 서비스"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', None)
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"=== WeatherService 초기화 ===")
        self.logger.info(f"API 키 존재: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            self.logger.info(f"API 키 앞 10자리: {self.api_key[:10]}...")
    
    def get_weather_by_location(self, gu_name):
        """구 이름을 기반으로 날씨 정보 조회"""
        
        self.logger.info(f"=== 날씨 정보 요청: {gu_name} ===")
        
        # 서울시 주요 구별 격자 좌표 (기상청 격자 좌표계)
        location_coords = {
            '강남구': {'nx': 61, 'ny': 125},
            '강동구': {'nx': 62, 'ny': 126},
            '강북구': {'nx': 61, 'ny': 128},
            '강서구': {'nx': 58, 'ny': 126},
            '관악구': {'nx': 59, 'ny': 124},
            '광진구': {'nx': 62, 'ny': 126},
            '구로구': {'nx': 58, 'ny': 125},
            '금천구': {'nx': 59, 'ny': 124},
            '노원구': {'nx': 61, 'ny': 129},
            '도봉구': {'nx': 61, 'ny': 129},
            '동대문구': {'nx': 61, 'ny': 127},
            '동작구': {'nx': 59, 'ny': 125},
            '마포구': {'nx': 59, 'ny': 126},
            '서대문구': {'nx': 59, 'ny': 127},
            '서초구': {'nx': 61, 'ny': 125},
            '성동구': {'nx': 61, 'ny': 127},
            '성북구': {'nx': 61, 'ny': 127},
            '송파구': {'nx': 62, 'ny': 125},
            '양천구': {'nx': 58, 'ny': 126},
            '영등포구': {'nx': 58, 'ny': 126},
            '용산구': {'nx': 60, 'ny': 126},
            '은평구': {'nx': 59, 'ny': 127},
            '종로구': {'nx': 60, 'ny': 127},
            '중구': {'nx': 60, 'ny': 127},
            '중랑구': {'nx': 62, 'ny': 127}
        }
        
        coords = location_coords.get(gu_name, location_coords['강남구'])  # 기본값: 강남구
        self.logger.info(f"좌표 정보: nx={coords['nx']}, ny={coords['ny']}")
        
        try:
            # 실제 API 호출 (API 키가 있는 경우)
            if self.api_key:
                self.logger.info("실제 기상청 API 호출 시도...")
                weather_data = self._call_weather_api(coords['nx'], coords['ny'])
                result = self._parse_weather_data(weather_data)
                self.logger.info(f"API 결과: {result}")
                return result
            else:
                # API 키가 없는 경우 Mock 데이터 반환
                self.logger.info("API 키 없음 - Mock 데이터 사용")
                return self._get_mock_weather_data(gu_name)
                
        except Exception as e:
            self.logger.error(f"날씨 API 호출 오류: {e}")
            return self._get_mock_weather_data(gu_name)
    
    def _call_weather_api(self, nx, ny):
        """기상청 API 호출"""
        now = datetime.now()
        base_date = now.strftime('%Y%m%d')
        
        # 현재 시간에 따른 기준 시간 설정
        current_hour = now.hour
        if current_hour < 2:
            base_time = "2300"
            base_date = (now - timedelta(days=1)).strftime('%Y%m%d')
        elif current_hour < 5:
            base_time = "0200"
        elif current_hour < 8:
            base_time = "0500"
        elif current_hour < 11:
            base_time = "0800"
        elif current_hour < 14:
            base_time = "1100"
        elif current_hour < 17:
            base_time = "1400"
        elif current_hour < 20:
            base_time = "1700"
        elif current_hour < 23:
            base_time = "2000"
        else:
            base_time = "2300"
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': 1000,
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }
        
        self.logger.info(f"API 요청 파라미터: {params}")
        
        try:
            response = requests.get(f"{self.base_url}/getVilageFcst", params=params, timeout=10)
            self.logger.info(f"API 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"API 응답 데이터: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                self.logger.error(f"API 오류 상태코드: {response.status_code}")
                self.logger.error(f"API 오류 내용: {response.text}")
                raise Exception(f"API 오류: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.logger.error("API 호출 타임아웃")
            raise Exception("API 타임아웃")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API 요청 오류: {e}")
            raise Exception(f"API 요청 오류: {e}")
    
    def _parse_weather_data(self, api_data):
        """API 응답 데이터 파싱 - 현재 날씨 + 시간별 예보"""
        try:
            self.logger.info("날씨 데이터 파싱 시작...")
            
            # API 응답 구조 확인
            if 'response' not in api_data:
                self.logger.error("API 응답에 'response' 키 없음")
                raise Exception("Invalid API response structure")
            
            response = api_data['response']
            if 'body' not in response:
                self.logger.error("API 응답에 'body' 키 없음")
                raise Exception("Invalid API response structure")
            
            body = response['body']
            if 'items' not in body or not body['items']:
                self.logger.error("API 응답에 데이터 없음")
                raise Exception("No weather data available")
            
            items = body['items']['item']
            self.logger.info(f"총 {len(items)}개의 날씨 데이터 아이템 수신")
            
            # 현재 시간 정보
            now = datetime.now()
            current_date = now.strftime('%Y%m%d')
            current_hour = now.hour
            
            # 시간별 데이터 정리
            weather_by_time = {}
            
            for item in items:
                fcst_date = item['fcstDate']
                fcst_time = item['fcstTime']
                category = item['category']
                value = item['fcstValue']
                
                # 오늘 날짜의 데이터만 처리
                if fcst_date == current_date:
                    time_key = fcst_time
                    
                    if time_key not in weather_by_time:
                        weather_by_time[time_key] = {}
                    
                    if category == 'TMP':  # 온도
                        weather_by_time[time_key]['temp'] = int(value)
                        self.logger.info(f"온도: {value}°C (시간: {fcst_time})")
                    elif category == 'SKY':  # 하늘상태
                        sky_codes = {'1': '맑음', '3': '구름많음', '4': '흐림'}
                        weather_by_time[time_key]['condition'] = sky_codes.get(value, '맑음')
                        self.logger.info(f"하늘상태: {weather_by_time[time_key]['condition']} (시간: {fcst_time})")
                    elif category == 'PTY':  # 강수형태
                        if value != '0':
                            pty_codes = {'1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
                            weather_by_time[time_key]['condition'] = pty_codes.get(value, '비')
            
            # 현재 시간과 가장 가까운 시간대 찾기
            current_weather = None
            hourly_forecast = []
            
            # 시간 순서대로 정렬
            sorted_times = sorted(weather_by_time.keys())
            
            for time_str in sorted_times:
                hour = int(time_str[:2])
                weather_info = weather_by_time[time_str]
                
                # 온도와 하늘상태가 모두 있는 데이터만 사용
                if 'temp' in weather_info and 'condition' in weather_info:
                    formatted_weather = {
                        'time': f"{hour:02d}:00",
                        'temp': f"{weather_info['temp']}°C",
                        'condition': weather_info['condition']
                    }
                    
                    # 현재 시간 이후의 첫 번째 데이터를 현재 날씨로 설정
                    if current_weather is None and hour >= current_hour:
                        current_weather = formatted_weather
                        self.logger.info(f"현재 날씨 설정: {current_weather}")
                    
                    # 현재 시간 이후 3시간까지의 예보 수집
                    if hour > current_hour and len(hourly_forecast) < 3:
                        hourly_forecast.append(formatted_weather)
            
            # 현재 날씨가 없으면 첫 번째 데이터 사용
            if current_weather is None and sorted_times:
                first_time = sorted_times[0]
                if 'temp' in weather_by_time[first_time] and 'condition' in weather_by_time[first_time]:
                    current_weather = {
                        'time': f"{int(first_time[:2]):02d}:00",
                        'temp': f"{weather_by_time[first_time]['temp']}°C",
                        'condition': weather_by_time[first_time]['condition']
                    }
            
            result = {
                'temp': current_weather['temp'] if current_weather else '18°C',
                'condition': current_weather['condition'] if current_weather else '맑음',
                'dust': '보통',
                'description': '외출하기 좋은 날씨예요',
                'hourly_forecast': hourly_forecast
            }
            
            self.logger.info(f"최종 날씨 데이터: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"날씨 데이터 파싱 오류: {e}")
            return self._get_mock_weather_data()
    
    def _get_mock_weather_data(self, location='강남구'):
        """Mock 날씨 데이터 (API 키가 없거나 오류 시 사용)"""
        import random
        
        self.logger.info(f"Mock 날씨 데이터 생성: {location}")
        
        # 현재 실제 온도에 가까운 범위로 수정 (여름철 고려)
        temp_ranges = {
            '강남구': (28, 33),  # 여름철 실제 온도 반영
            '강북구': (27, 32),
            '마포구': (28, 33),
            '송파구': (28, 33),
            '서초구': (28, 33)
        }
        
        temp_range = temp_ranges.get(location, (28, 33))
        current_temp = random.randint(temp_range[0], temp_range[1])
        
        conditions = ['맑음', '구름많음', '흐림']
        condition = random.choice(conditions)
        
        dust_levels = ['좋음', '보통', '나쁨']
        dust = random.choice(dust_levels)
        
        # 시간별 예보 Mock 데이터 생성
        now = datetime.now()
        hourly_forecast = []
        
        for i in range(1, 4):  # 1시간 후, 2시간 후, 3시간 후
            future_hour = (now.hour + i) % 24
            temp_variation = random.randint(-2, 2)
            forecast_temp = max(temp_range[0], min(temp_range[1], current_temp + temp_variation))
            forecast_condition = random.choice(conditions)
            
            hourly_forecast.append({
                'time': f"{future_hour:02d}:00",
                'temp': f'{forecast_temp}°C',
                'condition': forecast_condition
            })
        
        result = {
            'temp': f'{current_temp}°C',
            'condition': condition,
            'dust': dust,
            'description': f'{location}의 현재 날씨입니다 (Mock)',
            'hourly_forecast': hourly_forecast
        }
        
        self.logger.info(f"Mock 데이터 결과: {result}")
        return result