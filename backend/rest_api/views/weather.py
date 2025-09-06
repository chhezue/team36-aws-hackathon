from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from local_data.weather_service import WeatherService


@csrf_exempt
@require_http_methods(["GET"])
def get_weather(request):
    district = request.GET.get('district', '강남구')
    
    try:
        # DB 연결 없이 날씨 서비스 직접 호출
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_by_location(district)
        
        return JsonResponse({
            'success': True,
            'district': district,
            'weather': weather_data
        })
        
    except Exception as e:
        # 오류 시 스켈레톤 데이터 반환
        return JsonResponse({
            'success': True,
            'district': district,
            'weather': {
                'temp': '--°C',
                'condition': '정보 없음',
                'dust': '--',
                'description': '날씨 정보를 불러올 수 없습니다',
                'hourly_forecast': []
            }
        })