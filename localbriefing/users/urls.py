from django.urls import path
from . import views

urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('naver/login/', views.naver_login, name='naver_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),
    path('email/login/', views.email_login, name='email_login'),
    path('briefing/', views.briefing_view, name='briefing'),
]