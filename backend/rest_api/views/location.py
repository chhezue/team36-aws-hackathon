from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from local_data.models import Location, LocalIssue, SentimentSummary
from django.db.models import Count
from datetime import date, timedelta

@csrf_exempt
@require_http_methods(["GET"])
def get_districts(request):
    try:
        # 각 구별 데이터 개수와 함께 반환
        districts_data = []
        locations = Location.objects.all().order_by('gu')
        
        for location in locations:
            # 최근 7일 이슈 개수
            week_ago = date.today() - timedelta(days=7)
            issue_count = LocalIssue.objects.filter(
                location=location,
                collected_at__date__gte=week_ago
            ).count()
            
            districts_data.append({
                'name': location.gu,
                'code': location.gu_code,
                'recent_issues': issue_count,
                'has_data': issue_count > 0
            })
        
        return JsonResponse({
            'success': True,
            'districts': districts_data,
            'total_count': len(districts_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'지역 데이터 조회 중 오류: {str(e)}'
        }, status=500)