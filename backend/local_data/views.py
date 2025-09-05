from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import Location, SentimentSummary, SentimentAnalysis, RawData, DistrictAnnouncement, LocalIssue
from .sentiment_analyzer import SimpleSentimentAnalyzer, update_sentiment_summary

def briefing_view(request):
    """실제 데이터 기반 브리핑 뷰"""
    from restaurants.views import get_restaurant_data
    
    # 사용자 거주지 가져오기 (세션 또는 기본값)
    user_district = request.session.get('district', '강남구')
    location = Location.objects.filter(gu=user_district).first()
    if not location:
        location, _ = Location.objects.get_or_create(gu=user_district)
    
    today = date.today()
    
    # 오늘의 감성 요약
    today_summary = SentimentSummary.objects.filter(
        location=location,
        date=today
    ).first()
    
    # 감성 온도에 가장 영향을 많이 준 상위 5개 콘텐츠
    top_impact_content = get_top_impact_content(location, today)
    
    # 오늘의 동네 이슈를 소스별로 분류
    local_issues = {
        'youtube': LocalIssue.objects.filter(
            location=location,
            source='youtube',
            collected_at__date=today
        ).order_by('-collected_at')[:5],
        'naver_news': LocalIssue.objects.filter(
            location=location,
            source='naver_news',
            collected_at__date=today
        ).order_by('-collected_at')[:5]
    }
    
    # 구청 공지사항 (최신 3개)
    district_news = DistrictAnnouncement.objects.filter(
        location=location
    ).order_by('-collected_at')[:3]
    
    # 음식점 데이터
    restaurant_data = get_restaurant_data(user_district)
    
    # 날씨 데이터 (실제 크롤링)
    from .weather_service import WeatherService
    weather_service = WeatherService()
    weather_data = weather_service.get_weather_by_location(location.gu)
    
    briefing_data = {
        'user_name': '사용자',
        'location': f'{location.gu}',
        'date': today.strftime('%Y년 %m월 %d일'),
        'weather': weather_data,
        'sentiment_summary': today_summary,
        'top_impact_content': top_impact_content,
        'local_issues': local_issues,
        'district_news': district_news,
        'new_restaurants': restaurant_data.get('new_restaurants', []),
        'popular_restaurants': restaurant_data.get('popular_restaurants', [])
    }
    return render(request, 'briefing.html', briefing_data)

def get_top_impact_content(location, target_date):
    """감성 온도에 가장 영향을 많이 준 상위 5개 콘텐츠 추출"""
    analyses = SentimentAnalysis.objects.filter(
        location=location,
        analyzed_at__date=target_date
    )
    
    impact_items = []
    
    for analysis in analyses:
        if analysis.content_type == 'local_issue':
            try:
                issue = LocalIssue.objects.get(id=analysis.content_id)
                # 영향도 계산
                sentiment_weight = 1 if analysis.sentiment == 'positive' else -1 if analysis.sentiment == 'negative' else 0
                impact_score = abs(analysis.confidence * sentiment_weight * 100)
                
                impact_items.append({
                    'title': issue.title,
                    'url': issue.url,
                    'source': issue.get_source_display(),
                    'source_type': issue.source,
                    'sentiment': analysis.sentiment,
                    'impact_score': impact_score,
                    'view_count': issue.view_count
                })
            except LocalIssue.DoesNotExist:
                continue
    
    # 영향도 높은 순으로 정렬 후 상위 5개 반환
    impact_items.sort(key=lambda x: x['impact_score'], reverse=True)
    return impact_items[:5]



