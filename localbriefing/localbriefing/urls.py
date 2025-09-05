from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from restaurants.views import get_restaurant_data

# 서울시 구/동 데이터
SEOUL_DISTRICTS = {
    '강남구': ['역삼동', '삼성동', '청담동', '대치동', '신사동', '논현동', '압구정동', '개포동', '세곡동', '자곡동', '율현동', '일원동', '수서동', '도곡동'],
    '강동구': ['강일동', '고덕동', '길동', '둔촌동', '명일동', '상일동', '성내동', '암사동', '천호동'],
    '강북구': ['미아동', '번동', '수유동', '우이동'],
    '강서구': ['가양동', '개화동', '공항동', '과해동', '내발산동', '등촌동', '마곡동', '방화동', '염창동', '오곡동', '오쇠동', '외발산동', '화곡동'],
    '관악구': ['남현동', '대학동', '도림동', '보라매동', '삼성동', '서원동', '성현동', '신림동', '인헌동', '조원동', '중앙동', '청림동', '청룡동', '행운동'],
    '광진구': ['광장동', '구의동', '군자동', '능동', '자양동', '중곡동', '화양동'],
    '구로구': ['가리봉동', '개봉동', '고척동', '구로동', '궁동', '신도림동', '오류동', '온수동', '천왕동', '항동'],
    '금천구': ['가산동', '독산동', '시흥동'],
    '노원구': ['공릉동', '상계동', '월계동', '중계동', '하계동'],
    '도봉구': ['도봉동', '방학동', '쌍문동', '창동'],
    '동대문구': ['답십리동', '신설동', '용두동', '제기동', '전농동', '청량리동', '회기동', '휘경동', '이문동', '장안동'],
    '동작구': ['노량진동', '대방동', '사당동', '상도동', '신대방동', '흑석동'],
    '마포구': ['공덕동', '구수동', '노고산동', '대흥동', '도화동', '마포동', '망원동', '상암동', '상수동', '서강동', '서교동', '성산동', '신공덕동', '신수동', '아현동', '연남동', '염리동', '용강동', '토정동', '하중동', '합정동', '현석동'],
    '서대문구': ['남가좌동', '냉천동', '대신동', '대현동', '미근동', '봉원동', '북가좌동', '북아현동', '신촌동', '연희동', '영천동', '옥천동', '창천동', '천연동', '충정로동', '홍은동', '홍제동'],
    '서초구': ['내곡동', '반포동', '방배동', '서초동', '신원동', '양재동', '염곡동', '원지동', '잠원동'],
    '성동구': ['금호동', '마장동', '사근동', '성수동', '송정동', '용답동', '왕십리동', '홍익동'],
    '성북구': ['길음동', '돈암동', '동선동', '보문동', '삼선동', '상월곡동', '석관동', '성북동', '안암동', '월곡동', '정릉동', '종암동', '하월곡동'],
    '송파구': ['가락동', '거여동', '마천동', '문정동', '방이동', '삼전동', '석촌동', '송파동', '신천동', '오금동', '오륜동', '잠실동', '장지동', '풍납동'],
    '양천구': ['목동', '신월동', '신정동'],
    '영등포구': ['당산동', '대림동', '도림동', '문래동', '신길동', '양평동', '여의도동', '영등포동'],
    '용산구': ['남영동', '보광동', '서빙고동', '용산동', '원효로동', '이촌동', '이태원동', '청파동', '한강로동', '한남동', '효창동', '후암동'],
    '은평구': ['갈현동', '구산동', '녹번동', '대조동', '불광동', '수색동', '신사동', '역촌동', '응암동', '증산동', '진관동'],
    '종로구': ['가회동', '교남동', '궁정동', '관수동', '관철동', '관훈동', '구기동', '권농동', '견지동', '계동', '고산동', '공평동', '광화문동', '국궁동', '궁정동', '금융동', '낙원동', '내수동', '내자동', '누상동', '누하동', '다동', '당주동', '도렴동', '돈의동', '동숭동', '명륜동', '묘동', '무악동', '봉익동', '부암동', '사간동', '사직동', '삼청동', '서린동', '세종로', '소격동', '송월동', '수송동', '숭인동', '신교동', '신영동', '안국동', '연건동', '연지동', '예지동', '옥인동', '와룡동', '운니동', '원서동', '원남동', '이화동', '인사동', '익선동', '인의동', '장사동', '재동', '적선동', '종로동', '중학동', '창신동', '청운동', '체부동', '충신동', '탑동', '통의동', '통인동', '팔판동', '평동', '평창동', '필운동', '행촌동', '혜화동', '홍지동', '홍파동', '화동', '훈정동'],
    '중구': ['광희동', '남산동', '남창동', '다산동', '동화동', '립정동', '명동', '무학동', '방산동', '봉래동', '산림동', '삼각동', '소공동', '수표동', '신당동', '쌍림동', '예관동', '예장동', '오장동', '을지로동', '의주로동', '인현동', '입정동', '장교동', '장충동', '저동', '정동', '주자동', '중림동', '충무로동', '태평로동', '필동', '황학동', '회현동', '흥인동'],
    '중랑구': ['면목동', '망우동', '상봉동', '신내동', '중화동']
}

