import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from users.models import Location, RawData, DistrictAnnouncement, LocalIssue, SentimentAnalysis
from users.sentiment_analyzer import SimpleSentimentAnalyzer, update_sentiment_summary

class Command(BaseCommand):
    help = '크롤링된 데이터의 감성 분석 실행'
    
    def add_arguments(self, parser):
        parser.add_argument('--location', type=str, help='분석할 지역명 (예: 강남구)')
        parser.add_argument('--days', type=int, default=7, help='분석할 일수 (기본: 7일)')
    
    def handle(self, *args, **options):
        analyzer = SimpleSentimentAnalyzer()
        
        # 지역 필터링
        locations = Location.objects.all()
        if options['location']:
            locations = locations.filter(gu=options['location'])
        
        # 날짜 범위 설정
        end_date = date.today()
        start_date = end_date - timedelta(days=options['days'])
        
        for location in locations:
            self.stdout.write(f"\n=== {location.gu} 감성 분석 시작 ===")
            
            analyzed_count = 0
            
            # 1. RawData 분석
            raw_data_items = RawData.objects.filter(
                location=location,
                collected_at__date__gte=start_date,
                processed=False
            )
            
            for item in raw_data_items:
                # 이미 분석된 데이터는 스킵
                if SentimentAnalysis.objects.filter(
                    content_type='raw_data',
                    content_id=item.id
                ).exists():
                    continue
                
                # 제목과 내용 합쳐서 분석
                text = f"{item.title} {item.content}"
                result = analyzer.analyze_text(text)
                
                # 분석 결과 저장
                SentimentAnalysis.objects.create(
                    location=location,
                    content_type='raw_data',
                    content_id=item.id,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    keywords=result['keywords']
                )
                
                analyzed_count += 1
            
            # 2. DistrictAnnouncement 분석
            announcements = DistrictAnnouncement.objects.filter(
                location=location,
                collected_at__date__gte=start_date
            )
            
            for announcement in announcements:
                if SentimentAnalysis.objects.filter(
                    content_type='district_announcement',
                    content_id=announcement.id
                ).exists():
                    continue
                
                text = f"{announcement.title} {announcement.content}"
                result = analyzer.analyze_text(text)
                
                SentimentAnalysis.objects.create(
                    location=location,
                    content_type='district_announcement',
                    content_id=announcement.id,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    keywords=result['keywords']
                )
                
                analyzed_count += 1
            
            # 3. LocalIssue 분석
            issues = LocalIssue.objects.filter(
                location=location,
                collected_at__date__gte=start_date
            )
            
            for issue in issues:
                if SentimentAnalysis.objects.filter(
                    content_type='local_issue',
                    content_id=issue.id
                ).exists():
                    continue
                
                result = analyzer.analyze_text(issue.title)
                
                SentimentAnalysis.objects.create(
                    location=location,
                    content_type='local_issue',
                    content_id=issue.id,
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    keywords=result['keywords']
                )
                
                analyzed_count += 1
            
            # 4. 일별 감성 요약 업데이트
            for i in range(options['days']):
                target_date = end_date - timedelta(days=i)
                summary = update_sentiment_summary(location, target_date)
                
                if summary.total_count > 0:
                    self.stdout.write(
                        f"  {target_date}: {summary.mood_emoji} "
                        f"긍정 {summary.positive_ratio:.1f}% "
                        f"부정 {summary.negative_ratio:.1f}% "
                        f"(총 {summary.total_count}건)"
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f"{location.gu} 완료: {analyzed_count}건 분석")
            )
        
        self.stdout.write(
            self.style.SUCCESS("\n감성 분석 완료!")
        )