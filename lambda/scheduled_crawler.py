import json
import psycopg2
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def lambda_handler(event, context):
    """EventBridge로 매일 자정 실행되는 크롤링 함수"""
    
    try:
        districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구',
            '종로구', '중구', '중랑구'
        ]
        
        total_processed = 0
        
        for district in districts:
            raw_data = crawl_district_data(district)
            save_to_rds(raw_data, district)
            total_processed += len(raw_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '크롤링 완료',
                'processed_items': total_processed,
                'districts': len(districts)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def crawl_district_data(district):
    """구별 데이터 크롤링"""
    data = []
    
    # 유튜브 크롤링
    youtube_data = crawl_youtube(district)
    data.extend(youtube_data)
    
    # 네이버 뉴스 크롤링
    naver_data = crawl_naver_news(district)
    data.extend(naver_data)
    
    return data

def crawl_youtube(district):
    """유튜브 크롤링"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={district}+뉴스+오늘"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers)
        
        return [
            {
                'title': f'{district} 유튜브 뉴스',
                'url': 'https://youtube.com/example',
                'source': 'youtube'
            }
        ]
    except:
        return []

def crawl_naver_news(district):
    """네이버 뉴스 크롤링"""
    try:
        search_url = f"https://search.naver.com/search.naver?where=news&query={district}+뉴스"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers)
        
        return [
            {
                'title': f'{district} 네이버 뉴스',
                'url': 'https://news.naver.com/example',
                'source': 'naver_news'
            }
        ]
    except:
        return []

def save_to_rds(data, district):
    """RDS에 크롤링 데이터 저장"""
    conn = psycopg2.connect(
        host=os.environ['RDS_HOSTNAME'],
        database=os.environ['RDS_DB_NAME'],
        user=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD']
    )
    
    with conn.cursor() as cursor:
        for item in data:
            cursor.execute("""
                INSERT INTO local_data_localissue (title, url, source, location_id, collected_at)
                VALUES (%s, %s, %s, (SELECT id FROM local_data_location WHERE name = %s), %s)
                ON CONFLICT (url) DO NOTHING
            """, (item['title'], item['url'], item['source'], district, datetime.now()))
    
    conn.commit()
    conn.close()