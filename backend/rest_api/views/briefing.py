from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from local_data.models import Location, LocalIssue, SentimentSummary
from datetime import date

@csrf_exempt
def get_briefing(request):
    district = request.GET.get('district', '강남구')
    
    try:
        location = Location.objects.get(gu=district)
        
        # 오늘 날짜의 감성 요약
        today = date.today()
        sentiment_summary = SentimentSummary.objects.filter(
            location=location, 
            date=today
        ).first()
        
        # 최근 동네 이슈
        recent_issues = LocalIssue.objects.filter(
            location=location
        ).order_by('-collected_at')[:5]
        
        data = {
            'district': district,
            'date': today.isoformat(),
            'sentiment': {
                'temperature': sentiment_summary.sentiment_temperature if sentiment_summary else 0,
                'mood_emoji': sentiment_summary.mood_emoji if sentiment_summary else '☁️',
                'description': sentiment_summary.temperature_description if sentiment_summary else '보통'
            } if sentiment_summary else None,
            'issues': [
                {
                    'title': issue.title,
                    'source': issue.get_source_display(),
                    'url': issue.url,
                    'sentiment_impact': issue.sentiment_impact_score
                } for issue in recent_issues
            ]
        }
        
        return JsonResponse(data)
        
    except Location.DoesNotExist:
        return JsonResponse({'error': 'District not found'}, status=404)