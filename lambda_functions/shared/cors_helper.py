import json

def cors_response(status_code, body, origin='*'):
    """CORS 헤더가 포함된 응답을 생성하는 헬퍼 함수"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body
    }

def handle_options():
    """OPTIONS 요청 처리"""
    return cors_response(200, '')
