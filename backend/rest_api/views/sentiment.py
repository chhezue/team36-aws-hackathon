from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from local_data.models import Location, SentimentSummary
from datetime import date, timedelta

@csrf_exempt
def get_sentiment_summary(request):
    district = request.GET.get('district', '강남구')
    days = int(request.GET.get('days', 7))
    
    try:
        location = Location.objects.get(gu=district)
        
        # 최근 N일간의 감성 요약
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        summaries = SentimentSummary.objects.filter(
            location=location,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        data = {
            'district': district,
            'period': f'{start_date} ~ {end_date}',
            'summaries': [
                {
                    'date': summary.date.isoformat(),
                    'temperature': summary.sentiment_temperature,
                    'mood_emoji': summary.mood_emoji,
                    'positive_count': summary.positive_count,
                    'negative_count': summary.negative_count,
                    'neutral_count': summary.neutral_count,
                    'total_issues': summary.total_issues
                } for summary in summaries
            ]
        }
        
        return JsonResponse(data)
        
    except Location.DoesNotExist:
        return JsonResponse({'error': 'District not found'}, status=404)