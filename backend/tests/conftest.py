"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv('.env.test', override=True)


@pytest.fixture(scope="session")
def test_env():
    """Provide test environment configuration."""
    return {
        "SUPABASE_URL": os.getenv("TEST_SUPABASE_URL", os.getenv("SUPABASE_URL")),
        "SUPABASE_KEY": os.getenv("TEST_SUPABASE_KEY", os.getenv("SUPABASE_KEY")),
        "AWS_REGION": os.getenv("TEST_AWS_REGION", "us-east-1"),
        "CHROMADB_PATH": os.getenv("TEST_CHROMADB_PATH", "./test_chromadb"),
    }


@pytest.fixture(scope="function")
def mock_supabase(mocker):
    """Mock Supabase client for unit tests."""
    mock_client = mocker.MagicMock()
    mock_client.storage.from_.return_value.upload.return_value = {
        "Key": "test-file.png",
        "Id": "test-id-123"
    }
    return mock_client


@pytest.fixture(scope="function")
def mock_aws_bedrock(mocker):
    """Mock AWS Bedrock client for unit tests."""
    mock_client = mocker.MagicMock()
    mock_client.invoke_model.return_value = {
        "body": mocker.MagicMock(read=lambda: b'{"images": ["base64data"]}')
    }
    return mock_client


@pytest.fixture(scope="function")
def mock_chromadb(mocker):
    """Mock ChromaDB client for unit tests."""
    mock_client = mocker.MagicMock()
    mock_collection = mocker.MagicMock()
    mock_collection.query.return_value = {
        "documents": [["test document"]],
        "metadatas": [[{"source": "test"}]],
        "distances": [[0.5]]
    }
    mock_client.get_or_create_collection.return_value = mock_collection
    return mock_client


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment between tests."""
    yield
    # Cleanup code here if needed
