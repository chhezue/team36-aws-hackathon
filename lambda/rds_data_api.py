import json
import psycopg2
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """RDS에서 저장된 데이터 조회 API"""
    
    try:
        # API Gateway 경로에서 엔드포인트 추출
        path = event.get('rawPath', '').strip('/')
        body = json.loads(event.get('body', '{}'))
        district = body.get('district')
        
        if path == 'briefing':
            data = get_briefing_data(district)
        elif path == 'sentiment':
            days = body.get('days', 7)
            data = get_sentiment_data(district, days)
        elif path == 'weather':
            data = get_weather_data(district)
        elif path == 'restaurants':
            data = get_restaurant_data(district)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(data, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_db_connection():
    """RDS 연결"""
    return psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )

def get_briefing_data(district):
    """브리핑 데이터 조회"""
    conn = get_db_connection()
    
    with conn.cursor() as cursor:
        yesterday = datetime.now() - timedelta(days=1)
        
        cursor.execute("""
            SELECT title, url, source, collected_at
            FROM local_data_localissue li
            JOIN local_data_location loc ON li.location_id = loc.id
            WHERE loc.name = %s AND li.collected_at >= %s
            ORDER BY li.collected_at DESC
            LIMIT 10
        """, (district, yesterday))
        
        results = cursor.fetchall()
        
        return {
            'district': district,
            'issues': [
                {
                    'title': row[0],
                    'url': row[1],
                    'source': row[2],
                    'collected_at': row[3].isoformat()
                } for row in results
            ]
        }

def get_sentiment_data(district, days):
    """감성 분석 데이터 조회"""
    conn = get_db_connection()
    
    with conn.cursor() as cursor:
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT AVG(sentiment_score), COUNT(*)
            FROM local_data_sentimentanalysis sa
            JOIN local_data_location loc ON sa.location_id = loc.id
            WHERE loc.name = %s AND sa.analyzed_at >= %s
        """, (district, start_date))
        
        result = cursor.fetchone()
        
        return {
            'district': district,
            'sentiment_score': float(result[0]) if result[0] else 0,
            'total_analyzed': result[1],
            'days': days
        }

def get_weather_data(district):
    """날씨 데이터 조회"""
    return {
        'district': district,
        'temperature': 22,
        'weather': '맑음',
        'humidity': 65
    }

def get_restaurant_data(district):
    """음식점 데이터 조회"""
    conn = get_db_connection()
    
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT name, address, category
            FROM local_data_restaurantinfo ri
            JOIN local_data_location loc ON ri.location_id = loc.id
            WHERE loc.name = %s
            ORDER BY ri.created_at DESC
            LIMIT 5
        """, (district,))
        
        results = cursor.fetchall()
        
        return {
            'district': district,
            'restaurants': [
                {
                    'name': row[0],
                    'address': row[1],
                    'category': row[2]
                } for row in results
            ]
        }