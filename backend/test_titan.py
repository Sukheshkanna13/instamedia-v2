import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = boto3.client('bedrock-runtime', region_name='us-east-1',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

body = {
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {
        "text": "A modern workspace"
    },
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "quality": "standard",
        "height": 1024,
        "width": 1024,
        "cfgScale": 8.0
    }
}

try:
    response = client.invoke_model(
        modelId='amazon.titan-image-generator-v2:0',
        contentType='application/json',
        accept='application/json',
        body=json.dumps(body)
    )
    print("Success! Titan works.")
except Exception as e:
    print(f"Error: {e}")
