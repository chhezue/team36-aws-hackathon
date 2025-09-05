from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from local_data.models import Location, LocalIssue, SentimentSummary, DistrictAnnouncement, RestaurantInfo
from datetime import date, timedelta
import json

@csrf_exempt
@require_http_methods(["GET"])
def get_briefing(request):
    district = request.GET.get('district', '강남구')
    
    try:
        location = Location.objects.get(gu=district)
        today = date.today()
        
        # 감성 요약 데이터
        sentiment_summary = SentimentSummary.objects.filter(
            location=location, 
            date=today
        ).first()
        
        # 감성 점수를 온도로 변환 (0~100 스케일)
        def get_mood_data(sentiment_summary):
            if not sentiment_summary:
                return {
                    'temperature': 50,
                    'mood_emoji': '☁️',
                    'description': '보통',
                    'positive_ratio': 0,
                    'negative_ratio': 0
                }
            
            score = sentiment_summary.sentiment_score
            temp = max(0, min(100, (score + 1) * 50))  # -1~1을 0~100으로 변환
            
            if temp >= 70:
                emoji, desc = '😊', '좋음'
            elif temp >= 30:
                emoji, desc = '😐', '보통'
            else:
                emoji, desc = '😔', '나쁨'
                
            return {
                'temperature': round(temp, 1),
                'mood_emoji': emoji,
                'description': desc,
                'positive_ratio': round(sentiment_summary.positive_ratio, 1),
                'negative_ratio': round(sentiment_summary.negative_ratio, 1)
            }
        
        # 최근 동네 이슈 (7일 이내, 5개 제한)
        week_ago = today - timedelta(days=7)
        recent_issues = LocalIssue.objects.filter(
            location=location,
            collected_at__date__gte=week_ago
        ).order_by('-view_count', '-collected_at')[:5]
        
        # 구청 공지사항
        announcements = DistrictAnnouncement.objects.filter(
            location=location
        ).order_by('-created_at')[:5]
        
        # 신규 음식점 (최근 30일)
        month_ago = today - timedelta(days=30)
        new_restaurants = RestaurantInfo.objects.filter(
            location=location,
            license_date__gte=month_ago,
            business_status_name='영업'
        ).order_by('-license_date')[:5]
        
        data = {
            'success': True,
            'district': district,
            'date': today.isoformat(),
            'sentiment': get_mood_data(sentiment_summary),
            'categories': {
                'local_issues': {
                    'title': '동네 이슈',
                    'emoji': '💬',
                    'items': [{
                        'title': issue.title,
                        'source': issue.get_source_display(),
                        'url': issue.url,
                        'view_count': issue.view_count,
                        'collected_at': issue.collected_at.strftime('%m/%d %H:%M')
                    } for issue in recent_issues]
                },
                'announcements': {
                    'title': '구청 소식',
                    'emoji': '📢',
                    'items': [{
                        'title': announcement.title,
                        'department': announcement.department,
                        'view_count': announcement.view_count,
                        'created_at': announcement.created_at.strftime('%m/%d') if announcement.created_at else ''
                    } for announcement in announcements]
                },
                'new_restaurants': {
                    'title': '신규 개업 음식점',
                    'emoji': '🆕',
                    'items': [{
                        'name': restaurant.business_name,
                        'type': restaurant.get_business_type_display(),
                        'address': restaurant.road_address or restaurant.lot_address,
                        'license_date': restaurant.license_date.strftime('%m/%d') if restaurant.license_date else ''
                    } for restaurant in new_restaurants]
                }
            }
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
            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=500)