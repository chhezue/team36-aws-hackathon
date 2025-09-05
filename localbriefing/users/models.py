from django.db import models
from django.contrib.auth.models import AbstractUser

class Location(models.Model):
    gu = models.CharField(max_length=50, verbose_name="구")
    gu_code = models.CharField(max_length=10, blank=True, verbose_name="구 코드")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'locations'
        verbose_name = "지역"
        verbose_name_plural = "지역들"

    def __str__(self):
        return f"{self.gu}"

class User(AbstractUser):
    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="거주지"
    )

    class Meta:
        db_table = 'users'
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

class RawData(models.Model):
    CATEGORY_CHOICES = [
        ('weather', '날씨'),
        ('district_news', '구/동 공지사항'),
        ('community', '커뮤니티 이슈'),
        ('secondhand', '중고거래'),
        ('restaurants', '맛집'),
        ('local_news', '지역 뉴스'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    source_url = models.TextField(blank=True, verbose_name="출처 URL")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    title = models.TextField(blank=True, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    collected_at = models.DateTimeField(auto_now_add=True, verbose_name="수집일시")
    processed = models.BooleanField(default=False, verbose_name="처리 완료")

    class Meta:
        db_table = 'raw_data'
        indexes = [
            models.Index(fields=['location', 'category', 'collected_at']),
            models.Index(fields=['processed']),
        ]
        verbose_name = "원시 데이터"
        verbose_name_plural = "원시 데이터들"

    def __str__(self):
        return f"{self.location} - {self.category} - {self.collected_at.date()}"

class Briefing(models.Model):
    STATUS_CHOICES = [
        ('generating', '생성 중'),
        ('generated', '생성 완료'),
        ('failed', '생성 실패'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    date = models.DateField(verbose_name="브리핑 날짜")
    content = models.JSONField(verbose_name="브리핑 내용")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated', verbose_name="상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'briefings'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['location', 'date']),
        ]
        verbose_name = "브리핑"
        verbose_name_plural = "브리핑들"

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class DistrictAnnouncement(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    board_type = models.CharField(max_length=50, blank=True, verbose_name="게시판 종류")
    post_number = models.CharField(max_length=20, blank=True, verbose_name="게시물 번호")
    title = models.TextField(verbose_name="제목")
    content = models.TextField(blank=True, verbose_name="내용")
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    author = models.CharField(max_length=100, blank=True, verbose_name="작성자")
    department = models.CharField(max_length=100, blank=True, verbose_name="부서명")
    created_at = models.DateTimeField(null=True, blank=True, verbose_name="등록일시")
    collected_at = models.DateTimeField(auto_now_add=True, verbose_name="수집일시")

    class Meta:
        db_table = 'district_announcements'
        indexes = [
            models.Index(fields=['location', 'created_at']),
            models.Index(fields=['board_type']),
        ]
        verbose_name = "구청 공지사항"
        verbose_name_plural = "구청 공지사항들"

    def __str__(self):
        return f"{self.location} - {self.title[:50]}"

class RestaurantInfo(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('general', '일반음식점'),
        ('bakery', '제과점'),
        ('cafe', '휴게음식점'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    management_number = models.CharField(max_length=50, unique=True, verbose_name="관리번호")
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, verbose_name="업종")
    license_date = models.DateField(null=True, blank=True, verbose_name="인허가일자")
    business_status_code = models.CharField(max_length=10, blank=True, verbose_name="영업상태코드")
    business_status_name = models.CharField(max_length=50, blank=True, verbose_name="영업상태명")
    business_name = models.CharField(max_length=200, blank=True, verbose_name="사업장명")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="전화번호")
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="소재지면적")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="우편번호")
    road_address = models.TextField(blank=True, verbose_name="도로명주소")
    lot_address = models.TextField(blank=True, verbose_name="지번주소")
    coordinate_x = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True, verbose_name="X좌표")
    coordinate_y = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True, verbose_name="Y좌표")
    collected_at = models.DateTimeField(auto_now_add=True, verbose_name="수집일시")

    class Meta:
        db_table = 'restaurant_info'
        indexes = [
            models.Index(fields=['location', 'business_type']),
            models.Index(fields=['business_status_code']),
            models.Index(fields=['license_date']),
        ]
        verbose_name = "음식점 정보"
        verbose_name_plural = "음식점 정보들"

    def __str__(self):
        return f"{self.business_name} ({self.business_type})"