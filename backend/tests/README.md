# Backend Testing Guide

## Overview

This directory contains all backend tests organized by type:
- `unit/` - Fast, isolated unit tests
- `integration/` - Tests that verify component interactions
- `e2e/` - End-to-end tests for complete workflows

## Setup

1. Install test dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure test environment:
```bash
cp .env.test.example .env.test
# Edit .env.test with your test credentials
```

## Running Tests

### All tests
```bash
pytest
```

### Unit tests only
```bash
pytest -m unit
```

### Integration tests only
```bash
pytest -m integration
```

### With coverage report
```bash
pytest --cov=. --cov-report=html
```

### Specific test file
```bash
pytest tests/unit/test_configuration_validator.py
```

## Test Structure

Each test file should follow this pattern:

```python
import pytest

@pytest.mark.unit
def test_function_name(mock_dependency):
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Fixtures

Common fixtures are defined in `conftest.py`:
- `test_env` - Test environment configuration
- `mock_supabase` - Mocked Supabase client
- `mock_aws_bedrock` - Mocked AWS Bedrock client
- `mock_chromadb` - Mocked ChromaDB client

## Best Practices

1. **Isolation**: Unit tests should mock all external dependencies
2. **Speed**: Unit tests should run in < 1 second
3. **Clarity**: Use descriptive test names that explain what is being tested
4. **Coverage**: Aim for 80%+ code coverage
5. **Cleanup**: Always clean up test data in integration tests
