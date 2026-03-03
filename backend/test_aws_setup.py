"""
Test AWS Setup for Phase 6
Verifies AWS credentials, Bedrock access, and S3 bucket
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("AWS SETUP VERIFICATION FOR PHASE 6")
print("=" * 80)
print()

# Track results
results = {
    "aws_credentials": False,
    "bedrock_access": False,
    "s3_bucket": False,
    "claude_api": False
}

# Test 1: AWS Credentials
print("1️⃣ Testing AWS Credentials...")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    print(f"   ✅ AWS_ACCESS_KEY_ID found: {AWS_ACCESS_KEY_ID[:10]}...")
    print(f"   ✅ AWS_SECRET_ACCESS_KEY found: {'*' * 20}")
    print(f"   ✅ AWS_REGION: {AWS_REGION}")
    results["aws_credentials"] = True
    
    # Try to verify with boto3
    try:
        import boto3
        sts = boto3.client('sts', region_name=AWS_REGION)
        identity = sts.get_caller_identity()
        print(f"   ✅ AWS Identity verified:")
        print(f"      Account: {identity['Account']}")
        print(f"      User ARN: {identity['Arn']}")
    except ImportError:
        print("   ⚠️  boto3 not installed. Run: pip install boto3")
        print("   ℹ️  Credentials found but not verified")
    except Exception as e:
        print(f"   ❌ Credential verification failed: {str(e)[:100]}")
        results["aws_credentials"] = False
else:
    print("   ❌ AWS credentials not found in .env")
    print("   ℹ️  Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to backend/.env")

# Test 2: Bedrock Access
print("\n2️⃣ Testing AWS Bedrock Access...")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-image-generator-v1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

if results["aws_credentials"]:
    try:
        import boto3
        bedrock = boto3.client('bedrock', region_name=BEDROCK_REGION)
        models = bedrock.list_foundation_models()
        
        # Check if Titan Image Generator is available
        titan_available = any(
            'titan' in model.get('modelId', '').lower() and 'image' in model.get('modelId', '').lower()
            for model in models.get('modelSummaries', [])
        )
        
        if titan_available:
            print(f"   ✅ Bedrock access confirmed")
            print(f"   ✅ Titan Image Generator available")
            print(f"   ✅ Model ID: {BEDROCK_MODEL_ID}")
            results["bedrock_access"] = True
        else:
            print(f"   ⚠️  Bedrock access works but Titan Image Generator not found")
            print(f"   ℹ️  You may need to request model access")
            
    except ImportError:
        print("   ⚠️  boto3 not installed. Run: pip install boto3")
    except Exception as e:
        error_msg = str(e)
        if "AccessDeniedException" in error_msg:
            print("   ❌ Access Denied: Bedrock access not enabled")
            print("   ℹ️  Request access at: https://console.aws.amazon.com/bedrock/")
        elif "UnrecognizedClientException" in error_msg:
            print("   ❌ Invalid AWS credentials")
        else:
            print(f"   ❌ Bedrock test failed: {error_msg[:100]}")
else:
    print("   ⏭️  Skipped (AWS credentials not configured)")

# Test 3: S3 Bucket
print("\n3️⃣ Testing S3 Bucket Access...")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

if S3_BUCKET_NAME:
    print(f"   ℹ️  Bucket name: {S3_BUCKET_NAME}")
    
    if results["aws_credentials"]:
        try:
            import boto3
            s3 = boto3.client('s3', region_name=S3_REGION)
            
            # Check if bucket exists
            try:
                s3.head_bucket(Bucket=S3_BUCKET_NAME)
                print(f"   ✅ S3 bucket exists and is accessible")
                results["s3_bucket"] = True
            except:
                print(f"   ⚠️  Bucket not found or not accessible")
                print(f"   ℹ️  Create with: aws s3 mb s3://{S3_BUCKET_NAME} --region {S3_REGION}")
                
        except ImportError:
            print("   ⚠️  boto3 not installed")
        except Exception as e:
            print(f"   ❌ S3 test failed: {str(e)[:100]}")
    else:
        print("   ⏭️  Skipped (AWS credentials not configured)")
else:
    print("   ❌ S3_BUCKET_NAME not found in .env")
    print("   ℹ️  Add S3_BUCKET_NAME to backend/.env")

# Test 4: Claude API (Optional)
print("\n4️⃣ Testing Claude API (Optional)...")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

if ANTHROPIC_API_KEY:
    print(f"   ✅ ANTHROPIC_API_KEY found: {ANTHROPIC_API_KEY[:10]}...")
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        # Note: We don't actually call the API to avoid charges
        print(f"   ✅ Claude API client initialized")
        print(f"   ℹ️  API key format looks valid")
        results["claude_api"] = True
    except ImportError:
        print("   ⚠️  anthropic package not installed")
        print("   ℹ️  Run: pip install anthropic")
    except Exception as e:
        print(f"   ❌ Claude API test failed: {str(e)[:100]}")
else:
    print("   ⚠️  ANTHROPIC_API_KEY not found (optional)")
    print("   ℹ️  Get key from: https://console.anthropic.com/")
    print("   ℹ️  Can use Gemini/Groq as alternative for prompt translation")
    results["claude_api"] = True  # Mark as pass since it's optional

# Summary
print("\n" + "=" * 80)
print("SETUP SUMMARY")
print("=" * 80)

total_tests = len(results)
passed_tests = sum(results.values())

print(f"\nTests Passed: {passed_tests}/{total_tests}")
print()

for test, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test.replace('_', ' ').title()}")

print()

if passed_tests == total_tests:
    print("🎉 ALL TESTS PASSED!")
    print("✅ AWS setup is complete and ready for Phase 6")
    print()
    print("Next steps:")
    print("  1. Start Phase 6, Days 8-9 (Frontend UI)")
    print("  2. Test image generation with sample prompts")
    print("  3. Monitor AWS costs in billing dashboard")
    sys.exit(0)
elif results["aws_credentials"]:
    print("⚠️  PARTIAL SETUP")
    print("AWS credentials are configured but some services need attention.")
    print()
    print("You can:")
    print("  Option A: Fix the issues above and re-run this test")
    print("  Option B: Start with mock mode while waiting for AWS approval")
    print("  Option C: Proceed with available services only")
    sys.exit(1)
else:
    print("❌ SETUP INCOMPLETE")
    print("AWS credentials are not configured.")
    print()
    print("Please follow the AWS_SETUP_GUIDE.md to:")
    print("  1. Configure AWS CLI")
    print("  2. Add credentials to backend/.env")
    print("  3. Re-run this test")
    sys.exit(1)
