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
        
        # 500개 데이터로 감성 온도 계산
        def calculate_sentiment_temperature(sentiment_data):
            if not sentiment_data:
                return {
                    'temperature': 50,
                    'mood_emoji': '☁️',
                    'description': '보통',
                    'positive_ratio': 0,
                    'negative_ratio': 0
                }
            
            from local_data.sentiment_analyzer import SimpleSentimentAnalyzer
            analyzer = SimpleSentimentAnalyzer()
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            # 500개 데이터 감성 분석
            for item in sentiment_data:
                result = analyzer.analyze_text(item.title)
                if result['sentiment'] == 'positive':
                    positive_count += 1
                elif result['sentiment'] == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = positive_count + negative_count + neutral_count
            if total == 0:
                return {
                    'temperature': 50,
                    'mood_emoji': '☁️',
                    'description': '보통',
                    'positive_ratio': 0,
                    'negative_ratio': 0
                }
            
            pos_ratio = (positive_count / total) * 100
            neg_ratio = (negative_count / total) * 100
            
            # 온도 계산 (0~100)
            temp = int(pos_ratio - neg_ratio + 50)
            temp = max(0, min(100, temp))
            
            if temp >= 80:
                emoji, desc = '😊', '매우 좋음'
            elif temp >= 60:
                emoji, desc = '🙂', '좋음'
            elif temp >= 40:
                emoji, desc = '😐', '보통'
            elif temp >= 20:
                emoji, desc = '😕', '나쁨'
            else:
                emoji, desc = '😔', '매우 나쁨'
                
            return {
                'temperature': temp,
                'mood_emoji': emoji,
                'description': desc,
                'positive_ratio': round(pos_ratio, 1),
                'negative_ratio': round(neg_ratio, 1)
            }
        
        # 7일 이내 데이터만 필터링
        week_ago = today - timedelta(days=7)
        
        # 동네 이슈 - 7일 이내 조회수 높은 순 5개
        recent_issues = LocalIssue.objects.filter(
            location=location,
            collected_at__date__gte=week_ago
        ).order_by('-view_count', '-collected_at')[:5]
        
        # 감성 온도계 - 7일 이내 500개 데이터로 분석
        sentiment_data = LocalIssue.objects.filter(
            location=location,
            collected_at__date__gte=week_ago
        ).order_by('-collected_at')[:500]
        
        # 신규 음식점 (서울시 API - 실제 인허가일자 기준)
        new_restaurants = RestaurantInfo.objects.filter(
            location=location,
            management_number__startswith='seoul_',
            business_status_name='영업'
        ).order_by('-license_date')[:5]
        
        # 핵플 음식점 (카카오 API - 인기 맛집)
        hot_restaurants = RestaurantInfo.objects.filter(
            location=location,
            management_number__startswith='kakao_',
            business_status_name='영업'
        ).order_by('-collected_at')[:5]
        
        # 감성 온도 계산 결과에 영향을 준 뉴스 추가
        sentiment_result = calculate_sentiment_temperature(sentiment_data)
        sentiment_result['influential_news'] = [{
            'title': issue.title,
            'source': issue.get_source_display(),
            'url': issue.url,
            'view_count': issue.view_count,
            'collected_at': issue.collected_at.strftime('%m/%d %H:%M')
        } for issue in sentiment_data[:5]]  # 감성 분석에 사용된 상위 5개 데이터
        
        data = {
            'success': True,
            'district': district,
            'date': today.isoformat(),
            'sentiment': sentiment_result,
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

                'new_restaurants': {
                    'title': '신규 개업 음식점',
                    'emoji': '🆕',
                    'items': [{
                        'name': restaurant.business_name,
                        'type': restaurant.get_business_type_display(),
                        'address': restaurant.road_address or restaurant.lot_address,
                        'license_date': restaurant.license_date.strftime('%m/%d') if restaurant.license_date else ''
                    } for restaurant in new_restaurants]
                },
                'hot_restaurants': {
                    'title': '핵플 음식점',
                    'emoji': '🔥',
                    'items': [{
                        'name': restaurant.business_name,
                        'type': restaurant.get_business_type_display(),
                        'address': restaurant.road_address or restaurant.lot_address,
                        'phone': restaurant.phone_number
                    } for restaurant in hot_restaurants]
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