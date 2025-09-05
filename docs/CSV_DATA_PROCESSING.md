# LocalBriefing CSV 데이터 처리 가이드

## 개요

이 문서는 강남구에서 제공하는 실제 CSV 데이터를 LocalBriefing 시스템에 통합하는 방법을 설명합니다. 현재 `data/gangnam/` 폴더에 있는 4개의 CSV 파일을 분석하고 처리하는 방법을 제시합니다.

---

## 1. 사용 가능한 CSV 데이터

### 1.1 강남구 공지사항 및 행사정보
**파일**: `서울시강남구공지사항및행사정보.csv`

**주요 컬럼**:
- `게시판종류`: 행사정보, 공지사항 등
- `게시물번호`: 고유 게시물 ID
- `제목`: 공지사항/행사 제목
- `내용`: HTML 형태의 상세 내용
- `조회수`: 게시물 조회수
- `작성자`: 작성자명
- `부서명`: 담당 부서
- `등록일시`: 게시물 등록 시간

**활용 방안**:
- 구청 공지사항 카테고리의 주요 데이터 소스
- AI 요약을 통해 주민들에게 중요한 정책 및 행사 정보 제공

### 1.2 음식점 인허가 정보 (3개 파일)
**파일들**:
- `서울시강남구일반음식점인허가정보.csv`
- `서울시강남구제과점영업인허가정보.csv`
- `서울시강남구휴게음식점인허가정보.csv`

**주요 컬럼**:
- `관리번호`: 고유 사업장 식별자
- `인허가일자`: 영업 허가 받은 날짜
- `영업상태코드/명`: 현재 영업 상태
- `사업장명`: 음식점 이름
- `전화번호`: 연락처
- `소재지면적`: 매장 면적
- `도로명주소`, `지번주소`: 위치 정보
- `좌표(X,Y)`: 지리적 좌표

**활용 방안**:
- 새로운 맛집 카테고리의 데이터 소스
- 최근 인허가 받은 음식점을 "신규 오픈" 정보로 활용
- 지역별 음식점 분포 및 트렌드 분석

---

## 2. Django 모델 매핑

### 2.1 DistrictAnnouncement 모델
```python
class DistrictAnnouncement(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    board_type = models.CharField(max_length=50, blank=True)  # 게시판종류
    post_number = models.CharField(max_length=20, blank=True)  # 게시물번호
    title = models.TextField()  # 제목
    content = models.TextField(blank=True)  # 내용
    view_count = models.IntegerField(default=0)  # 조회수
    author = models.CharField(max_length=100, blank=True)  # 작성자
    department = models.CharField(max_length=100, blank=True)  # 부서명
    created_at = models.DateTimeField(null=True, blank=True)  # 등록일시
    collected_at = models.DateTimeField(auto_now_add=True)
```

### 2.2 RestaurantInfo 모델
```python
class RestaurantInfo(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('general', '일반음식점'),
        ('bakery', '제과점'),
        ('cafe', '휴게음식점'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    management_number = models.CharField(max_length=50, unique=True)  # 관리번호
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    license_date = models.DateField(null=True, blank=True)  # 인허가일자
    business_status_code = models.CharField(max_length=10, blank=True)  # 영업상태코드
    business_status_name = models.CharField(max_length=50, blank=True)  # 영업상태명
    business_name = models.CharField(max_length=200, blank=True)  # 사업장명
    phone_number = models.CharField(max_length=20, blank=True)  # 전화번호
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 소재지면적
    postal_code = models.CharField(max_length=10, blank=True)  # 우편번호
    road_address = models.TextField(blank=True)  # 도로명주소
    lot_address = models.TextField(blank=True)  # 지번주소
    coordinate_x = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    coordinate_y = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
```

---

## 3. CSV 데이터 처리 구현

