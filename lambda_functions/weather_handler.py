import json
import requests
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """날씨 정보 조회 Lambda 함수"""
    # OPTIONS 요청 처리
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # 요청 파라미터 추출
        gu_name = event.get('gu_name', '강남구')
        
        logger.info(f"날씨 정보 요청: {gu_name}")
        
        # WeatherService 인스턴스 생성 및 날씨 조회
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_by_location(gu_name)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': weather_data,
                'location': gu_name
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"날씨 조회 오류: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            }, ensure_ascii=False)
        }

class WeatherService:
    """기상청 API를 활용한 날씨 정보 서비스"""
    
    def __init__(self):
        self.api_key = os.environ.get('WEATHER_API_KEY')
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
        
        logger.info(f"WeatherService 초기화 - API 키 존재: {'Yes' if self.api_key else 'No'}")
    
    def get_weather_by_location(self, gu_name):
        """구 이름을 기반으로 날씨 정보 조회"""
        
        # 서울시 주요 구별 격자 좌표
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
        
        coords = location_coords.get(gu_name, location_coords['강남구'])
        
        try:
            if self.api_key:
                weather_data = self._call_weather_api(coords['nx'], coords['ny'])
                return self._parse_weather_data(weather_data)
            else:
                return self._get_skeleton_weather_data()
                
        except Exception as e:
            logger.error(f"날씨 API 호출 오류: {e}")
            return self._get_skeleton_weather_data()
    
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
        
        response = requests.get(f"{self.base_url}/getVilageFcst", params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 오류: {response.status_code}")
    
    def _parse_weather_data(self, api_data):
        """API 응답 데이터 파싱"""
        try:
            items = api_data['response']['body']['items']['item']
            
            now = datetime.now()
            current_date = now.strftime('%Y%m%d')
            current_hour = now.hour
            
            weather_by_time = {}
            
            for item in items:
                fcst_date = item['fcstDate']
                fcst_time = item['fcstTime']
                category = item['category']
                value = item['fcstValue']
                
                if fcst_date == current_date:
                    time_key = fcst_time
                    
                    if time_key not in weather_by_time:
                        weather_by_time[time_key] = {}
                    
                    if category == 'TMP':
                        weather_by_time[time_key]['temp'] = int(value)
                    elif category == 'SKY':
                        sky_codes = {'1': '맑음', '3': '구름많음', '4': '흐림'}
                        weather_by_time[time_key]['condition'] = sky_codes.get(value, '맑음')
                    elif category == 'PTY':
                        if value != '0':
                            pty_codes = {'1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
                            weather_by_time[time_key]['condition'] = pty_codes.get(value, '비')
            
            # 현재 날씨 및 시간별 예보 생성
            current_weather = None
            hourly_forecast = []
            
            sorted_times = sorted(weather_by_time.keys())
            
            for time_str in sorted_times:
                hour = int(time_str[:2])
                weather_info = weather_by_time[time_str]
                
                if 'temp' in weather_info and 'condition' in weather_info:
                    formatted_weather = {
                        'time': f"{hour:02d}:00",
                        'temp': f"{weather_info['temp']}°C",
                        'condition': weather_info['condition']
                    }
                    
                    if current_weather is None and hour >= current_hour:
                        current_weather = formatted_weather
                    
                    if hour > current_hour and len(hourly_forecast) < 3:
                        hourly_forecast.append(formatted_weather)
            
            if current_weather is None and sorted_times:
                first_time = sorted_times[0]
                if 'temp' in weather_by_time[first_time] and 'condition' in weather_by_time[first_time]:
                    current_weather = {
                        'time': f"{int(first_time[:2]):02d}:00",
                        'temp': f"{weather_by_time[first_time]['temp']}°C",
                        'condition': weather_by_time[first_time]['condition']
                    }
            
            return {
                'temp': current_weather['temp'] if current_weather else '18°C',
                'condition': current_weather['condition'] if current_weather else '맑음',
                'dust': '보통',
                'description': '외출하기 좋은 날씨예요',
                'hourly_forecast': hourly_forecast
            }
            
        except Exception as e:
            logger.error(f"날씨 데이터 파싱 오류: {e}")
            return self._get_skeleton_weather_data()
    
    def _get_skeleton_weather_data(self):
        """스켈레톤 날씨 데이터"""
        return {
            'temp': '--°C',
            'condition': '정보 없음',
            'dust': '--',
            'description': '날씨 정보를 불러올 수 없습니다',
            'hourly_forecast': []
        }