"""
Unit tests for ConfigurationValidator.

Tests validation of environment variables, AWS config, Supabase config,
and health checks for all services.
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from validation.configuration_validator import (
    ConfigurationValidator,
    ValidationResult,
    ValidationError,
    ServiceHealth,
    HealthCheckResults
)


@pytest.mark.unit
class TestConfigurationValidator:
    """Test suite for ConfigurationValidator."""
    
    def test_validation_result_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult(is_valid=True)
        result.add_error('TEST_VAR', 'Test error', 'expected', 'actual')
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field == 'TEST_VAR'
        assert result.errors[0].message == 'Test error'
    
    def test_validation_result_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult(is_valid=True)
        result.add_warning('Test warning')
        
        assert result.is_valid is True  # Warnings don't affect validity
        assert len(result.warnings) == 1
        assert result.warnings[0] == 'Test warning'
    
    def test_validate_environment_variables_all_present(self, monkeypatch):
        """Test validation passes when all required env vars are present."""
        # Set all required environment variables
        required_vars = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key',
            'AWS_REGION': 'us-east-1',
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'GEMINI_API_KEY': 'test-gemini-key',
        }
        
        for key, value in required_vars.items():
            monkeypatch.setenv(key, value)
        
        validator = ConfigurationValidator()
        result = validator._validate_environment_variables()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_environment_variables_missing(self, monkeypatch):
        """Test validation fails when required env vars are missing."""
        # Clear all environment variables
        for var in ConfigurationValidator.REQUIRED_ENV_VARS:
            monkeypatch.delenv(var, raising=False)
        
        validator = ConfigurationValidator()
        result = validator._validate_environment_variables()
        
        assert result.is_valid is False
        assert len(result.errors) == len(ConfigurationValidator.REQUIRED_ENV_VARS)
    
    def test_validate_environment_variables_empty(self, monkeypatch):
        """Test validation fails when env vars are empty strings."""
        monkeypatch.setenv('SUPABASE_URL', '')
        monkeypatch.setenv('SUPABASE_KEY', '   ')  # Whitespace only
        
        validator = ConfigurationValidator()
        result = validator._validate_environment_variables()
        
        assert result.is_valid is False
        # Should have errors for empty SUPABASE_URL and SUPABASE_KEY
        error_fields = [e.field for e in result.errors]
        assert 'SUPABASE_URL' in error_fields
        assert 'SUPABASE_KEY' in error_fields
    
    def test_validate_aws_config_region_mismatch(self, monkeypatch):
        """Test detection of AWS region mismatch (the eu-north-1 vs us-east-1 bug)."""
        monkeypatch.setenv('AWS_REGION', 'us-east-1')
        monkeypatch.setenv('AWS_S3_REGION', 'eu-north-1')  # Mismatch!
        monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'test-key')
        monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'test-secret')
        
        validator = ConfigurationValidator()
        result = validator.validate_aws_config()
        
        assert result.is_valid is False
        # Should have error about region mismatch
        error_messages = [e.message for e in result.errors]
        assert any('mismatch' in msg.lower() for msg in error_messages)
    
    def test_validate_aws_config_valid_region(self, monkeypatch):
        """Test validation passes with consistent AWS region."""
        monkeypatch.setenv('AWS_REGION', 'us-east-1')
        monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'test-key')
        monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'test-secret')
        
        validator = ConfigurationValidator()
        
        with patch('boto3.client') as mock_boto:
            mock_client = Mock()
            mock_boto.return_value = mock_client
            
            result = validator.validate_aws_config()
            
            # Should not have region mismatch error
            assert result.is_valid is True or len(result.errors) == 0
    
    @patch('validation.configuration_validator.create_client')
    def test_validate_supabase_config_bucket_not_found(self, mock_create_client, monkeypatch):
        """Test detection of Supabase bucket not found error."""
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        monkeypatch.setenv('SUPABASE_KEY', 'test-key')
        monkeypatch.setenv('SUPABASE_BUCKET_NAME', 'brand-assets')
        
        # Mock Supabase client to raise bucket not found error
        mock_supabase = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.side_effect = Exception("Bucket not found")
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage
        mock_create_client.return_value = mock_supabase
        
        validator = ConfigurationValidator()
        result = validator.validate_supabase_config()
        
        assert result.is_valid is False
        # Should have error about bucket not found
        error_messages = [e.message for e in result.errors]
        assert any('bucket' in msg.lower() and 'not found' in msg.lower() 
                  for msg in error_messages)
    
    @patch('validation.configuration_validator.create_client')
    def test_validate_supabase_config_bucket_accessible(self, mock_create_client, monkeypatch):
        """Test validation passes when Supabase bucket is accessible."""
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        monkeypatch.setenv('SUPABASE_KEY', 'test-key')
        monkeypatch.setenv('SUPABASE_BUCKET_NAME', 'brand-assets')
        
        # Mock Supabase client with accessible bucket
        mock_supabase = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = []  # Empty list is fine
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage
        mock_create_client.return_value = mock_supabase
        
        validator = ConfigurationValidator()
        result = validator.validate_supabase_config()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_api_keys_missing_gemini(self, monkeypatch):
        """Test validation fails when Gemini API key is missing."""
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        
        validator = ConfigurationValidator()
        result = validator.validate_api_keys()
        
        assert result.is_valid is False
        error_fields = [e.field for e in result.errors]
        assert 'GEMINI_API_KEY' in error_fields
    
    def test_validate_api_keys_present(self, monkeypatch):
        """Test validation passes when API keys are present."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-gemini-key')
        
        validator = ConfigurationValidator()
        result = validator.validate_api_keys()
        
        # Should not have error for GEMINI_API_KEY
        error_fields = [e.field for e in result.errors]
        assert 'GEMINI_API_KEY' not in error_fields
    
    @patch('validation.configuration_validator.create_client')
    def test_health_check_supabase_healthy(self, mock_create_client):
        """Test Supabase health check when service is healthy."""
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_KEY'] = 'test-key'
        
        # Mock healthy Supabase
        mock_supabase = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = []
        mock_storage.from_.return_value = mock_bucket
        mock_supabase.storage = mock_storage
        mock_create_client.return_value = mock_supabase
        
        validator = ConfigurationValidator()
        health = validator._check_supabase_health()
        
        assert health.is_healthy is True
        assert health.service_name == 'supabase'
        assert health.response_time > 0
        assert health.error_message is None
    
    @patch('validation.configuration_validator.create_client')
    def test_health_check_supabase_unhealthy(self, mock_create_client):
        """Test Supabase health check when service is unhealthy."""
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_KEY'] = 'test-key'
        
        # Mock unhealthy Supabase
        mock_create_client.side_effect = Exception("Connection failed")
        
        validator = ConfigurationValidator()
        health = validator._check_supabase_health()
        
        assert health.is_healthy is False
        assert health.service_name == 'supabase'
        assert health.error_message is not None
        assert 'Connection failed' in health.error_message
    
    @patch('boto3.client')
    def test_health_check_aws_bedrock_healthy(self, mock_boto_client):
        """Test AWS Bedrock health check when service is healthy."""
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
        
        # Mock healthy AWS Bedrock
        mock_client = Mock()
        mock_client.list_foundation_models.return_value = {'models': []}
        mock_boto_client.return_value = mock_client
        
        validator = ConfigurationValidator()
        health = validator._check_aws_bedrock_health()
        
        assert health.is_healthy is True
        assert health.service_name == 'aws_bedrock'
        assert health.response_time > 0
    
    @patch('chromadb.PersistentClient')
    def test_health_check_chromadb_healthy(self, mock_chromadb):
        """Test ChromaDB health check when service is healthy."""
        # Mock healthy ChromaDB
        mock_client = Mock()
        mock_client.list_collections.return_value = []
        mock_chromadb.return_value = mock_client
        
        validator = ConfigurationValidator()
        health = validator._check_chromadb_health()
        
        assert health.is_healthy is True
        assert health.service_name == 'chromadb'
        assert health.response_time > 0
    
    def test_run_health_checks_all_healthy(self, mocker):
        """Test run_health_checks when all services are healthy."""
        validator = ConfigurationValidator()
        
        # Mock all health check methods to return healthy
        mocker.patch.object(
            validator, '_check_supabase_health',
            return_value=ServiceHealth('supabase', True, 0.1)
        )
        mocker.patch.object(
            validator, '_check_aws_bedrock_health',
            return_value=ServiceHealth('aws_bedrock', True, 0.2)
        )
        mocker.patch.object(
            validator, '_check_chromadb_health',
            return_value=ServiceHealth('chromadb', True, 0.1)
        )
        mocker.patch.object(
            validator, '_check_apify_health',
            return_value=ServiceHealth('apify', True, 0.1)
        )
        
        results = validator.run_health_checks()
        
        assert results.all_healthy is True
        assert len(results.services) == 4
        assert all(s.is_healthy for s in results.services.values())
    
    def test_run_health_checks_some_unhealthy(self, mocker):
        """Test run_health_checks when some services are unhealthy."""
        validator = ConfigurationValidator()
        
        # Mock mixed health status
        mocker.patch.object(
            validator, '_check_supabase_health',
            return_value=ServiceHealth('supabase', True, 0.1)
        )
        mocker.patch.object(
            validator, '_check_aws_bedrock_health',
            return_value=ServiceHealth('aws_bedrock', False, 0.2, 'Connection timeout')
        )
        mocker.patch.object(
            validator, '_check_chromadb_health',
            return_value=ServiceHealth('chromadb', True, 0.1)
        )
        mocker.patch.object(
            validator, '_check_apify_health',
            return_value=ServiceHealth('apify', True, 0.1)
        )
        
        results = validator.run_health_checks()
        
        assert results.all_healthy is False
        assert results.services['aws_bedrock'].is_healthy is False
        assert results.services['aws_bedrock'].error_message == 'Connection timeout'


@pytest.mark.integration
class TestConfigurationValidatorIntegration:
    """Integration tests for ConfigurationValidator with real services."""
    
    def test_validate_all_with_real_env(self):
        """Test validate_all with actual environment variables."""
        # This test will use actual environment variables
        # Skip if not in test environment
        if not os.getenv('TEST_SUPABASE_URL'):
            pytest.skip("Test environment not configured")
        
        validator = ConfigurationValidator()
        result = validator.validate_all()
        
        # Should complete without crashing
        assert isinstance(result, ValidationResult)
        
        # Log results for debugging
        if not result.is_valid:
            for error in result.errors:
                print(f"Validation error: {error.field} - {error.message}")
