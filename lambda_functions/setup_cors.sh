#!/bin/bash

# Lambda Function URL에 CORS 설정 적용
FUNCTIONS=("data-handler" "weather-handler" "restaurant-handler" "crawler-handler")

for FUNCTION in "${FUNCTIONS[@]}"; do
    echo "Setting CORS for $FUNCTION..."
    
    aws lambda update-function-url-config \
        --function-name "$FUNCTION" \
        --cors '{
            "AllowCredentials": false,
            "AllowHeaders": ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"],
            "AllowMethods": ["GET", "POST", "OPTIONS"],
            "AllowOrigins": ["*"],
            "ExposeHeaders": [],
            "MaxAge": 86400
        }' \
        --region us-east-1
        
    echo "CORS configured for $FUNCTION"
done

echo "All Lambda Function URLs configured with CORS"
