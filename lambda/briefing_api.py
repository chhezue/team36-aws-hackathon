import json
import psycopg2
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """브리핑 데이터 조회 API"""
    
    try:
        # API Gateway에서 경로 파라미터 추출
        district = event['pathParameters']['district']
        
        # RDS에서 최신 브리핑 데이터 조회
        briefing_data = get_briefing_data(district)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(briefing_data, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_briefing_data(district):
    """RDS에서 브리핑 데이터 조회"""
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        # 최근 24시간 내 데이터 조회
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
        
        briefing_data = {
            'district': district,
            'generated_at': datetime.now().isoformat(),
            'issues': []
        }
        
        for row in results:
            briefing_data['issues'].append({
                'title': row[0],
                'url': row[1],
                'source': row[2],
                'summary': row[3],
                'collected_at': row[4].isoformat()
            })
    
    conn.close()
    return briefing_data