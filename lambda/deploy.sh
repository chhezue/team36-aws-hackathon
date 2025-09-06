#!/bin/bash

# RDS 데이터 API Lambda 배포
zip -r rds-data-api.zip rds_data_api.py requirements.txt
aws lambda update-function-code --function-name localbriefing-data-api --zip-file fileb://rds-data-api.zip

# 크롤링 Lambda 배포  
zip -r crawler.zip scheduled_crawler.py requirements.txt
aws lambda update-function-code --function-name localbriefing-crawler --zip-file fileb://crawler.zip

echo "배포 완료"