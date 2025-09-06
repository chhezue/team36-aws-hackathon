import json
import boto3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

def lambda_handler(event, context):
    """간단한 크롤링 Lambda 핸들러 (DB 연결 없이)"""
    try:
        # 이벤트에서 파라미터 추출
        district = event.get('district', '강남구')
        limit = event.get('limit', 10)
        
        print(f"크롤링 시작: {district}, 제한: {limit}")
        
        # 간단한 네이버 뉴스 크롤링
        results = crawl_naver_news(district, limit)
        
        # CloudWatch 메트릭 전송
        try:
            cloudwatch = boto3.client('cloudwatch')
            cloudwatch.put_metric_data(
                Namespace='LocalBriefing/Crawler',
                MetricData=[
                    {
                        'MetricName': 'IssuesCollected',
                        'Value': len(results),
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            print(f"CloudWatch 메트릭 전송 실패: {e}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'크롤링 완료: {len(results)}개 수집',
                'district': district,
                'results': results[:5],  # 처음 5개만 반환
                'timestamp': datetime.utcnow().isoformat()
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Lambda 실행 오류: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def crawl_naver_news(district, limit):
    """네이버 뉴스 크롤링"""
    results = []
    
    try:
        query = f"{district} 뉴스"
        url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sort=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('.list_news .bx')[:limit]
            
            for item in news_items:
                title_elem = item.select_one('.news_tit')
                if title_elem:
                    results.append({
                        'source': 'naver_news',
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'view_count': 0,
                        'published_at': datetime.now().isoformat()
                    })
        
        print(f"크롤링 결과: {len(results)}개")
        return results
        
    except Exception as e:
        print(f"크롤링 오류: {e}")
        return []