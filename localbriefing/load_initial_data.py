import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localbriefing.settings')
django.setup()

from users.models import Location

# 서울시 25개 구 데이터
districts = [
    '강남구', '강동구', '강북구', '강서구', '관악구',
    '광진구', '구로구', '금천구', '노원구', '도봉구',
    '동대문구', '동작구', '마포구', '서대문구', '서초구',
    '성동구', '성북구', '송파구', '양천구', '영등포구',
    '용산구', '은평구', '종로구', '중구', '중랑구'
]

for district in districts:
    location, created = Location.objects.get_or_create(gu=district)
    if created:
        print(f"Created: {district}")
    else:
        print(f"Already exists: {district}")

print("Initial data loading completed!")