@csrf_exempt
def get_districts(request):
    return JsonResponse({'districts': list(SEOUL_DISTRICTS.keys())})

@csrf_exempt
def get_dongs(request):
    district = request.GET.get('district')
    if district in SEOUL_DISTRICTS:
        return JsonResponse({'dongs': SEOUL_DISTRICTS[district]})
    return JsonResponse({'dongs': []})

def onboarding_view(request):
    return render(request, 'onboarding.html')

def briefing_view(request):
    # 실제 음식점 데이터 가져오기
    try:
        restaurant_data = get_restaurant_data('강남구')
        
        # 신설 음식점 포맷팅
        new_restaurants = []
        for r in restaurant_data['new_restaurants']:
            new_restaurants.append(f"{r['name']} ({r['license_date']})")
        
        # 인기 맛집 포맷팅
        popular_restaurants = []
        for r in restaurant_data['popular_restaurants']:
            popular_restaurants.append(f"{r['name']} ({r.get('category', '음식점')})")
            
    except Exception as e:
        error_msg = f"음식점 데이터 로딩 오류: {str(e)}"
        print(error_msg)
        new_restaurants = [error_msg]
        popular_restaurants = [error_msg]
    
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

        'new_restaurants': new_restaurants or ['신설 음식점 정보를 불러오는 중...'],
        'popular_restaurants': popular_restaurants or ['인기 맛집 정보를 불러오는 중...']
    }
    return render(request, 'briefing.html', briefing_data)

def settings_view(request):
    if request.method == 'POST':
        # 설정 업데이트 처리
        return JsonResponse({'status': 'success', 'message': '설정이 저장되었습니다.'})
    
    # 기본 설정 데이터
    settings_data = {
        'user_email': 'user@example.com',
        'district': '강남구',
        'dong': '역삼동',
        'notification_time': '07:00',
        'weekend_notifications': True,
        'categories': {
            'weather': True,
            'district_news': True,
            'community': True,
            'secondhand': False,
            'restaurants': True
        }
    }
    return render(request, 'settings.html', settings_data)

def glassmorphism_demo_view(request):
    return render(request, 'glassmorphism_demo.html')

def glassmorphism_login_view(request):
    return render(request, 'glassmorphism_login.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', onboarding_view, name='onboarding'),
    path('briefing/', briefing_view, name='briefing'),
    path('settings/', settings_view, name='settings'),
    path('glassmorphism/', glassmorphism_demo_view, name='glassmorphism_demo'),
    path('login/', glassmorphism_login_view, name='glassmorphism_login'),
    path('users/', include('users.urls')),
    path('api/districts/', get_districts, name='get_districts'),
    path('api/dongs/', get_dongs, name='get_dongs'),
]