import json
import boto3
import psycopg2
import os
from datetime import datetime

def lambda_handler(event, context):
    """매일 새벽 4시 실행되는 스케줄링된 크롤러"""
    
    try:
        districts = ['강남구', '강동구', '강북구', '강서구', '관악구']
        
        for district in districts:
            # 1. 크롤링 실행
            raw_data = crawl_district_data(district)
            
            # 2. RDS에 원시 데이터 저장
            save_to_rds(raw_data, district)
            
            # 3. Bedrock으로 요약 생성 및 저장
            process_and_save_summaries(raw_data, district)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': '크롤링 완료'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def crawl_district_data(district):
    """구별 데이터 크롤링"""
    # 크롤링 로직 구현
    return [
        {'title': f'{district} 공지사항', 'url': 'http://example.com', 'source': 'district'}
    ]

def save_to_rds(data, district):
    """RDS에 원시 데이터 저장"""
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        for item in data:
            cursor.execute("""
                INSERT INTO local_data_rawdata (title, source_url, category, content, location_id, collected_at)
                VALUES (%s, %s, %s, %s, (SELECT id FROM local_data_location WHERE name = %s), %s)
            """, (item['title'], item['url'], item['source'], item['title'], district, datetime.now()))
    
    conn.commit()
    conn.close()

def process_and_save_summaries(data, district):
    """Bedrock으로 요약 생성 후 저장"""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        for item in data:
            # Bedrock 요약
            body = json.dumps({
                "prompt": f"\\n\\nHuman: 다음을 동네 뉴스로 3문장 요약: {item['title']}\\n\\nAssistant:",
                "max_tokens_to_sample": 200,
                "temperature": 0.7
            })
            
            response = bedrock.invoke_model(
                body=body,
                modelId="anthropic.claude-v2",
                accept="application/json",
                contentType="application/json"
            )
            
            result = json.loads(response.get('body').read())
            summary = result.get('completion', '').strip()
            
            # 브리핑 데이터 저장
            cursor.execute("""
                INSERT INTO local_data_localissue (title, url, source, location_id, collected_at, summary)
                VALUES (%s, %s, %s, (SELECT id FROM local_data_location WHERE name = %s), %s, %s)
            """, (item['title'], item['url'], item['source'], district, datetime.now(), summary))
    
    conn.commit()
    conn.close()