import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = boto3.client('bedrock-runtime', region_name='us-west-2',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

body = {
    "prompt": "A beautiful sunset over the mountains",
    "mode": "text-to-image",
    "aspect_ratio": "1:1",
    "output_format": "png"
}

try:
    response = client.invoke_model(
        modelId='stability.stable-image-core-v1:1',
        contentType='application/json',
        accept='application/json',
        body=json.dumps(body)
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
