import requests
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.conf import settings
from .models import User

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