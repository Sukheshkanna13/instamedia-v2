import boto3
import os

from dotenv import load_dotenv
load_dotenv()

try:
    client = boto3.client('bedrock', 
                          region_name='us-west-2',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    response = client.list_foundation_models()
    for rm in response.get('modelSummaries', []):
        if 'stability' in rm['providerName'].lower():
            print(rm['modelId'])
except Exception as e:
    print(f"Error: {e}")
