import requests
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.conf import settings
from .models import User, Location, LocalIssue
from datetime import datetime, date, timedelta
from django.utils import timezone

def kakao_login(request):
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}&redirect_uri=http://127.0.0.1:8000/users/kakao/callback/&response_type=code"
    return redirect(kakao_auth_url)

def naver_login(request):
    naver_auth_url = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={settings.NAVER_CLIENT_ID}&redirect_uri=http://127.0.0.1:8000/users/naver/callback/&state=random_state"
    return redirect(naver_auth_url)

def kakao_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('/')
    
    # 액세스 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.KAKAO_CLIENT_ID,
        'redirect_uri': 'http://127.0.0.1:8000/users/kakao/callback/',
        'code': code,
    }
    
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return redirect('/')
    
    # 사용자 정보 요청
    user_url = "https://kapi.kakao.com/v2/user/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(user_url, headers=headers)
    user_data = user_response.json()
    
    kakao_id = user_data.get('id')
    email = user_data.get('kakao_account', {}).get('email', f'kakao_{kakao_id}@kakao.com')
    nickname = user_data.get('properties', {}).get('nickname', f'카카오사용자{kakao_id}')
    
    # 사용자 생성 또는 로그인
    user, created = User.objects.get_or_create(
        username=f'kakao_{kakao_id}',
        defaults={
            'email': email,
            'first_name': nickname,
        }
    )
    
    login(request, user)
    return redirect('/briefing/')

def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        return redirect('/')
    
    # 액세스 토큰 요청
    token_url = "https://nid.naver.com/oauth2.0/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.NAVER_CLIENT_ID,
        'client_secret': settings.NAVER_CLIENT_SECRET,
        'redirect_uri': 'http://127.0.0.1:8000/users/naver/callback/',
        'code': code,
        'state': state,
    }
    
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return redirect('/')
    
    # 사용자 정보 요청
    user_url = "https://openapi.naver.com/v1/nid/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(user_url, headers=headers)
    user_data = user_response.json()
    
    response_data = user_data.get('response', {})
    naver_id = response_data.get('id')
    email = response_data.get('email', f'naver_{naver_id}@naver.com')
    name = response_data.get('name', f'네이버사용자{naver_id}')
    
    # 사용자 생성 또는 로그인
    user, created = User.objects.get_or_create(
        username=f'naver_{naver_id}',
        defaults={
            'email': email,
            'first_name': name,
        }
    )
    
    login(request, user)
    return redirect('/briefing/')

def email_login(request):
    return redirect('/briefing/')

@csrf_exempt
def set_user_location(request):
    """사용자 거주지 설정 API"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        gu_name = data.get('gu')
        
        if gu_name:
            # Location 객체 생성 또는 조회
            location, created = Location.objects.get_or_create(gu=gu_name)
            
            # 세션에 임시 저장 (로그인 전)
            request.session['selected_location'] = gu_name
            
            # 로그인된 사용자인 경우 바로 저장
            if request.user.is_authenticated:
                request.user.location = location
                request.user.save()
            
            return JsonResponse({'success': True, 'location': gu_name})
    
    return JsonResponse({'success': False})

@csrf_exempt
def complete_onboarding(request):
    """온보딩 완료 처리"""
    if request.method == 'POST':
        # 세션에서 선택된 위치 정보 가져오기
        selected_location = request.session.get('selected_location')
        
        if selected_location and request.user.is_authenticated:
            location, created = Location.objects.get_or_create(gu=selected_location)
            request.user.location = location
            request.user.save()
            
            # 세션 정리
            if 'selected_location' in request.session:
                del request.session['selected_location']
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def briefing_view(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=== 브리핑 뷰 시작 ===")
    
    # 사용자 위치 정보 가져오기
    user_location = '강남구'  # 기본값
    user_name = '김철수'  # 기본값
    
    if request.user.is_authenticated:
        # 로그인된 사용자의 위치 정보
        if hasattr(request.user, 'location') and request.user.location:
            user_location = request.user.location.gu
        
        # 사용자 이름 설정
        if request.user.first_name:
            user_name = request.user.first_name
        elif request.user.username:
            user_name = request.user.username
    else:
        # 비로그인 사용자의 경우 세션에서 위치 정보 가져오기
        session_location = request.session.get('selected_location')
        if session_location:
            user_location = session_location
    
    logger.info(f"사용자 위치: {user_location}, 사용자명: {user_name}")
    
    # 실제 음식점 데이터 가져오기
    try:
        from restaurants.views import get_restaurant_data
        restaurant_data = get_restaurant_data(user_location)
        new_restaurants = restaurant_data.get('new_restaurants', [])
        popular_restaurants = restaurant_data.get('popular_restaurants', [])
        
        logger.info(f"브리핑에서 받은 데이터: 신설 {len(new_restaurants)}개, 인기 {len(popular_restaurants)}개")
        
    except Exception as e:
        logger.error(f"음식점 데이터 로딩 오류: {str(e)}")
        new_restaurants = []
        popular_restaurants = []
    
    # 실제 날씨 데이터 가져오기
    try:
        from .weather_service import WeatherService
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_by_location(user_location)
        logger.info(f"날씨 데이터 로딩 성공: {user_location}")
    except Exception as e:
        logger.error(f"날씨 데이터 로딩 오류: {str(e)}")
        weather_data = {
            'temp': '18°C',
            'condition': '맑음',
            'dust': '보통',
            'description': '외출하기 좋은 날씨예요'
        }
    
    # 사용자 위치 객체 가져오기
    try:
        location = Location.objects.get(gu=user_location)
    except Location.DoesNotExist:
        location = Location.objects.create(gu=user_location)
    
    # 7일 이내 데이터만 조회
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # 소스별로 동네 이슈 데이터 조회 (최대 5개, 7일 이내)
    youtube_issues = LocalIssue.objects.filter(
        location=location, source='youtube', 
        collected_at__gte=seven_days_ago,
        published_at__gte=seven_days_ago
    ).order_by('-view_count', '-collected_at')[:5]
    
    naver_search_issues = LocalIssue.objects.filter(
        location=location, source='naver_search', 
        collected_at__gte=seven_days_ago,
        published_at__gte=seven_days_ago
    ).order_by('-collected_at')[:5]
    
    naver_news_issues = LocalIssue.objects.filter(
        location=location, source='naver_news', 
        collected_at__gte=seven_days_ago,
        published_at__gte=seven_days_ago
    ).order_by('-collected_at')[:5]
    
    briefing_data = {
        'user_name': user_name,
        'location': f'{user_location} 역삼동',
        'date': datetime.now().strftime('%Y년 %m월 %d일 %A'),
        'weather': weather_data,
        'district_news': [
            '역삼동 도서관 리모델링 완료',
            '3월 말까지 무료 독감 예방접종',
            '어린이집 입소 대기자 모집'
        ],
        'new_restaurants': new_restaurants,
        'popular_restaurants': popular_restaurants,
        'local_issues': {
            'youtube': youtube_issues,
            'naver_search': naver_search_issues,
            'naver_news': naver_news_issues,
        }
    }
    
    print(f"템플릿 전달 데이터: 신장 {len(new_restaurants)}개, 인기 {len(popular_restaurants)}개")
    if new_restaurants:
        print(f"신장 첫번째: {new_restaurants[0]['name']}")
    if popular_restaurants:
        print(f"인기 첫번째: {popular_restaurants[0]['name']}")
    
    logger.info("브리핑 데이터 준비 완료")
    return render(request, 'briefing.html', briefing_data)