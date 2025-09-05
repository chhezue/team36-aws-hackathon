from django.apps import AppConfig

class LocalDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'local_data'
    
    def ready(self):
        """앱 시작 시 스케줄러 자동 시작"""
        import os
        
        # 개발 서버나 마이그레이션 시에는 스케줄러 시작하지 않음
        if os.environ.get('RUN_MAIN') == 'true' or 'runserver' in os.sys.argv:
            return
            
        # 프로덕션 환경에서만 스케줄러 자동 시작
        if os.environ.get('DJANGO_SETTINGS_MODULE') == 'localbriefing.settings.production':
            from .scheduler import crawler_scheduler
            crawler_scheduler.start_scheduler()