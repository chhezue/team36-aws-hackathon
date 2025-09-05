from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from local_data.weather_service import WeatherService
from local_data.models import Location

@csrf_exempt
@require_http_methods(["GET"])
def get_weather(request):
    district = request.GET.get('district', '강남구')
    
    try:
        # 위치 확인
        location = Location.objects.get(gu=district)
        
        # 날씨 서비스 호출
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_by_location(district)
        
        return JsonResponse({
            'success': True,
            'district': district,
            'weather': weather_data
        })
        
    except Location.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'지역 "{district}"을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'날씨 정보 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=500)