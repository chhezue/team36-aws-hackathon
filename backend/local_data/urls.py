from django.urls import path
from . import views

urlpatterns = [
    path('briefing/', views.briefing_view, name='briefing'),
    path('set-location/', views.set_user_location, name='set_user_location'),
    path('complete-onboarding/', views.complete_onboarding, name='complete_onboarding'),
    path('theme-selector/', views.theme_selector, name='theme_selector'),
    path('sentiment/', views.sentiment_dashboard, name='sentiment_dashboard'),
    path('sentiment/<int:location_id>/', views.sentiment_dashboard, name='sentiment_dashboard_location'),
    path('api/sentiment/<int:location_id>/', views.sentiment_api, name='sentiment_api'),
    path('api/sentiment/<int:location_id>/details/', views.sentiment_details_api, name='sentiment_details_api'),
    path('settings/', views.settings_view, name='settings'),
    path('', views.onboarding_view, name='onboarding'),
]