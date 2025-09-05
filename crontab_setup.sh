#!/bin/bash

# LocalBriefing 크론탭 설정 스크립트

PROJECT_PATH="/Users/sesil/PycharmProjects/team36-aws-hackathon/localbriefing"
PYTHON_PATH="/Users/sesil/PycharmProjects/team36-aws-hackathon/venv/bin/python"

# 현재 크론탭 백업
crontab -l > crontab_backup.txt 2>/dev/null

# 새로운 크론 작업 추가
echo "# LocalBriefing 자동 크롤링 및 감성 분석" >> temp_cron.txt
echo "0 0 * * * cd $PROJECT_PATH && $PYTHON_PATH manage.py daily_crawl_and_analyze --limit=30" >> temp_cron.txt
echo "" >> temp_cron.txt

# 기존 크론탭과 합치기
if [ -f crontab_backup.txt ]; then
    cat crontab_backup.txt temp_cron.txt | crontab -
else
    crontab temp_cron.txt
fi

# 임시 파일 정리
rm -f temp_cron.txt

echo "크론탭 설정 완료!"
echo "매일 자정에 크롤링 및 감성 분석이 실행됩니다."
echo ""
echo "현재 크론탭 목록:"
crontab -l