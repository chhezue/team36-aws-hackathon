import requests
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
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

def briefing_view(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=== 브리핑 뷰 시작 ===")
    
    # 실제 음식점 데이터 가져오기
    try:
        from restaurants.views import get_restaurant_data
        restaurant_data = get_restaurant_data('강남구')
        new_restaurants = restaurant_data.get('new_restaurants', [])
        popular_restaurants = restaurant_data.get('popular_restaurants', [])
        
        logger.info(f"브리핑에서 받은 데이터: 신설 {len(new_restaurants)}개, 인기 {len(popular_restaurants)}개")
        
    except Exception as e:
        logger.error(f"음식점 데이터 로딩 오류: {str(e)}")
        new_restaurants = []
        popular_restaurants = []
    
    # 기본 사용자 위치 (강남구)
    try:
        location = Location.objects.get(gu='강남구')
    except Location.DoesNotExist:
        location = Location.objects.create(gu='강남구')
    
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
        'user_name': '김철수',
        'location': '강남구 역삼동',
        'date': '2024년 3월 15일 금요일',
        'weather': {
            'condition': '맑음',
            'temp': '18°C',
            'dust': '보통',
            'description': '외출하기 좋은 날씨예요'
        },
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
    
    logger.info("브리핑 데이터 준비 완료")
    return render(request, 'briefing.html', briefing_data)