from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse

def onboarding_view(request):
    return render(request, 'onboarding.html')

def briefing_view(request):
    # 목업 데이터
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
        'community_issues': [
            '역삼역 근처 공사로 교통 혼잡',
            '새로 생긴 카페 후기 좋음',
            '반려동물 실종 제보 급증'
        ],
        'secondhand': [
            '아이폰 케이스 나눔',
            '공기청정기 저렴하게',
            '유아용품 일괄 판매'
        ],
        'restaurants': [
            '역삼동 새 파스타집 오픈',
            '24시간 족발집 인기',
            '디저트 카페 할인 이벤트'
        ]
    }
    return render(request, 'briefing.html', briefing_data)

def settings_view(request):
    return render(request, 'settings.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', onboarding_view, name='onboarding'),
    path('briefing/', briefing_view, name='briefing'),
    path('settings/', settings_view, name='settings'),
]