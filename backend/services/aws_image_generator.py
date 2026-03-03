"""
AWS Bedrock Image Generator Service - Phase 6, Days 12-13
Generates images using Amazon Titan Image Generator and uploads to S3.

Features:
- Single image generation
- Concurrent carousel image generation
- S3 upload with public URLs
- Error handling and retries
"""

import os
import json
import base64
import uuid
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("⚠️  boto3 not installed. AWS features will be disabled.")


class AWSImageGenerator:
    """Service for generating images with AWS Bedrock Titan and uploading to S3"""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        bedrock_region: str,
        bedrock_model_id: str,
        s3_bucket_name: str,
        s3_region: str
    ):
        """
        Initialize AWS clients
        
        Args:
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            aws_region: Default AWS region
            bedrock_region: Region for Bedrock (us-east-1 for Titan)
            bedrock_model_id: Bedrock model ID (amazon.titan-image-generator-v2:0)
            s3_bucket_name: S3 bucket for storing images
            s3_region: S3 bucket region
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for AWS image generation")
        
        self.bedrock_model_id = bedrock_model_id
        self.s3_bucket_name = s3_bucket_name
        self.s3_region = s3_region
        
        # Create Bedrock Runtime client (for image generation)
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=bedrock_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # Create S3 client (for uploading images)
        self.s3_client = boto3.client(
            's3',
            region_name=s3_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        print(f"✅ AWS Image Generator initialized")
        print(f"   Bedrock: {bedrock_region} / {bedrock_model_id}")
        print(f"   S3: {s3_bucket_name} ({s3_region})")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        cfg_scale: float = 8.0,
        seed: Optional[int] = None
    ) -> bytes:
        """
        Generate a single image using AWS Bedrock Titan
        
        Args:
            prompt: Text description of the image
            negative_prompt: What to avoid in the image
            width: Image width (512-2048, must be multiple of 64)
            height: Image height (512-2048, must be multiple of 64)
            cfg_scale: How closely to follow the prompt (1.0-10.0)
            seed: Random seed for reproducibility
            
        Returns:
            Image data as bytes
        """
        # Prepare request body for Titan Image Generator v2
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",  # or "premium"
                "height": height,
                "width": width,
                "cfgScale": cfg_scale
            }
        }
        
        if negative_prompt:
            body["textToImageParams"]["negativeText"] = negative_prompt
        
        if seed is not None:
            body["imageGenerationConfig"]["seed"] = seed
        
        try:
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract base64 image
            if 'images' in response_body and len(response_body['images']) > 0:
                base64_image = response_body['images'][0]
                image_data = base64.b64decode(base64_image)
                return image_data
            else:
                raise ValueError("No image returned from Bedrock")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"Bedrock error ({error_code}): {error_message}")
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def upload_to_s3(
        self,
        image_data: bytes,
        filename: Optional[str] = None,
        content_type: str = "image/png",
        expiration: int = 604800  # 7 days in seconds
    ) -> str:
        """
        Upload image to S3 and return presigned URL (valid for 7 days)
        
        Args:
            image_data: Image bytes
            filename: Optional filename (generates UUID if not provided)
            content_type: MIME type
            expiration: URL expiration time in seconds (default 7 days)
            
        Returns:
            Presigned S3 URL (valid for specified duration)
        """
        if filename is None:
            filename = f"generated/{uuid.uuid4()}.png"
        
        try:
            # Upload to S3 (private object)
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=filename,
                Body=image_data,
                ContentType=content_type
            )
            
            # Generate presigned URL (valid for 7 days)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket_name,
                    'Key': filename
                },
                ExpiresIn=expiration
            )
            
            return url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"S3 upload error ({error_code}): {error_message}")
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def generate_and_upload(
        self,
        prompt: str,
        filename: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image and upload to S3 in one call
        
        Args:
            prompt: Image prompt
            filename: Optional S3 filename
            **kwargs: Additional args for generate_image()
            
        Returns:
            {
                "url": str,
                "filename": str,
                "size_bytes": int,
                "generation_time_seconds": float
            }
        """
        start_time = time.time()
        
        # Generate image
        image_data = self.generate_image(prompt, **kwargs)
        
        # Upload to S3
        url = self.upload_to_s3(image_data, filename)
        
        generation_time = time.time() - start_time
        
        return {
            "url": url,
            "filename": filename or url.split('/')[-1],
            "size_bytes": len(image_data),
            "generation_time_seconds": round(generation_time, 2)
        }
    
    def generate_carousel_images(
        self,
        slides: List[Dict[str, str]],
        max_workers: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate images for carousel slides concurrently
        
        Args:
            slides: List of slides with 'image_prompt' field
            max_workers: Max concurrent generations (default 3)
            
        Returns:
            List of results with URLs for each slide
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all generation tasks
            future_to_slide = {}
            for idx, slide in enumerate(slides):
                prompt = slide.get('image_prompt', '')
                if not prompt:
                    continue
                
                filename = f"carousel/{uuid.uuid4()}_slide_{idx+1}.png"
                future = executor.submit(
                    self.generate_and_upload,
                    prompt=prompt,
                    filename=filename
                )
                future_to_slide[future] = (idx, slide)
            
            # Collect results as they complete
            for future in as_completed(future_to_slide):
                idx, slide = future_to_slide[future]
                try:
                    result = future.result()
                    results.append({
                        "slide_number": idx + 1,
                        "url": result["url"],
                        "generation_time_seconds": result["generation_time_seconds"]
                    })
                    print(f"✅ Generated slide {idx+1} in {result['generation_time_seconds']}s")
                except Exception as e:
                    print(f"❌ Failed to generate slide {idx+1}: {e}")
                    results.append({
                        "slide_number": idx + 1,
                        "url": None,
                        "error": str(e)
                    })
        
        # Sort by slide number
        results.sort(key=lambda x: x['slide_number'])
        return results
    
    def generate_storyboard_keyframes(
        self,
        scenes: List[Dict[str, str]],
        max_workers: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate keyframe images for video storyboard concurrently
        
        Args:
            scenes: List of scenes with 'keyframe_prompt' field
            max_workers: Max concurrent generations (default 3)
            
        Returns:
            List of results with URLs for each scene
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all generation tasks
            future_to_scene = {}
            for idx, scene in enumerate(scenes):
                prompt = scene.get('keyframe_prompt', '')
                if not prompt:
                    continue
                
                filename = f"storyboard/{uuid.uuid4()}_scene_{idx+1}.png"
                future = executor.submit(
                    self.generate_and_upload,
                    prompt=prompt,
                    filename=filename
                )
                future_to_scene[future] = (idx, scene)
            
            # Collect results as they complete
            for future in as_completed(future_to_scene):
                idx, scene = future_to_scene[future]
                try:
                    result = future.result()
                    results.append({
                        "scene_number": idx + 1,
                        "url": result["url"],
                        "generation_time_seconds": result["generation_time_seconds"]
                    })
                    print(f"✅ Generated scene {idx+1} in {result['generation_time_seconds']}s")
                except Exception as e:
                    print(f"❌ Failed to generate scene {idx+1}: {e}")
                    results.append({
                        "scene_number": idx + 1,
                        "url": None,
                        "error": str(e)
                    })
        
        # Sort by scene number
        results.sort(key=lambda x: x['scene_number'])
        return results


# ── FACTORY FUNCTION ──────────────────────────────────────────────────────────

def create_aws_image_generator() -> Optional[AWSImageGenerator]:
    """
    Factory function to create AWSImageGenerator from environment variables
    
    Returns:
        AWSImageGenerator instance or None if credentials not configured
    """
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    # Always use us-east-1 for Bedrock Titan Image Generator
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
    
    # Overwrite bedrock region explicitly to us-east-1 to prevent "eu-north-1 is wrong" error
    bedrock_region = "us-east-1"
    
    bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-image-generator-v2:0")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_region = os.getenv("S3_REGION", aws_region)
    
    if not all([aws_access_key_id, aws_secret_access_key, s3_bucket_name]):
        print("⚠️  AWS credentials not fully configured")
        return None
    
    try:
        return AWSImageGenerator(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            bedrock_region=bedrock_region,
            bedrock_model_id=bedrock_model_id,
            s3_bucket_name=s3_bucket_name,
            s3_region=s3_region
        )
    except Exception as e:
        print(f"❌ Failed to create AWS Image Generator: {e}")
        return None
