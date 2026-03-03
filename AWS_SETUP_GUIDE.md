# AWS Setup Guide for Phase 6

**Purpose**: Configure AWS credentials for Bedrock and S3 access  
**Date**: March 2, 2026  
**For**: Phase 6 - Multi-Modal Creative Studio

---

## 🎯 What You Need

For Phase 6, you need:
1. **AWS Account** (with Bedrock access)
2. **IAM User** with appropriate permissions
3. **Access Keys** (Access Key ID + Secret Access Key)
4. **S3 Bucket** for storing generated images
5. **Bedrock Access** (may require approval)

---

## 📋 Step-by-Step Setup

### Step 1: Check Your AWS Account Type

You mentioned you have **AWS Builder ID**. Let's verify what access you have:

```bash
# Check if AWS CLI is installed
aws --version

# If not installed, install it:
# macOS:
brew install awscli

# Or download from: https://aws.amazon.com/cli/
```

---

### Step 2: Configure AWS CLI

**Option A: If you have IAM User credentials**

Run this command and I'll guide you through the prompts:

```bash
aws configure
```

You'll be asked for:
1. **AWS Access Key ID**: (from IAM console)
2. **AWS Secret Access Key**: (from IAM console)
3. **Default region**: `us-east-1` (recommended for Bedrock)
4. **Default output format**: `json`

**Option B: If you have AWS Builder ID (SSO)**

```bash
aws configure sso
```

You'll be asked for:
1. **SSO start URL**: Your organization's SSO URL
2. **SSO Region**: Usually `us-east-1`
3. **SSO registration scopes**: `sso:account:access`

---

### Step 3: Verify Your Credentials

After configuring, test your access:

```bash
# Test basic AWS access
aws sts get-caller-identity

# This should return your account info:
# {
#     "UserId": "...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/yourname"
# }
```

---

### Step 4: Check Bedrock Access

AWS Bedrock requires special access. Check if you have it:

```bash
# List available Bedrock models
aws bedrock list-foundation-models --region us-east-1

# If this works, you have Bedrock access!
# If you get an error, you need to request access (see Step 5)
```

---

### Step 5: Request Bedrock Access (If Needed)

If you don't have Bedrock access yet:

1. **Go to AWS Console**: https://console.aws.amazon.com/bedrock/
2. **Click "Get Started"** or "Request Access"
3. **Select Models**:
   - ✅ Amazon Titan Image Generator G1
   - ✅ Anthropic Claude 3 Haiku (for prompt translation)
4. **Submit Request** (usually approved within 24-48 hours)

**Alternative**: Use AWS Free Tier models while waiting for approval

---

### Step 6: Create S3 Bucket

Create a bucket for storing generated images:

```bash
# Create S3 bucket (replace with your preferred name)
aws s3 mb s3://instamedia-generated-content --region us-east-1

# Verify bucket created
aws s3 ls

# Set bucket policy for public read (optional, for sharing images)
# We'll configure this later if needed
```

---

### Step 7: Get Your Credentials

Now let's get the credentials to add to your `.env` file:

```bash
# View your configured credentials
cat ~/.aws/credentials

# This will show:
# [default]
# aws_access_key_id = AKIA...
# aws_secret_access_key = ...

# View your region
cat ~/.aws/config

# This will show:
# [default]
# region = us-east-1
```

---

## 🔐 Adding Credentials to .env

Once you have your credentials, add them to `backend/.env`:

```bash
# Open .env file
nano backend/.env

# Or use your preferred editor
```

Add these lines:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...your_access_key...
AWS_SECRET_ACCESS_KEY=...your_secret_key...
AWS_REGION=us-east-1

# AWS Bedrock
BEDROCK_MODEL_ID=amazon.titan-image-generator-v1
BEDROCK_REGION=us-east-1

# S3 Storage
S3_BUCKET_NAME=instamedia-generated-content
S3_REGION=us-east-1

