# Error Tracking Integration Guide

## Overview

This guide shows how to integrate the ErrorTracker into existing modules to capture production errors.

## Quick Start

### 1. Import Error Tracking Functions

```python
from monitoring.error_tracker import (
    track_error,
    track_supabase_error,
    track_aws_error,
    track_api_error,
    track_ui_error,
    ErrorSeverity
)
```

### 2. Wrap Critical Operations

## Brand Asset Upload Module

```python
@app.route('/api/brand-assets/upload', methods=['POST'])
def upload_logo():
    try:
        if 'logo' not in request.files:
            return jsonify({"error": "No logo file provided"}), 400
        
        file = request.files['logo']
        brand_id = request.form.get('brand_id', 'default')
        
        # ... validation code ...
        
        # Upload to Supabase Storage
        try:
            result = supabase.storage.from_(bucket_name).upload(
                file_path,
                file_content,
                {"content-type": file.content_type}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            
            return jsonify({
                "success": True,
                "logo_url": public_url
            })
            
        except Exception as storage_error:
            # Track Supabase-specific error
            track_supabase_error(
                storage_error,
                operation='upload',
                bucket_name=bucket_name,
                file_name=file_path
            )
            return jsonify({
                "error": f"Storage upload failed: {str(storage_error)}"
            }), 500
    
    except Exception as e:
        # Track general error
        track_error(e, context={
            'module': 'brand_asset_upload',
            'endpoint': '/api/brand-assets/upload',
            'brand_id': brand_id
        })
        return jsonify({"error": "Upload failed"}), 500
```

## Content Ideation Module

```python
@app.route('/api/ideate', methods=['POST'])
def ideate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        try:
            # Call LLM
            response = call_llm(prompt)
            
            # Parse response
            ideas = parse_llm_json(response)
            
            if not ideas or len(ideas) == 0:
                # Track when API returns no results (blank page issue)
                track_api_error(
                    Exception("No ideas generated"),
                    endpoint='/api/ideate',
                    method='POST',
                    query_params={'prompt': prompt[:100]}  # Truncate for logging
                )
                return jsonify({"error": "No ideas generated"}), 500
            
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
```

## Creative Studio Module

```python
@app.route('/api/studio/generate', methods=['POST'])
def studio_generate():
    try:
        data = request.json
        
        try:
            # Generate post
            post_content = generate_post_content(data)
            
            # Score tone
            tone_score = score_tone(post_content)
            
            if not post_content:
                # Track non-functional button issue
                track_error(
                    Exception("Generate post produced no output"),
                    context={
                        'module': 'creative_studio',
                        'operation': 'generate_post',
                        'input_data': data
                    },
                    severity=ErrorSeverity.WARNING
                )
                return jsonify({"error": "No content generated"}), 500
            
            return jsonify({
                "content": post_content,
                "tone_score": tone_score
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
```

## Media Generator Module

```python
@app.route('/api/generate-media', methods=['POST'])
def generate_media():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        try:
            # Get AWS region
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            # Initialize Bedrock client
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # Generate image
            response = bedrock_client.invoke_model(
                modelId='amazon.titan-image-generator-v1',
                body=json.dumps({
                    "textToImageParams": {"text": prompt},
                    "taskType": "TEXT_IMAGE",
                    "imageGenerationConfig": {
                        "numberOfImages": 1,
                        "quality": "standard",
                        "height": 1024,
                        "width": 1024
                    }
                })
            )
            
            # Process response
            result = json.loads(response['body'].read())
            
            return jsonify({
                "success": True,
                "image": result['images'][0]
            })
            
        except Exception as aws_error:
            # Track AWS-specific error (catches region mismatch)
            track_aws_error(
                aws_error,
                service='bedrock',
                operation='invoke_model',
                region=aws_region,
                model_id='amazon.titan-image-generator-v1'
            )
            return jsonify({"error": f"Image generation failed: {str(aws_error)}"}), 500
    
    except Exception as e:
        track_error(e, context={
            'module': 'media_generator',
            'endpoint': '/api/generate-media'
        })
        return jsonify({"error": "Request failed"}), 500
```

## Calendar Module

