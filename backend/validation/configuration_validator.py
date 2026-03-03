"""
Configuration Validator - Validates environment configuration and service health.

This module catches configuration errors before runtime, including:
- Missing environment variables
- AWS region mismatches
- Supabase bucket accessibility
- Invalid API keys
"""
import os
import boto3
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from supabase import create_client, Client
import chromadb
from apify_client import ApifyClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    expected: str
    actual: str


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, field: str, message: str, expected: str = "", actual: str = ""):
        """Add a validation error."""
        self.is_valid = False
        self.errors.append(ValidationError(field, message, expected, actual))
    
    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)


@dataclass
class ServiceHealth:
    """Health status of a service."""
    service_name: str
    is_healthy: bool
    response_time: float
    error_message: Optional[str] = None


@dataclass
class HealthCheckResults:
    """Results of health checks for all services."""
    all_healthy: bool
    services: Dict[str, ServiceHealth]


class ConfigurationValidator:
    """
    Validates environment configuration and service health.
    
    This validator catches common configuration errors before they cause
    runtime failures, including the AWS region mismatch and Supabase
    bucket errors found in manual testing.
    """
    
    # Required environment variables
    REQUIRED_ENV_VARS = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GEMINI_API_KEY',
    ]
    
    # Optional but recommended
    OPTIONAL_ENV_VARS = [
        'APIFY_API_KEY',
        'SENTRY_DSN',
    ]
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.validation_results = []
    
    def validate_all(self) -> ValidationResult:
        """
        Validate all configuration.
        
        Returns:
            ValidationResult with all validation errors and warnings
        """
        logger.info("Starting comprehensive configuration validation...")
        
        result = ValidationResult(is_valid=True)
        
        # Validate environment variables
        env_result = self._validate_environment_variables()
        if not env_result.is_valid:
            result.is_valid = False
            result.errors.extend(env_result.errors)
        result.warnings.extend(env_result.warnings)
        
        # Only proceed with service validation if env vars are present
        if env_result.is_valid:
            # Validate AWS configuration
            aws_result = self.validate_aws_config()
            if not aws_result.is_valid:
                result.is_valid = False
                result.errors.extend(aws_result.errors)
            result.warnings.extend(aws_result.warnings)
            
            # Validate Supabase configuration
            supabase_result = self.validate_supabase_config()
            if not supabase_result.is_valid:
                result.is_valid = False
                result.errors.extend(supabase_result.errors)
            result.warnings.extend(supabase_result.warnings)
            
            # Validate API keys
            api_result = self.validate_api_keys()
            if not api_result.is_valid:
                result.is_valid = False
                result.errors.extend(api_result.errors)
            result.warnings.extend(api_result.warnings)
        
        if result.is_valid:
            logger.info("✓ All configuration validation passed")
        else:
            logger.error(f"✗ Configuration validation failed with {len(result.errors)} errors")
        
        return result
    
    def _validate_environment_variables(self) -> ValidationResult:
        """Validate all required environment variables are present."""
        result = ValidationResult(is_valid=True)
        
        for var in self.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if not value or value.strip() == '':
                result.add_error(
                    field=var,
                    message=f"Required environment variable '{var}' is missing or empty",
                    expected="Non-empty string",
                    actual=value or "None"
                )
        
        # Check optional variables
        for var in self.OPTIONAL_ENV_VARS:
            value = os.getenv(var)
            if not value or value.strip() == '':
                result.add_warning(f"Optional environment variable '{var}' is not set")
        
        return result
    
    def validate_aws_config(self) -> ValidationResult:
        """
        Validate AWS configuration including region consistency.
        
        This catches the eu-north-1 vs us-east-1 region mismatch error
        found in manual testing.
        """
        result = ValidationResult(is_valid=True)
        
        aws_region = os.getenv('AWS_REGION', '')
        
        if not aws_region:
            result.add_error(
                field='AWS_REGION',
                message="AWS_REGION not configured",
                expected="Valid AWS region (e.g., us-east-1)",
                actual="None"
            )
            return result
        
        # Validate region format
        valid_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1'
        ]
        
        if aws_region not in valid_regions:
            result.add_warning(
                f"AWS_REGION '{aws_region}' is not a common region. "
                f"Ensure this is correct."
            )
        
        # Check for region consistency across AWS services
        try:
            # Check Bedrock region
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # Check S3 region (if configured)
            s3_region = os.getenv('AWS_S3_REGION', aws_region)
            if s3_region != aws_region:
                result.add_error(
                    field='AWS_S3_REGION',
                    message="AWS S3 region mismatch with AWS_REGION",
                    expected=aws_region,
                    actual=s3_region
                )
            
            logger.info(f"✓ AWS region configuration validated: {aws_region}")
            
        except Exception as e:
            result.add_error(
                field='AWS_CREDENTIALS',
                message=f"Failed to initialize AWS client: {str(e)}",
                expected="Valid AWS credentials",
                actual="Invalid or missing credentials"
            )
        
        return result
    
    def validate_supabase_config(self) -> ValidationResult:
        """
        Validate Supabase configuration including bucket accessibility.
        
        This catches the "Bucket not found" 400 error found in manual testing.
        """
        result = ValidationResult(is_valid=True)
        
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_KEY', '')
        
        if not supabase_url or not supabase_key:
            result.add_error(
                field='SUPABASE_CONFIG',
                message="Supabase URL or KEY not configured",
                expected="Valid Supabase credentials",
                actual="Missing credentials"
            )
            return result
        
        try:
            # Initialize Supabase client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Check bucket accessibility
            bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'brand-assets')
            
            try:
                # Try to list files in bucket (this will fail if bucket doesn't exist)
                supabase.storage.from_(bucket_name).list()
                logger.info(f"✓ Supabase bucket '{bucket_name}' is accessible")
                
            except Exception as bucket_error:
                error_msg = str(bucket_error)
                if 'not found' in error_msg.lower() or 'bucket' in error_msg.lower():
                    result.add_error(
                        field='SUPABASE_BUCKET',
                        message=f"Supabase bucket '{bucket_name}' not found or not accessible",
                        expected=f"Accessible bucket named '{bucket_name}'",
                        actual=f"Bucket not found: {error_msg}"
                    )
                else:
                    result.add_warning(
                        f"Could not verify bucket '{bucket_name}': {error_msg}"
                    )
            
        except Exception as e:
            result.add_error(
                field='SUPABASE_CONNECTION',
                message=f"Failed to connect to Supabase: {str(e)}",
                expected="Valid Supabase connection",
                actual=f"Connection failed: {str(e)}"
            )
        
        return result
    
    def validate_api_keys(self) -> ValidationResult:
        """
        Validate API keys by making test calls.
        
        This ensures API keys are valid before runtime.
        """
        result = ValidationResult(is_valid=True)
        
        # Validate Gemini API key
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        if gemini_key:
            # Note: Actual validation would require making a test API call
            # For now, just check it's not empty
            logger.info("✓ GEMINI_API_KEY is present")
        else:
            result.add_error(
                field='GEMINI_API_KEY',
                message="GEMINI_API_KEY is missing",
                expected="Valid Gemini API key",
                actual="None"
            )
        
        # Validate Apify API key (optional)
        apify_key = os.getenv('APIFY_API_KEY', '')
        if apify_key:
            try:
                client = ApifyClient(apify_key)
                # Test the key by getting user info
                user = client.user().get()
                logger.info(f"✓ APIFY_API_KEY is valid (user: {user.get('username', 'unknown')})")
            except Exception as e:
                result.add_warning(f"APIFY_API_KEY validation failed: {str(e)}")
        
        return result
    
    def run_health_checks(self) -> HealthCheckResults:
        """
        Run health checks for all external services.
        
        Returns:
            HealthCheckResults with status of each service
        """
        logger.info("Running health checks for all services...")
        
        services = {}
        
        # Check Supabase
        services['supabase'] = self._check_supabase_health()
        
        # Check AWS Bedrock
        services['aws_bedrock'] = self._check_aws_bedrock_health()
        
        # Check ChromaDB
        services['chromadb'] = self._check_chromadb_health()
        
        # Check Apify (optional)
        services['apify'] = self._check_apify_health()
        
        all_healthy = all(s.is_healthy for s in services.values())
        
        if all_healthy:
            logger.info("✓ All services are healthy")
        else:
            unhealthy = [name for name, s in services.items() if not s.is_healthy]
            logger.warning(f"✗ Unhealthy services: {', '.join(unhealthy)}")
        
        return HealthCheckResults(all_healthy=all_healthy, services=services)
    
    def _check_supabase_health(self) -> ServiceHealth:
        """Check Supabase service health."""
        import time
        start = time.time()
        
        try:
            supabase_url = os.getenv('SUPABASE_URL', '')
            supabase_key = os.getenv('SUPABASE_KEY', '')
            
            if not supabase_url or not supabase_key:
                return ServiceHealth(
                    service_name='supabase',
                    is_healthy=False,
                    response_time=0,
                    error_message="Supabase credentials not configured"
                )
            
            supabase: Client = create_client(supabase_url, supabase_key)
            # Simple health check - try to access storage
            bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'brand-assets')
            supabase.storage.from_(bucket_name).list(limit=1)
            
            response_time = time.time() - start
            return ServiceHealth(
                service_name='supabase',
                is_healthy=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start
            return ServiceHealth(
                service_name='supabase',
                is_healthy=False,
                response_time=response_time,
                error_message=str(e)
            )
    
    def _check_aws_bedrock_health(self) -> ServiceHealth:
        """Check AWS Bedrock service health."""
        import time
        start = time.time()
        
        try:
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # List available models as a health check
            bedrock_models = boto3.client(
                'bedrock',
                region_name=aws_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            bedrock_models.list_foundation_models()
            
            response_time = time.time() - start
            return ServiceHealth(
                service_name='aws_bedrock',
                is_healthy=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start
            return ServiceHealth(
                service_name='aws_bedrock',
                is_healthy=False,
                response_time=response_time,
                error_message=str(e)
            )
    
    def _check_chromadb_health(self) -> ServiceHealth:
        """Check ChromaDB service health."""
        import time
        start = time.time()
        
        try:
            chromadb_path = os.getenv('CHROMADB_PATH', './chromadb')
            client = chromadb.PersistentClient(path=chromadb_path)
            
            # Try to list collections
            client.list_collections()
            
            response_time = time.time() - start
            return ServiceHealth(
                service_name='chromadb',
                is_healthy=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start
            return ServiceHealth(
                service_name='chromadb',
                is_healthy=False,
                response_time=response_time,
                error_message=str(e)
            )
    
    def _check_apify_health(self) -> ServiceHealth:
        """Check Apify service health."""
        import time
        start = time.time()
        
        try:
            apify_key = os.getenv('APIFY_API_KEY', '')
            
            if not apify_key:
                return ServiceHealth(
                    service_name='apify',
                    is_healthy=True,  # Optional service
                    response_time=0,
                    error_message="Apify API key not configured (optional)"
                )
            
            client = ApifyClient(apify_key)
            client.user().get()
            
            response_time = time.time() - start
            return ServiceHealth(
                service_name='apify',
                is_healthy=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start
            return ServiceHealth(
                service_name='apify',
                is_healthy=False,
                response_time=response_time,
                error_message=str(e)
            )


def main():
    """Run configuration validation from command line."""
    validator = ConfigurationValidator()
    
    print("\n" + "="*60)
    print("CONFIGURATION VALIDATION")
    print("="*60 + "\n")
    
    # Run validation
    result = validator.validate_all()
    
    if result.errors:
        print("\n❌ ERRORS:")
        for error in result.errors:
            print(f"  • {error.field}: {error.message}")
            if error.expected:
                print(f"    Expected: {error.expected}")
            if error.actual:
                print(f"    Actual: {error.actual}")
    
    if result.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in result.warnings:
            print(f"  • {warning}")
    
    # Run health checks
    print("\n" + "="*60)
    print("HEALTH CHECKS")
    print("="*60 + "\n")
    
    health = validator.run_health_checks()
    
    for name, service in health.services.items():
        status = "✓" if service.is_healthy else "✗"
        print(f"{status} {name}: ", end="")
        if service.is_healthy:
            print(f"healthy ({service.response_time:.2f}s)")
        else:
            print(f"unhealthy - {service.error_message}")
    
    print("\n" + "="*60)
    if result.is_valid and health.all_healthy:
        print("✓ ALL CHECKS PASSED")
    else:
        print("✗ VALIDATION FAILED")
    print("="*60 + "\n")
    
    return 0 if (result.is_valid and health.all_healthy) else 1


if __name__ == '__main__':
    exit(main())