# Claude API (for prompt translation)
ANTHROPIC_API_KEY=sk-ant-...your_claude_key...
```

---

## 🧪 Test Your Setup

Let me create a test script for you:

```bash
# Run this test script
python backend/test_aws_setup.py
```

This will verify:
- ✅ AWS credentials are valid
- ✅ Bedrock access is working
- ✅ S3 bucket is accessible
- ✅ Claude API key is valid

---

## 🚨 Troubleshooting

### Issue 1: "Unable to locate credentials"

**Solution**:
```bash
# Check if credentials file exists
ls -la ~/.aws/

# If not, run aws configure again
aws configure
```

### Issue 2: "Access Denied" for Bedrock

**Solution**:
- You need to request Bedrock access (see Step 5)
- Or use IAM user with Bedrock permissions

### Issue 3: "Bucket already exists"

**Solution**:
```bash
# Use a different bucket name
aws s3 mb s3://instamedia-generated-content-yourname --region us-east-1
```

### Issue 4: "Region not supported"

**Solution**:
- Bedrock is only available in certain regions
- Use `us-east-1` or `us-west-2`

---

## 📝 What to Share With Me

Once you've completed the setup, share:

1. **Confirmation that AWS CLI is configured**:
   ```bash
   aws sts get-caller-identity
   ```
   (Share the output - it's safe, doesn't contain secrets)

2. **Bedrock access status**:
   ```bash
   aws bedrock list-foundation-models --region us-east-1 2>&1 | head -5
   ```
   (Share if it works or shows error)

3. **S3 bucket name**:
   ```bash
   aws s3 ls
   ```
   (Share the bucket name you created)

4. **Confirm .env is updated**:
   ```bash
   grep "AWS_ACCESS_KEY_ID" backend/.env | cut -c1-30
   ```
   (This shows first 30 chars only - safe to share)

---

## 🔒 Security Best Practices

### DO:
- ✅ Keep credentials in `.env` file (already in `.gitignore`)
- ✅ Use IAM users with minimal permissions
- ✅ Rotate access keys regularly
- ✅ Enable MFA on your AWS account

### DON'T:
- ❌ Commit `.env` to git
- ❌ Share credentials in chat/email
- ❌ Use root account credentials
- ❌ Give overly broad permissions

---

## 📊 IAM Permissions Needed

If you're creating an IAM user, it needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::instamedia-generated-content",
        "arn:aws:s3:::instamedia-generated-content/*"
      ]
    }
  ]
}
```

---

## 🎯 Quick Start Commands

Run these commands in order:

```bash
# 1. Check AWS CLI
aws --version

# 2. Configure credentials
aws configure

# 3. Test access
aws sts get-caller-identity

# 4. Check Bedrock
aws bedrock list-foundation-models --region us-east-1

# 5. Create S3 bucket
aws s3 mb s3://instamedia-generated-content-$(whoami) --region us-east-1

# 6. List buckets
aws s3 ls

# 7. Update .env file
echo "AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)" >> backend/.env
echo "AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)" >> backend/.env
echo "AWS_REGION=us-east-1" >> backend/.env
echo "S3_BUCKET_NAME=instamedia-generated-content-$(whoami)" >> backend/.env
```

---

## ✅ Checklist

Before proceeding to Phase 6 implementation:

- [ ] AWS CLI installed and configured
- [ ] Credentials verified with `aws sts get-caller-identity`
- [ ] Bedrock access confirmed (or requested)
- [ ] S3 bucket created
- [ ] `.env` file updated with credentials
- [ ] Test script passes
- [ ] Claude API key obtained (if using)

---

## 🚀 Next Steps

Once setup is complete:

1. Run the test script to verify everything works
2. Start Phase 6, Days 8-9 (Frontend UI)
3. Test image generation with sample prompts
4. Monitor AWS costs in billing dashboard

---

## 💡 Alternative: Use Mock Mode First

If AWS setup takes time, we can:

1. **Build frontend UI first** (Days 8-9) with mock data
2. **Implement translation layer** (Days 10-11) with mock outputs
3. **Add AWS integration later** (Days 12-13) when credentials are ready

This way, we don't block progress!

---

**Ready to proceed?** Let me know:
1. If you need help with any specific step
2. Your current AWS setup status
3. If you want to start with mock mode while setting up AWS