def set_user_location(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        if district:
            request.session['district'] = district
            return JsonResponse({'status': 'success', 'district': district})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def complete_onboarding(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        categories = request.POST.getlist('categories')
        
        if district:
            request.session['district'] = district
        if categories:
            request.session['categories'] = categories
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def theme_selector(request):
    return JsonResponse({'status': 'success'})

def sentiment_dashboard(request, location_id=None):
    """감성 온도계 대시보드"""
    if location_id:
        location = get_object_or_404(Location, id=location_id)
    else:
        # 기본값: 강남구
        location = Location.objects.filter(gu='강남구').first()
    
    today = date.today()
    
    # 오늘의 감성 요약
    today_summary = SentimentSummary.objects.filter(
        location=location,
        date=today
    ).first()
    
    if not today_summary:
        # 데이터가 없으면 업데이트 시도
        today_summary = update_sentiment_summary(location, today)
    
    # 최근 7일 트렌드
    week_summaries = SentimentSummary.objects.filter(
        location=location,
        date__gte=today - timedelta(days=6)
    ).order_by('date')
    
    # 차트 데이터 준비
    chart_data = {
        'dates': [summary.date.strftime('%m/%d') for summary in week_summaries],
        'sentiment_scores': [summary.sentiment_score for summary in week_summaries],
        'positive_ratios': [summary.positive_ratio for summary in week_summaries],
        'negative_ratios': [summary.negative_ratio for summary in week_summaries]
    }
    
    context = {
        'location': location,
        'today_summary': today_summary,
        'chart_data': chart_data,
        'locations': Location.objects.all()
    }
    
    return render(request, 'sentiment/dashboard.html', context)

def sentiment_api(request, location_id):
    """감성 데이터 API"""
    location = get_object_or_404(Location, id=location_id)
    days = int(request.GET.get('days', 7))
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    summaries = SentimentSummary.objects.filter(
        location=location,
        date__gte=start_date
    ).order_by('date')
    
    data = {
        'location': location.gu,
        'summaries': [
            {
                'date': summary.date.isoformat(),
                'sentiment_score': summary.sentiment_score,
                'positive_count': summary.positive_count,
                'negative_count': summary.negative_count,
                'neutral_count': summary.neutral_count,
                'positive_ratio': summary.positive_ratio,
                'negative_ratio': summary.negative_ratio,
                'mood_emoji': summary.mood_emoji,
                'top_keywords': summary.top_keywords
            }
            for summary in summaries
        ]
    }
    
    return JsonResponse(data)

def sentiment_details_api(request, location_id):
    """감성 온도에 영향을 준 상세 데이터 API"""
    location = get_object_or_404(Location, id=location_id)
    today = date.today()
    
    # 오늘의 감성 분석 데이터 가져오기
    analyses = SentimentAnalysis.objects.filter(
        location=location,
        analyzed_at__date=today
    ).order_by('-confidence')[:10]  # 신뢰도 높은 순으로 10개
    
    details = []
    
    for analysis in analyses:
        # 원본 데이터 찾기
        title = ""
        source = ""
        
        if analysis.content_type == 'raw_data':
            try:
                raw_data = RawData.objects.get(id=analysis.content_id)
                title = raw_data.title or raw_data.content[:50]
                source = f"{raw_data.get_category_display()}"
            except RawData.DoesNotExist:
                continue
                
        elif analysis.content_type == 'district_announcement':
            try:
                announcement = DistrictAnnouncement.objects.get(id=analysis.content_id)
                title = announcement.title[:50]
                source = "구청 공지사항"
            except DistrictAnnouncement.DoesNotExist:
                continue
                
        elif analysis.content_type == 'local_issue':
            try:
                issue = LocalIssue.objects.get(id=analysis.content_id)
                title = issue.title[:50]
                source = f"{issue.get_source_display()}"
            except LocalIssue.DoesNotExist:
                continue
        
        # 영향도 계산 (신뢰도 * 감성 가중치)
        sentiment_weight = 1 if analysis.sentiment == 'positive' else -1 if analysis.sentiment == 'negative' else 0
        impact = round(analysis.confidence * sentiment_weight * 10, 1)  # 10도 만점으로 스케일링
        
        details.append({
            'title': title,
            'source': source,
            'sentiment': analysis.sentiment,
            'confidence': analysis.confidence,
            'impact': impact,
            'keywords': analysis.keywords[:3]  # 상위 3개 키워드만
        })
    
    return JsonResponse({'details': details})

def settings_view(request):
    """설정 화면 뷰"""
    if request.method == 'POST':
        # 설정 저장
        district = request.POST.get('district')
        if district:
            request.session['district'] = district
        
        # 카테고리 설정 저장
        categories = {
            'weather': request.POST.get('weather') == 'on',
            'community': request.POST.get('community') == 'on',
            'restaurants': request.POST.get('restaurants') == 'on',
            'new_restaurants': request.POST.get('new_restaurants') == 'on',
        }
        request.session['categories'] = categories
        
        # 알림 설정
        request.session['notification_time'] = request.POST.get('notification_time', '07:00')
        request.session['weekend_notifications'] = request.POST.get('weekend_notifications') == 'on'
        
        return render(request, 'settings.html', {
            'success': True,
            'district': district or request.session.get('district', '강남구'),
            'categories': categories,
            'notification_time': request.session.get('notification_time', '07:00'),
            'weekend_notifications': request.session.get('weekend_notifications', True)
        })
    
    # GET 요청 - 설정 화면 표시
    return render(request, 'settings.html', {
        'district': request.session.get('district', '강남구'),
        'categories': request.session.get('categories', {
            'weather': True,
            'community': True, 
            'restaurants': True,
            'new_restaurants': True
        }),
        'notification_time': request.session.get('notification_time', '07:00'),
        'weekend_notifications': request.session.get('weekend_notifications', True)
    })

def onboarding_view(request):
    """온보딩 화면 뷰"""
    return render(request, 'onboarding.html')