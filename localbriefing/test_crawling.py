#!/usr/bin/env python
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localbriefing.settings')
django.setup()

from users.models import LocalIssue, Location
from users.crawlers import LocalIssueCrawler

def test_crawling():
    print("=== 동네 이슈 크롤링 테스트 ===")
    
    # 강남구 위치 확인/생성
    location, created = Location.objects.get_or_create(gu='강남구')
    if created:
        print("강남구 위치 생성됨")
    
    # 크롤링 실행
    crawler = LocalIssueCrawler()
    results = crawler.crawl_all('강남구')
    
    print(f"\n총 {len(results)}개 이슈 수집:")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['source']}] {result['title'][:50]}...")
        print(f"   URL: {result['url']}")
        print(f"   조회수: {result['view_count']}")
        print()
    
    # 데이터베이스 저장된 데이터 확인
    saved_issues = LocalIssue.objects.filter(location=location)
    print(f"\n데이터베이스에 저장된 이슈: {saved_issues.count()}개")
    
    for issue in saved_issues:
        print(f"- [{issue.source}] {issue.title[:50]}...")

if __name__ == "__main__":
    test_crawling()