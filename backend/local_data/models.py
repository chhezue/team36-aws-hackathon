from django.db import models

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

class LocalIssue(models.Model):
    SOURCE_CHOICES = [
        ('youtube', '유튜브'),
        ('naver_search', '네이버 검색'),
        ('naver_news', '네이버 뉴스'),
        ('instagram', '인스타그램'),
        ('community', '커뮤니티'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="출처")
    title = models.TextField(verbose_name="제목")
    url = models.CharField(max_length=200, verbose_name="원본 URL")
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="게시일시")
    collected_at = models.DateTimeField(auto_now_add=True, verbose_name="수집일시")
    
    class Meta:
        db_table = 'local_issues'
        indexes = [
            models.Index(fields=['location', 'source', 'collected_at']),
            models.Index(fields=['view_count']),
        ]
        verbose_name = "동네 이슈"
        verbose_name_plural = "동네 이슈들"
    
    def __str__(self):
        return f"{self.location} - {self.title[:50]}"

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

class SentimentAnalysis(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', '긍정'),
        ('negative', '부정'),
        ('neutral', '중립'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    content_type = models.CharField(max_length=50, verbose_name="콘텐츠 타입")
    content_id = models.PositiveIntegerField(verbose_name="콘텐츠 ID")
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, verbose_name="감성")
    confidence = models.FloatField(verbose_name="신뢰도")
    keywords = models.JSONField(default=list, verbose_name="추출 키워드")
    analyzed_at = models.DateTimeField(auto_now_add=True, verbose_name="분석일시")
    
    class Meta:
        db_table = 'sentiment_analysis'
        indexes = [
            models.Index(fields=['location', 'sentiment', 'analyzed_at']),
            models.Index(fields=['content_type', 'content_id']),
        ]
        unique_together = ['content_type', 'content_id']
        verbose_name = "감성 분석"
        verbose_name_plural = "감성 분석들"
    
    def __str__(self):
        return f"{self.location} - {self.get_sentiment_display()} ({self.confidence:.2f})"

class SentimentSummary(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    date = models.DateField(verbose_name="날짜")
    positive_count = models.IntegerField(default=0, verbose_name="긍정 개수")
    negative_count = models.IntegerField(default=0, verbose_name="부정 개수")
    neutral_count = models.IntegerField(default=0, verbose_name="중립 개수")
    sentiment_score = models.FloatField(default=0.0, verbose_name="감성 점수")
    top_keywords = models.JSONField(default=dict, verbose_name="주요 키워드")
    
    class Meta:
        db_table = 'sentiment_summary'
        unique_together = ['location', 'date']
        indexes = [
            models.Index(fields=['location', 'date']),
        ]
        verbose_name = "감성 요약"
        verbose_name_plural = "감성 요약들"
    
    def __str__(self):
        return f"{self.location} - {self.date} (점수: {self.sentiment_score:.2f})"
    
    @property
    def total_count(self):
        return self.positive_count + self.negative_count + self.neutral_count
    
    @property
    def positive_ratio(self):
        return (self.positive_count / self.total_count * 100) if self.total_count > 0 else 0
    
    @property
    def negative_ratio(self):
        return (self.negative_count / self.total_count * 100) if self.total_count > 0 else 0