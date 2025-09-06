import json
import boto3
import requests
import os
from datetime import datetime
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
    """음식점 데이터 수집 Lambda"""
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
        district = event.get('district')  # 특정 구 또는 None (전체)
        
        if district:
            districts = [district]
        else:
            districts = [
                '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
            ]
        
        total_saved = 0
        
        # 서울시 API + 카카오 API 데이터 수집
        for district_name in districts:
            saved_count = 0
            saved_count += crawl_seoul_api(district_name)
            saved_count += crawl_kakao_api(district_name)
            total_saved += saved_count
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'message': f'음식점 데이터 수집 완료: {total_saved}개',
                'districts_processed': len(districts),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"음식점 Lambda 오류: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

def crawl_seoul_api(district_name):
    """서울시 API 음식점 데이터 수집"""
    api_key = os.environ.get('SEOUL_API_KEY')
    if not api_key:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    saved_count = 0
    
    try:
        # 지역 ID 조회
        cursor.execute("SELECT id FROM locations WHERE gu = %s", (district_name,))
        location_row = cursor.fetchone()
        if not location_row:
            return 0
        location_id = location_row['id']
        
        # 서울시 API 호출
        url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CrtfcUpsoInfo/1/1000"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'CrtfcUpsoInfo' in data and 'row' in data['CrtfcUpsoInfo']:
                restaurants = data['CrtfcUpsoInfo']['row']
                
                for restaurant in restaurants:
                    district = restaurant.get('CGG_CODE_NM', '').strip()
                    if district != district_name:
                        continue
                    
                    management_number = restaurant.get('MGTNO', '')
                    if not management_number:
                        continue
                    
                    # 중복 체크
                    cursor.execute("SELECT id FROM restaurant_info WHERE management_number = %s", (management_number,))
                    if cursor.fetchone():
                        continue
                    
                    # 데이터 저장
                    cursor.execute("""
                        INSERT INTO restaurant_info 
                        (location_id, management_number, business_type, business_name, road_address, collected_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        location_id, management_number, 'general',
                        restaurant.get('UPSO_NM', ''), restaurant.get('RDN_CODE_NM', ''),
                        datetime.utcnow()
                    ))
                    saved_count += 1
        
        conn.commit()
        return saved_count
        
    except Exception as e:
        conn.rollback()
        print(f"서울시 API 오류: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def crawl_kakao_api(district_name):
    """카카오 API 음식점 데이터 수집"""
    kakao_key = os.environ.get('KAKAO_API_KEY')
    if not kakao_key:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    saved_count = 0
    
    try:
        # 지역 ID 조회
        cursor.execute("SELECT id FROM locations WHERE gu = %s", (district_name,))
        location_row = cursor.fetchone()
        if not location_row:
            return 0
        location_id = location_row['id']
        
        # 카카오 API 호출
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {'Authorization': f'KakaoAK {kakao_key}'}
        params = {
            'query': f'{district_name} 맛집',
            'category_group_code': 'FD6',
            'size': 5
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for place in data.get('documents', []):
                place_id = place.get('id')
                management_number = f"kakao_{place_id}"
                
                # 중복 체크
                cursor.execute("SELECT id FROM restaurant_info WHERE management_number = %s", (management_number,))
                if cursor.fetchone():
                    continue
                
                # 데이터 저장
                cursor.execute("""
                    INSERT INTO restaurant_info 
                    (location_id, management_number, business_type, business_name, road_address, collected_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    location_id, management_number, 'general',
                    place.get('place_name', ''), place.get('road_address_name', ''),
                    datetime.utcnow()
                ))
                saved_count += 1
        
        conn.commit()
        return saved_count
        
    except Exception as e:
        conn.rollback()
        print(f"카카오 API 오류: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()