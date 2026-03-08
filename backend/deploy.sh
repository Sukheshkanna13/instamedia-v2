#!/bin/bash
set -e

echo "Starting Deployment Process..."
echo "1. Fetching secrets from AWS Secrets Manager..."

# Note: This assumes the EC2 Instance has an IAM Role attached with permissions to read 'instamedia/prod/env'
export AWS_DEFAULT_REGION="us-east-1"

# Fetch secrets and parse them directly into a fresh .env.production file
aws secretsmanager get-secret-value --secret-id instamedia/prod/env --query SecretString --output text | jq -r 'to_entries | map("\(.key)=\(.value)") | .[]' > .env.production

if [ -s .env.production ]; then
    echo "Secrets successfully fetched and written to .env.production."
else
    echo "ERROR: Failed to fetch secrets or parse them. Aborting deployment."
    exit 1
fi

echo "2. Tearing down old containers..."
docker-compose down

echo "3. Rebuilding Docker Images..."
docker-compose build

echo "4. Spinning up production environment..."
docker-compose up -d

echo "✅ InstaMedia Backend Deployment Complete! Nginx reversing proxy is active on Port 443."
