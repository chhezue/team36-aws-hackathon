from django.core.management.base import BaseCommand
from local_data.models import Location

class Command(BaseCommand):
    help = '모든 서울시 구 데이터 로드'
    
    def handle(self, *args, **options):
        seoul_districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
            '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        created_count = 0
        for district in seoul_districts:
            location, created = Location.objects.get_or_create(gu=district)
            if created:
                created_count += 1
                self.stdout.write(f"✓ {district} 생성")
            else:
                self.stdout.write(f"- {district} 이미 존재")
        
        self.stdout.write(
            self.style.SUCCESS(f"완료: {created_count}개 새 지역 생성, 총 {Location.objects.count()}개 지역")
        )