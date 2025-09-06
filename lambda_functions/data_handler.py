import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

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
    """데이터 조회 Lambda 함수"""
    try:
        # 요청 타입 확인
        request_type = event.get('type', 'briefing')
        district = event.get('district', '강남구')
        
        if request_type == 'briefing':
            return get_briefing_data(district)
        elif request_type == 'sentiment':
            return get_sentiment_data(district)
        elif request_type == 'restaurants':
            return get_restaurant_data(district)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid request type'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_briefing_data(district):
    """브리핑 데이터 조회"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 지역 ID 조회
        cursor.execute("SELECT id FROM locations WHERE gu = %s", (district,))
        location_row = cursor.fetchone()
        if not location_row:
            raise Exception(f"지역을 찾을 수 없습니다: {district}")
        location_id = location_row['id']
        
        # 최근 7일 이슈 조회
        cursor.execute("""
            SELECT title, source, url, view_count, published_at, collected_at
            FROM local_issues 
            WHERE location_id = %s AND collected_at >= %s
            ORDER BY view_count DESC, collected_at DESC
            LIMIT 10
        """, (location_id, datetime.now() - timedelta(days=7)))
        
        local_issues = cursor.fetchall()
        
        # 감성 분석 데이터 조회
        cursor.execute("""
            SELECT sentiment, confidence, analyzed_at
            FROM sentiment_analysis 
            WHERE location_id = %s AND analyzed_at >= %s
            ORDER BY analyzed_at DESC
            LIMIT 50
        """, (location_id, datetime.now() - timedelta(days=7)))
        
        sentiment_data = cursor.fetchall()
        
        # 감성 온도 계산
        if sentiment_data:
            positive_count = sum(1 for s in sentiment_data if s['sentiment'] == 'positive')
            negative_count = sum(1 for s in sentiment_data if s['sentiment'] == 'negative')
            total_count = len(sentiment_data)
            
            positive_ratio = positive_count / total_count if total_count > 0 else 0
            negative_ratio = negative_count / total_count if total_count > 0 else 0
            
            # 감성 온도 (0-100)
            temperature = int(50 + (positive_ratio - negative_ratio) * 50)
            
            # 이모지 결정
            if temperature >= 70:
                mood_emoji = "😊"
            elif temperature >= 50:
                mood_emoji = "😐"
            else:
                mood_emoji = "😔"
        else:
            temperature = 50
            mood_emoji = "😐"
            positive_ratio = 0
            negative_ratio = 0
        
        # 응답 데이터 구성
        response_data = {
            'success': True,
            'district': district,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {
                'temperature': temperature,
                'mood_emoji': mood_emoji,
                'description': f'{district}의 오늘 분위기입니다',
                'positive_ratio': positive_ratio,
                'negative_ratio': negative_ratio,
                'influential_news': [
                    {
                        'title': issue['title'],
                        'source': issue['source'],
                        'url': issue['url'],
                        'view_count': issue['view_count'],
                        'collected_at': issue['collected_at'].isoformat() if issue['collected_at'] else None
                    } for issue in local_issues[:3]
                ]
            },
            'categories': {
                'local_issues': {
                    'title': '동네 이슈',
                    'emoji': '💬',
                    'items': [
                        {
                            'title': issue['title'],
                            'source': issue['source'],
                            'url': issue['url'],
                            'view_count': issue['view_count'],
                            'collected_at': issue['collected_at'].isoformat() if issue['collected_at'] else None
                        } for issue in local_issues
                    ]
                }
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(response_data, ensure_ascii=False)
        }
        
    finally:
        cursor.close()
        conn.close()

def get_sentiment_data(district):
    """감성 분석 데이터만 조회"""
    # 브리핑 데이터에서 감성 부분만 추출
    briefing_response = get_briefing_data(district)
    briefing_data = json.loads(briefing_response['body'])
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({
            'success': True,
            'sentiment': briefing_data.get('sentiment', {})
        }, ensure_ascii=False)
    }

def get_restaurant_data(district):
    """맛집 데이터 조회"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 지역 ID 조회
        cursor.execute("SELECT id FROM locations WHERE gu = %s", (district,))
        location_row = cursor.fetchone()
        if not location_row:
            raise Exception(f"지역을 찾을 수 없습니다: {district}")
        location_id = location_row['id']
        
        # 최근 맛집 데이터 조회
        cursor.execute("""
            SELECT business_name, business_type, road_address, collected_at
            FROM restaurant_info 
            WHERE location_id = %s AND collected_at >= %s
            ORDER BY collected_at DESC
            LIMIT 20
        """, (location_id, datetime.now() - timedelta(days=30)))
        
        restaurants = cursor.fetchall()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'restaurants': [
                    {
                        'name': r['business_name'],
                        'type': r['business_type'],
                        'address': r['road_address'],
                        'license_date': r['collected_at'].strftime('%Y-%m-%d') if r['collected_at'] else None
                    } for r in restaurants
                ]
            }, ensure_ascii=False)
        }
        
    finally:
        cursor.close()
        conn.close()