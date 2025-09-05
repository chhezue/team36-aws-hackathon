from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from local_data.models import Location, SentimentSummary, SentimentAnalysis
from datetime import date, timedelta
from django.db.models import Avg, Count

@csrf_exempt
@require_http_methods(["GET"])
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
        
        # 감성 점수를 온도로 변환하는 함수
        def score_to_temp(score):
            return max(0, min(100, (score + 1) * 50))
        
        def get_mood_emoji(temp):
            if temp >= 70:
                return '😊'
            elif temp >= 30:
                return '😐'
            else:
                return '😔'
        
        # 전체 기간 평균 계산
        avg_score = summaries.aggregate(avg_score=Avg('sentiment_score'))['avg_score'] or 0
        avg_temp = score_to_temp(avg_score)
        
        data = {
            'success': True,
            'district': district,
            'period': f'{start_date} ~ {end_date}',
            'average': {
                'temperature': round(avg_temp, 1),
                'mood_emoji': get_mood_emoji(avg_temp),
                'sentiment_score': round(avg_score, 3)
            },
            'summaries': [
                {
                    'date': summary.date.isoformat(),
                    'temperature': round(score_to_temp(summary.sentiment_score), 1),
                    'mood_emoji': get_mood_emoji(score_to_temp(summary.sentiment_score)),
                    'positive_count': summary.positive_count,
                    'negative_count': summary.negative_count,
                    'neutral_count': summary.neutral_count,
                    'total_count': summary.total_count,
                    'positive_ratio': round(summary.positive_ratio, 1),
                    'negative_ratio': round(summary.negative_ratio, 1),
                    'sentiment_score': round(summary.sentiment_score, 3),
                    'top_keywords': summary.top_keywords
                } for summary in summaries
            ],
            'total_summaries': summaries.count()
        }
        
        return JsonResponse(data)
        
    except Location.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'지역 "{district}"을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'감성 데이터 조회 중 오류: {str(e)}'
        }, status=500)