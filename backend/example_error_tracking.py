"""
Example: Error Tracking Integration

This file demonstrates how to integrate error tracking into existing modules.
Copy these patterns into your actual modules (app.py, services/, etc.)
"""
from flask import Flask, request, jsonify
from monitoring.error_tracker import (
    track_error,
    track_supabase_error,
    track_aws_error,
    track_api_error,
    ErrorSeverity
)
import os

app = Flask(__name__)


# Example 1: Brand Asset Upload with Error Tracking
@app.route('/api/brand-assets/upload', methods=['POST'])
def upload_with_tracking():
    """
    Upload endpoint with comprehensive error tracking.
    Catches the "Bucket not found" error from manual testing.
    """
    try:
        if 'logo' not in request.files:
            return jsonify({"error": "No logo file provided"}), 400
        
        file = request.files['logo']
        brand_id = request.form.get('brand_id', 'default')
        bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'brand-assets')
        
        try:
            # Simulate Supabase upload
            # In real code: supabase.storage.from_(bucket_name).upload(...)
            
            # If bucket not found, this will raise an exception
            raise Exception("Bucket not found")
            
        except Exception as storage_error:
            # Track Supabase-specific error with full context
            track_supabase_error(
                storage_error,
                operation='upload',
                bucket_name=bucket_name,
                file_name=file.filename
            )
            
            return jsonify({
                "error": f"Storage upload failed: {str(storage_error)}",
                "details": "Check Supabase bucket configuration"
            }), 500
    
    except Exception as e:
        # Track general error
        track_error(e, context={
            'module': 'brand_asset_upload',
            'endpoint': '/api/brand-assets/upload'
        })
        return jsonify({"error": "Upload failed"}), 500


# Example 2: Content Ideation with Error Tracking
@app.route('/api/ideate', methods=['POST'])
def ideate_with_tracking():
    """
    Ideation endpoint with error tracking.
    Catches the "blank page" issue when API returns no results.
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        try:
            # Simulate LLM call
            # In real code: response = call_llm(prompt)
            ideas = []  # Simulate empty response
            
            if not ideas or len(ideas) == 0:
                # Track when API returns no results (causes blank page)
                track_api_error(
                    Exception("No ideas generated - API returned empty response"),
                    endpoint='/api/ideate',
                    method='POST',
                    query_params={'prompt': prompt[:100]},  # Truncate for logging
                    status_code=200  # API succeeded but returned no data
                )
                
                return jsonify({
                    "error": "No ideas generated",
                    "message": "Try a different prompt or check API configuration"
                }), 500
            
            return jsonify({"ideas": ideas})
            
        except Exception as llm_error:
            track_api_error(
                llm_error,
                endpoint='/api/ideate',
                method='POST',
                status_code=500,
                query_params={'prompt': prompt[:100]}
            )
            return jsonify({"error": "Ideation failed"}), 500
    
    except Exception as e:
        track_error(e, context={
            'module': 'content_ideation',
            'endpoint': '/api/ideate'
        })
        return jsonify({"error": "Request failed"}), 500


# Example 3: Media Generator with Error Tracking
@app.route('/api/generate-media', methods=['POST'])
def generate_media_with_tracking():
    """
    Media generation endpoint with error tracking.
    Catches the AWS region mismatch error from manual testing.
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        try:
            # Get AWS configuration
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            s3_region = os.getenv('AWS_S3_REGION', aws_region)
            
            # Check for region mismatch (the production bug)
            if aws_region != s3_region:
                error = Exception(
                    f"AWS region mismatch: Bedrock={aws_region}, S3={s3_region}"
                )
                track_aws_error(
                    error,
                    service='bedrock',
                    operation='invoke_model',
                    region=aws_region,
                    model_id='amazon.titan-image-generator-v1'
                )
                return jsonify({
                    "error": "Configuration error: AWS region mismatch",
                    "details": f"Expected {aws_region}, got {s3_region}"
                }), 500
            
            # Simulate AWS Bedrock call
            # In real code: bedrock_client.invoke_model(...)
            
            return jsonify({
                "success": True,
                "image": "base64_image_data"
            })
            
        except Exception as aws_error:
            # Track AWS-specific error
            track_aws_error(
                aws_error,
                service='bedrock',
                operation='invoke_model',
                region=aws_region,
                model_id='amazon.titan-image-generator-v1'
            )
            return jsonify({
                "error": f"Image generation failed: {str(aws_error)}"
            }), 500
    
    except Exception as e:
        track_error(e, context={
            'module': 'media_generator',
            'endpoint': '/api/generate-media'
        })
        return jsonify({"error": "Request failed"}), 500


# Example 4: Creative Studio with Error Tracking
@app.route('/api/studio/generate', methods=['POST'])
def studio_generate_with_tracking():
    """
    Creative studio endpoint with error tracking.
    Catches the "non-functional button" issue when no output is generated.
    """
    try:
        data = request.json
        
        try:
            # Simulate post generation
            post_content = None  # Simulate no output (the production bug)
            
            if not post_content:
                # Track non-functional button issue
                track_error(
                    Exception("Generate post button produced no output"),
                    context={
                        'module': 'creative_studio',
                        'operation': 'generate_post',
                        'input_data': data,
                        'issue': 'non_functional_button'
                    },
                    severity=ErrorSeverity.WARNING
                )
                
                return jsonify({
                    "error": "No content generated",
                    "message": "The generate button did not produce output. Check LLM configuration."
                }), 500
            
            return jsonify({
                "content": post_content,
                "tone_score": 0.8
            })
            
        except Exception as gen_error:
            track_error(gen_error, context={
                'module': 'creative_studio',
                'operation': 'generate_post',
                'endpoint': '/api/studio/generate'
            })
            return jsonify({"error": "Generation failed"}), 500
    
    except Exception as e:
        track_error(e, context={
            'module': 'creative_studio',
            'endpoint': '/api/studio/generate'
        })
        return jsonify({"error": "Request failed"}), 500


# Example 5: Frontend Error Tracking Endpoint
@app.route('/api/track-error', methods=['POST'])
def track_frontend_error():
    """
    Endpoint to receive and track errors from frontend.
    Catches UI component errors and non-functional buttons.
    """
    try:
        data = request.json
        error_type = data.get('error_type', 'UnknownError')
        message = data.get('message', 'No message')
        
        # Create exception from frontend error
        exception = Exception(message)
        
        context = {
            'module': 'frontend',
            'component': data.get('component'),
            'endpoint': data.get('endpoint'),
            'stack': data.get('stack'),
            'user_agent': request.headers.get('User-Agent'),
            'props': data.get('props')
        }
        
        # Use appropriate severity
        severity = ErrorSeverity.ERROR
        if 'critical' in message.lower():
            severity = ErrorSeverity.CRITICAL
        elif 'warning' in message.lower():
            severity = ErrorSeverity.WARNING
        
        track_error(exception, context=context, severity=severity)
        
        return jsonify({"success": True}), 200
    
    except Exception as e:
        # Even error tracking can fail - log it
        print(f"Failed to track frontend error: {e}")
        return jsonify({"error": "Failed to track error"}), 500


if __name__ == '__main__':
    print("This is an example file showing error tracking integration.")
    print("Copy these patterns into your actual modules:")
    print("  - backend/app.py")
    print("  - backend/services/*.py")
    print("  - frontend/src/lib/api.ts")
    print("\nSee ERROR_TRACKING_INTEGRATION.md for complete guide.")