### 3.1 CSV 수집기 클래스
```python
# briefings/collectors/csv_collector.py
import csv
import os
from datetime import datetime
from django.conf import settings
from briefings.models import DistrictAnnouncement, RestaurantInfo, Location

class CSVCollector:
    def __init__(self):
        self.data_path = os.path.join(settings.BASE_DIR, 'data', 'gangnam')
        self.gangnam_location = Location.objects.get_or_create(
            gu='강남구', 
            defaults={'dong': '전체', 'gu_code': '3220000'}
        )[0]
    
    def collect_district_announcements(self):
        """강남구 공지사항 및 행사정보 수집"""
        file_path = os.path.join(self.data_path, '서울시강남구공지사항및행사정보.csv')
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # 중복 체크
                if not DistrictAnnouncement.objects.filter(
                    post_number=row['게시물번호']
                ).exists():
                    
                    # 등록일시 파싱
                    created_at = None
                    if row['등록일시']:
                        try:
                            created_at = datetime.strptime(
                                row['등록일시'], '%Y-%m-%d %H:%M:%S.%f'
                            )
                        except ValueError:
                            pass
                    
                    DistrictAnnouncement.objects.create(
                        location=self.gangnam_location,
                        board_type=row['게시판종류'],
                        post_number=row['게시물번호'],
                        title=row['제목'],
                        content=row['내용'],
                        view_count=int(row['조회수']) if row['조회수'] else 0,
                        author=row['작성자'],
                        department=row['부서명'],
                        created_at=created_at
                    )
    
    def collect_restaurant_info(self):
        """음식점 인허가 정보 수집"""
        restaurant_files = [
            ('서울시강남구일반음식점인허가정보.csv', 'general'),
            ('서울시강남구제과점영업인허가정보.csv', 'bakery'),
            ('서울시강남구휴게음식점인허가정보.csv', 'cafe'),
        ]
        
        for filename, business_type in restaurant_files:
            file_path = os.path.join(self.data_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # 중복 체크
                    if not RestaurantInfo.objects.filter(
                        management_number=row['관리번호']
                    ).exists():
                        
                        # 인허가일자 파싱
                        license_date = None
                        if row['인허가일자']:
                            try:
                                license_date = datetime.strptime(
                                    row['인허가일자'], '%Y-%m-%d'
                                ).date()
                            except ValueError:
                                pass
                        
                        # 좌표 파싱
                        coord_x = None
                        coord_y = None
                        try:
                            if row['소재지좌표(X)']:
                                coord_x = float(row['소재지좌표(X)'])
                            if row['소재지좌표(Y)']:
                                coord_y = float(row['소재지좌표(Y)'])
                        except (ValueError, KeyError):
                            pass
                        
                        # 면적 파싱
                        area_size = None
                        try:
                            if row['소재지면적']:
                                area_size = float(row['소재지면적'])
                        except (ValueError, KeyError):
                            pass
                        
                        RestaurantInfo.objects.create(
                            location=self.gangnam_location,
                            management_number=row['관리번호'],
                            business_type=business_type,
                            license_date=license_date,
                            business_status_code=row['영업상태코드'],
                            business_status_name=row['영업상태명'],
                            business_name=row.get('사업장명', ''),
                            phone_number=row.get('전화번호', ''),
                            area_size=area_size,
                            postal_code=row.get('우편번호', ''),
                            road_address=row.get('도로명주소', ''),
                            lot_address=row.get('지번주소', ''),
                            coordinate_x=coord_x,
                            coordinate_y=coord_y
                        )
    
    def collect_all(self):
        """모든 CSV 데이터 수집"""
        print("강남구 공지사항 수집 중...")
        self.collect_district_announcements()
        
        print("음식점 정보 수집 중...")
        self.collect_restaurant_info()
        
        print("CSV 데이터 수집 완료!")
```

### 3.2 Django Management Command
```python
# briefings/management/commands/import_csv_data.py
from django.core.management.base import BaseCommand
from briefings.collectors.csv_collector import CSVCollector

class Command(BaseCommand):
    help = 'Import CSV data from Gangnam-gu'
    
    def handle(self, *args, **options):
        collector = CSVCollector()
        collector.collect_all()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported CSV data')
        )
```

---

## 4. AI 요약을 위한 데이터 전처리

### 4.1 공지사항 요약 처리
```python
def process_announcements_for_ai(self):
    """공지사항을 AI 요약용으로 전처리"""
    from bs4 import BeautifulSoup
    
    recent_announcements = DistrictAnnouncement.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:10]
    
    processed_data = []
    for announcement in recent_announcements:
        # HTML 태그 제거
        soup = BeautifulSoup(announcement.content, 'html.parser')
        clean_content = soup.get_text().strip()
        
        # 요약용 텍스트 생성
        summary_text = f"""
        제목: {announcement.title}
        부서: {announcement.department}
        내용: {clean_content[:500]}...
        """
        
        processed_data.append({
            'category': 'district_news',
            'title': announcement.title,
            'content': summary_text,
            'source': f"강남구청 {announcement.board_type}"
        })
    
    return processed_data
```

### 4.2 신규 음식점 정보 처리
```python
def process_new_restaurants_for_ai(self):
    """최근 개업한 음식점 정보를 AI 요약용으로 전처리"""
    # 최근 30일 내 인허가 받은 음식점
    recent_restaurants = RestaurantInfo.objects.filter(
        license_date__gte=timezone.now().date() - timedelta(days=30),
        business_status_code='01'  # 영업중
    ).order_by('-license_date')[:15]
    
    processed_data = []
    for restaurant in recent_restaurants:
        summary_text = f"""
        새로 오픈한 {restaurant.get_business_type_display()}: {restaurant.business_name}
        위치: {restaurant.road_address}
        연락처: {restaurant.phone_number}
        개업일: {restaurant.license_date}
        """
        
        processed_data.append({
            'category': 'restaurants',
            'title': f"신규 오픈: {restaurant.business_name}",
            'content': summary_text,
            'source': "강남구 인허가 정보"
        })
    
    return processed_data
```

---

## 5. 실행 방법

### 5.1 초기 데이터 임포트
```bash
# CSV 데이터 임포트
python manage.py import_csv_data

# 데이터 확인
python manage.py shell
>>> from briefings.models import DistrictAnnouncement, RestaurantInfo
>>> print(f"공지사항: {DistrictAnnouncement.objects.count()}개")
>>> print(f"음식점: {RestaurantInfo.objects.count()}개")
```

### 5.2 정기적 업데이트
```python
# 일일 배치 작업에 포함
def daily_csv_update():
    collector = CSVCollector()
    collector.collect_all()
    
    # AI 요약 처리
    announcements = collector.process_announcements_for_ai()
    restaurants = collector.process_new_restaurants_for_ai()
    
    # Bedrock으로 요약 생성
    # ... AI 처리 로직
```

이 가이드를 통해 실제 강남구 CSV 데이터를 LocalBriefing 시스템에 효과적으로 통합할 수 있습니다.