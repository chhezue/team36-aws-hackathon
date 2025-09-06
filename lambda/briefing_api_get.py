import json
import psycopg2
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """GET 방식 브리핑 데이터 조회 API"""
    
    try:
        # GET 쿼리 파라미터에서 district 추출
        district = event.get('queryStringParameters', {}).get('district')
        request_type = event.get('queryStringParameters', {}).get('type', 'briefing')
        
        if not district:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'district parameter required'})
            }
        
        if request_type == 'sentiment':
            days = int(event.get('queryStringParameters', {}).get('days', 7))
            data = get_sentiment_data(district, days)
        else:
            data = get_briefing_data(district)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(data, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_briefing_data(district):
    """저장된 브리핑 데이터 조회"""
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        yesterday = datetime.now() - timedelta(days=1)
        
        cursor.execute("""
            SELECT title, url, source, summary, collected_at
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
                    'summary': row[3],
                    'collected_at': row[4].isoformat()
                } for row in results
            ]
        }

def get_sentiment_data(district, days):
    """감성 분석 데이터 조회"""
    return {
        'district': district,
        'sentiment_score': 75,
        'days': days
    }