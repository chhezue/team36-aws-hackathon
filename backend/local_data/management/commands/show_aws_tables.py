from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'AWS RDS 테이블 상세 정보 확인'
    
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # 모든 테이블과 행 개수 조회
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            self.stdout.write("=== AWS RDS PostgreSQL 테이블 상세 ===")
            
            for (table_name,) in tables:
                try:
                    # 각 테이블의 행 개수 조회
                    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                    row_count = cursor.fetchone()[0]
                    
                    # 컬럼 정보 조회
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, [table_name])
                    columns = cursor.fetchall()
                    
                    self.stdout.write(f"\n📋 {table_name}: {row_count}개 행")
                    for col_name, col_type in columns[:3]:  # 처음 3개 컬럼만 표시
                        self.stdout.write(f"   - {col_name}: {col_type}")
                    if len(columns) > 3:
                        self.stdout.write(f"   ... 총 {len(columns)}개 컬럼")
                        
                except Exception as e:
                    self.stdout.write(f"❌ {table_name}: 오류 - {str(e)}")
            
            self.stdout.write(f"\n총 {len(tables)}개 테이블 존재")