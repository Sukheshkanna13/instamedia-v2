# Testing Infrastructure Setup Guide

## Quick Start

This guide helps you set up and run the production-quality testing pipeline.

## Installation

### Backend Testing Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure test environment:**
```bash
cp .env.test .env.test.local
# Edit .env.test.local with your test credentials
```

3. **Run configuration validator:**
```bash
python validate_config.py
```

This will check:
- ✓ All required environment variables are present
- ✓ AWS region consistency (catches eu-north-1 vs us-east-1 mismatch)
- ✓ Supabase bucket accessibility (catches "Bucket not found" error)
- ✓ API key validity
- ✓ Service health (Supabase, AWS Bedrock, ChromaDB, Apify)

4. **Run unit tests:**
```bash
pytest tests/unit/ -v
```

5. **Run tests with coverage:**
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Frontend Testing Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Install Playwright browsers (for e2e tests):**
```bash
npx playwright install
```

3. **Run unit tests:**
```bash
npm test
```

4. **Run tests with UI:**
```bash
npm run test:ui
```

5. **Run e2e tests:**
```bash
npm run test:e2e
```

## Configuration Validation

The configuration validator catches common production errors before they happen:

### What It Checks

1. **Environment Variables**
   - All required variables present (SUPABASE_URL, AWS_REGION, etc.)
   - No empty or whitespace-only values

2. **AWS Configuration**
   - Region consistency across services
   - Valid credentials
   - Catches: "Error parsing the X-Amz-Credential parameter; the region 'eu-north-1' is wrong; expecting 'us-east-1'"

3. **Supabase Configuration**
   - Bucket exists and is accessible
   - Valid credentials
   - Catches: "Bucket not found" 400 errors

4. **API Keys**
   - Gemini API key present
   - Apify API key valid (optional)

5. **Service Health**
   - Supabase connectivity
   - AWS Bedrock availability
   - ChromaDB accessibility
   - Apify service status

### Running Validation

**Before tests:**
```bash
cd backend
python validate_config.py
```

**Before deployment:**
```bash
cd backend
python validate_config.py && echo "✓ Ready to deploy"
```

**In CI/CD:**
```yaml
- name: Validate Configuration
  run: |
    cd backend
    python validate_config.py
```

## Test Structure

### Backend Tests

```
backend/tests/
├── unit/                    # Fast, isolated unit tests
│   ├── test_configuration_validator.py
│   └── ...
├── integration/             # Component interaction tests
│   └── ...
├── e2e/                     # End-to-end workflow tests
│   └── ...
└── conftest.py             # Shared fixtures
```

### Frontend Tests

```
frontend/src/tests/
├── unit/                    # Component unit tests
├── integration/             # API integration tests
├── e2e/                     # User flow tests
├── utils/                   # Test utilities
│   └── test-utils.tsx
└── setup.ts                # Test setup
```

## Running Specific Tests

### Backend

```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/unit/test_configuration_validator.py

# Specific test function
pytest tests/unit/test_configuration_validator.py::test_validate_aws_config_region_mismatch

# With coverage
pytest --cov=. --cov-report=term-missing
```

### Frontend

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Specific test file
npm test -- src/tests/unit/MyComponent.test.tsx

# With coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# E2E with UI
npx playwright test --ui
```

## Troubleshooting

### "Module not found" errors

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Configuration validation fails

1. Check your `.env` file has all required variables
2. Verify AWS region is consistent (use `us-east-1` everywhere)
3. Verify Supabase bucket exists in your Supabase project
4. Test API keys manually

### Tests fail with "Connection refused"

- Ensure services are running (Supabase, AWS credentials configured)
- For unit tests, mocks should prevent this - check test setup
- For integration tests, verify test environment is configured

### Playwright browser installation fails

```bash
# Install specific browser
npx playwright install chromium

# Install all browsers
npx playwright install
```

## Next Steps

1. ✅ Task 1: Testing infrastructure setup - COMPLETE
2. ✅ Task 2: Configuration validator - COMPLETE
3. ⏭️  Task 3: Error tracking system
4. ⏭️  Task 5: Test data management
5. ⏭️  Task 6-11: Module-specific tests

## CI/CD Integration

The configuration validator will be integrated into the CI/CD pipeline to run automatically before deployment:

```yaml
# .github/workflows/test.yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Configuration
        run: |
          cd backend
          pip install -r requirements.txt
          python validate_config.py
      
  test:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Run Tests
        run: |
          cd backend
          pytest --cov=. --cov-fail-under=80
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [React Testing Library](https://testing-library.com/react)
