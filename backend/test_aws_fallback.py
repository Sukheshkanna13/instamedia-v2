import os
from dotenv import load_dotenv

# Load explicitly the .env
load_dotenv()

from services.aws_image_generator import create_aws_image_generator

def run_fallback_test():
    aws_gen = create_aws_image_generator()
    if not aws_gen:
        print("Failed to initialize AWS Generator")
        return
        
    print("Testing Fallback Pipeline...")
    # Force a failure by overriding the bedrock model id to something that causes 400 Validation Error or 403
    aws_gen.bedrock_model_id = "amazon.this-model-does-not-exist"
    
    print(f"Set broken model ID: {aws_gen.bedrock_model_id}")
    
    # Try generating
    try:
        res = aws_gen.generate_and_upload(
            prompt="A cinematic neon cyberpunk skyline with flying cars.",
            filename="fallback_test_output.png"
        )
        print("Pipeline Complete! Output:")
        print(res)
    except Exception as e:
        print(f"Exception escaped fallback: {e}")

if __name__ == "__main__":
    run_fallback_test()
