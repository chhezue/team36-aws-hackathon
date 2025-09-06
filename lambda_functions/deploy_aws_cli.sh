#!/bin/bash

# 환경변수 로드
source ../.env

# Python 3.9 환경 설정
pyenv local 3.9.18

# Lambda 함수 패키징
echo "패키징 중..."
zip -r crawler_function.zip crawler_handler.py
zip -r restaurant_function.zip restaurant_handler.py

# Lambda 함수 생성/업데이트
echo "Lambda 함수 배포 중..."

# Crawler 함수
aws lambda create-function \
  --function-name crawler-function \
  --runtime python3.9 \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \
  --handler crawler_handler.lambda_handler \
  --zip-file fileb://crawler_function.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{DB_HOST=$DB_HOST,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,KAKAO_API_KEY=$KAKAO_API_KEY}" \
  || aws lambda update-function-code \
  --function-name crawler-function \
  --zip-file fileb://crawler_function.zip

# Restaurant 함수
aws lambda create-function \
  --function-name restaurant-function \
  --runtime python3.9 \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \
  --handler restaurant_handler.lambda_handler \
  --zip-file fileb://restaurant_function.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{DB_HOST=$DB_HOST,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,SEOUL_API_KEY=$SEOUL_API_KEY,KAKAO_API_KEY=$KAKAO_API_KEY}" \
  || aws lambda update-function-code \
  --function-name restaurant-function \
  --zip-file fileb://restaurant_function.zip

echo "배포 완료!"