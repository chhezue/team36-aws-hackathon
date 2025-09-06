import json
import boto3
import asyncio
from datetime import datetime
import sys
import os

# Lambda Layer에서 공통 모듈 import
sys.path.append('/opt/python')
from shared.optimized_crawler import AsyncCrawlerWrapper
from shared.sentiment_analyzer import SimpleSentimentAnalyzer

# RDS 연결
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """RDS PostgreSQL 연결"""
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ.get('DB_PORT', '5432')
    )

def lambda_handler(event, context):
    """메인 Lambda 핸들러"""
    # OPTIONS 요청 처리
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # 이벤트에서 파라미터 추출
        district = event.get('district')  # 특정 구 또는 None (전체)
        limit = event.get('limit', 50)
        
        # 크롤링 실행
        crawler = AsyncCrawlerWrapper(max_concurrent=10)
        
        if district:
            # 단일 구 크롤링
            results = crawler.crawl_single_district(district, limit)
            district_results = {district: results}
        else:
            # 전체 구 크롤링
            districts = [
                '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
            ]
            district_results = crawler.crawl_all_districts(districts, limit)
        
        # 데이터베이스 저장 및 감성 분석
        total_saved = save_to_database(district_results)
        
        # CloudWatch 메트릭 전송
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            Namespace='VibeThermo/Crawler',
            MetricData=[
                {
                    'MetricName': 'IssuesCollected',
                    'Value': total_saved,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'message': f'크롤링 완료: {total_saved}개 수집',
                'districts_processed': len(district_results),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Lambda 실행 오류: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def save_to_database(district_results):
    """크롤링 결과를 RDS에 저장"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    analyzer = SimpleSentimentAnalyzer()
    total_saved = 0
    
    try:
        for district_name, results in district_results.items():
            if not results:
                continue
            
            # 지역 ID 조회
            cursor.execute("SELECT id FROM locations WHERE gu = %s", (district_name,))
            location_row = cursor.fetchone()
            if not location_row:
                continue
            location_id = location_row['id']
            
            for result in results:
                # 중복 체크
                cursor.execute("SELECT id FROM local_issues WHERE url = %s", (result['url'],))
                if cursor.fetchone():
                    continue
                
                # LocalIssue 저장
                cursor.execute("""
                    INSERT INTO local_issues (location_id, source, title, url, view_count, published_at, collected_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    location_id, result['source'], result['title'], result['url'],
                    result['view_count'], result['published_at'], datetime.utcnow()
                ))
                
                issue_id = cursor.fetchone()['id']
                
                # 감성 분석
                sentiment_result = analyzer.analyze_text(result['title'])
                
                # SentimentAnalysis 저장
                cursor.execute("""
                    INSERT INTO sentiment_analysis (location_id, content_type, content_id, sentiment, confidence, keywords, analyzed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    location_id, 'local_issue', issue_id, sentiment_result['sentiment'],
                    sentiment_result['confidence'], json.dumps(sentiment_result['keywords']), datetime.utcnow()
                ))
                
                total_saved += 1
        
        conn.commit()
        return total_saved
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()