```python
@app.route('/api/calendar/posts', methods=['GET', 'POST', 'PUT', 'DELETE'])
def calendar_posts():
    try:
        if request.method == 'POST':
            # Create post
            data = request.json
            # ... create logic ...
            
        elif request.method == 'PUT':
            # Update/reschedule post
            data = request.json
            post_id = data.get('id')
            # ... update logic ...
            
        elif request.method == 'DELETE':
            # Delete post
            post_id = request.args.get('id')
            # ... delete logic ...
            
        else:
            # GET - list posts
            # ... list logic ...
            pass
    
    except Exception as e:
        track_error(e, context={
            'module': 'calendar',
            'endpoint': '/api/calendar/posts',
            'method': request.method
        })
        return jsonify({"error": "Calendar operation failed"}), 500
```

## Frontend Integration (React)

### Create Error Boundary

```typescript
// frontend/src/components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  componentName: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Send error to backend
    fetch('/api/track-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error_type: 'UIError',
        message: error.message,
        component: this.props.componentName,
        stack: error.stack,
        componentStack: errorInfo.componentStack
      })
    }).catch(console.error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>We've been notified and are working on a fix.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Wrap Components

```typescript
// frontend/src/components/modules/CreativeStudio.tsx
import ErrorBoundary from '../ErrorBoundary';

function CreativeStudio() {
  return (
    <ErrorBoundary componentName="CreativeStudio">
      {/* Component content */}
    </ErrorBoundary>
  );
}
```

### Track API Errors

```typescript
// frontend/src/lib/api.ts
async function apiCall(endpoint: string, options: RequestInit = {}) {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      // Track API error
      await fetch('/api/track-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error_type: 'APIError',
          message: `API call failed: ${response.status}`,
          endpoint,
          method: options.method || 'GET',
          status_code: response.status
        })
      });
      
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    // Track network error
    await fetch('/api/track-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error_type: 'NetworkError',
        message: error.message,
        endpoint
      })
    }).catch(console.error);
    
    throw error;
  }
}
```

## Backend Error Tracking Endpoint

Add this endpoint to receive frontend errors:

```python
@app.route('/api/track-error', methods=['POST'])
def track_frontend_error():
    """Receive and track errors from frontend."""
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
            'user_agent': request.headers.get('User-Agent')
        }
        
        track_error(exception, context=context)
        
        return jsonify({"success": True}), 200
    
    except Exception as e:
        logger.error(f"Failed to track frontend error: {e}")
        return jsonify({"error": "Failed to track error"}), 500
```

## Testing Error Tracking

```python
# backend/tests/integration/test_error_tracking_integration.py
import pytest
from app import app
from monitoring.error_tracker import get_error_tracker

@pytest.mark.integration
def test_upload_error_tracking():
    """Test that upload errors are tracked."""
    tracker = get_error_tracker()
    initial_count = len(tracker.error_history)
    
    with app.test_client() as client:
        # Trigger error by uploading without file
        response = client.post('/api/brand-assets/upload')
        
        # Error should be tracked
        assert len(tracker.error_history) > initial_count
```

## Viewing Errors

### Local Development

Errors are logged to console with full context:

```
============================================================
ERROR CAPTURED
============================================================
Timestamp: 2024-01-15T10:30:00Z
Type: SupabaseStorageError
Module: brand_asset_upload
Severity: error
Message: Bucket not found: brand-assets

Stack Trace:
Traceback (most recent call last):
  ...

Context:
  operation: upload
  bucket_name: brand-assets
  file_name: logo_123.png
  supabase_url: https://xxx.supabase.co
============================================================
```

### Production (Sentry)

1. Set `SENTRY_DSN` environment variable
2. Errors automatically sent to Sentry with full context
3. View in Sentry dashboard with filtering by module, severity, etc.

## Best Practices

1. **Always track errors in try-except blocks**
2. **Use specific tracking functions** (track_supabase_error, track_aws_error, etc.)
3. **Include relevant context** (operation, parameters, user info)
4. **Set appropriate severity** (ERROR for failures, WARNING for degraded, CRITICAL for system-wide)
5. **Don't log sensitive data** (passwords, API keys, PII)
6. **Test error tracking** in integration tests

## Next Steps

1. Add error tracking to all Flask routes
2. Wrap React components in ErrorBoundary
3. Configure Sentry DSN for production
4. Set up alert notifications (email, Slack)
5. Create error dashboards in Sentry
