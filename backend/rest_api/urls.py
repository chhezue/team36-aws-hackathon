from django.urls import path
from .views.briefing import get_briefing
from .views.location import get_districts
from .views.sentiment import get_sentiment_summary
from .views.weather import get_weather

urlpatterns = [
    path('briefing/', get_briefing, name='get_briefing'),
    path('location/districts/', get_districts, name='get_districts'),
    path('sentiment/summary/', get_sentiment_summary, name='get_sentiment_summary'),
    path('weather/', get_weather, name='get_weather'),
]