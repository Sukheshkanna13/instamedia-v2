"""
Unit tests for ErrorTracker.

Tests error capture, context building, metrics, and Sentry integration.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from monitoring.error_tracker import (
    ErrorTracker,
    ErrorSeverity,
    ErrorEvent,
    ErrorMetrics,
    track_error,
    track_supabase_error,
    track_aws_error,
    track_api_error,
    track_ui_error
)


@pytest.mark.unit
class TestErrorTracker:
    """Test suite for ErrorTracker."""
    
    def test_error_tracker_initialization(self):
        """Test ErrorTracker initializes correctly."""
        tracker = ErrorTracker(enable_sentry=False)
        
        assert tracker.enable_sentry is False
        assert tracker.error_history == []
        assert tracker.max_history == 1000
    
    def test_capture_exception_basic(self):
        """Test capturing a basic exception."""
        tracker = ErrorTracker(enable_sentry=False)
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.capture_exception(e, context={'module': 'test'})
        
        assert len(tracker.error_history) == 1
        error = tracker.error_history[0]
        assert error.error_type == 'ValueError'
        assert error.message == 'Test error'
        assert error.module == 'test'
        assert error.severity == ErrorSeverity.ERROR.value
    
    def test_capture_exception_with_context(self):
        """Test capturing exception with full context."""
        tracker = ErrorTracker(enable_sentry=False)
        
        context = {
            'module': 'brand_upload',
            'request': {
                'method': 'POST',
                'url': '/api/upload',
                'body': {'file': 'test.png'}
            },
            'user': {
                'session_id': 'abc123',
                'user_id': 'user_456'
            }
        }
        
        try:
            raise RuntimeError("Upload failed")
        except RuntimeError as e:
            tracker.capture_exception(e, context=context)
        
        assert len(tracker.error_history) == 1
        error = tracker.error_history[0]
        assert error.module == 'brand_upload'
        assert 'request' in error.context
        assert 'user' in error.context
        assert 'environment' in error.context
    
    def test_capture_exception_critical_severity(self):
        """Test capturing critical exception triggers alert."""
        tracker = ErrorTracker(enable_sentry=False)
        
        with patch.object(tracker, 'send_alert') as mock_alert:
            try:
                raise Exception("Critical failure")
            except Exception as e:
                tracker.capture_exception(e, severity=ErrorSeverity.CRITICAL)
            
            mock_alert.assert_called_once()
            assert mock_alert.call_args[0][0] == ErrorSeverity.CRITICAL.value
    
    def test_log_error_without_exception(self):
        """Test logging error without exception object."""
        tracker = ErrorTracker(enable_sentry=False)
        
        tracker.log_error(
            error_type='ValidationError',
            message='Invalid input',
            context={'module': 'validation', 'field': 'email'}
        )
        
        assert len(tracker.error_history) == 1
        error = tracker.error_history[0]
        assert error.error_type == 'ValidationError'
        assert error.message == 'Invalid input'
        assert error.context['field'] == 'email'
    
    def test_error_history_max_size(self):
        """Test error history maintains max size."""
        tracker = ErrorTracker(enable_sentry=False)
        tracker.max_history = 10  # Set small limit for testing
        
        # Add more errors than max
        for i in range(15):
            tracker.log_error('TestError', f'Error {i}')
        
        assert len(tracker.error_history) == 10
        # Should keep most recent errors
        assert tracker.error_history[-1].message == 'Error 14'
    
    def test_get_error_metrics_empty(self):
        """Test getting metrics when no errors."""
        tracker = ErrorTracker(enable_sentry=False)
        
        metrics = tracker.get_error_metrics()
        
        assert metrics.total_errors == 0
        assert metrics.error_rate == 0.0
        assert metrics.errors_by_type == {}
        assert metrics.errors_by_module == {}
        assert metrics.recent_errors == []
    
    def test_get_error_metrics_with_errors(self):
        """Test getting metrics with multiple errors."""
        tracker = ErrorTracker(enable_sentry=False)
        
        # Add various errors
        tracker.log_error('ValueError', 'Error 1', {'module': 'module_a'})
        tracker.log_error('ValueError', 'Error 2', {'module': 'module_a'})
        tracker.log_error('TypeError', 'Error 3', {'module': 'module_b'})
        
        metrics = tracker.get_error_metrics()
        
        assert metrics.total_errors == 3
        assert metrics.errors_by_type['ValueError'] == 2
        assert metrics.errors_by_type['TypeError'] == 1
        assert metrics.errors_by_module['module_a'] == 2
        assert metrics.errors_by_module['module_b'] == 1
        assert len(metrics.recent_errors) == 3
    
    def test_build_error_context(self, monkeypatch):
        """Test building complete error context."""
        monkeypatch.setenv('AWS_REGION', 'us-east-1')
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        monkeypatch.setenv('SUPABASE_BUCKET_NAME', 'brand-assets')
        
        tracker = ErrorTracker(enable_sentry=False)
        
        exception = ValueError("Test")
        context = {'module': 'test', 'custom_field': 'value'}
        
        result = tracker._build_error_context(exception, context)
        
        assert 'environment' in result
        assert result['environment']['aws_region'] == 'us-east-1'
        assert result['environment']['supabase_bucket'] == 'brand-assets'
        assert 'exception' in result
        assert result['exception']['type'] == 'ValueError'
        assert result['custom_field'] == 'value'
    
    def test_send_alert(self, caplog):
        """Test sending alert logs correctly."""
        tracker = ErrorTracker(enable_sentry=False)
        
        tracker.send_alert('critical', 'System failure')
        
        # Check that alert was logged
        assert any('ALERT' in record.message for record in caplog.records)
        assert any('System failure' in record.message for record in caplog.records)
    
    @patch('monitoring.error_tracker.sentry_sdk')
    def test_sentry_integration_enabled(self, mock_sentry, monkeypatch):
        """Test Sentry integration when enabled."""
        monkeypatch.setenv('SENTRY_DSN', 'https://test@sentry.io/123')
        
        # Mock Sentry SDK availability
        with patch('monitoring.error_tracker.SENTRY_AVAILABLE', True):
            tracker = ErrorTracker(enable_sentry=True)
            
            # Sentry init should have been called
            mock_sentry.init.assert_called_once()
    
    def test_sentry_integration_disabled(self):
        """Test Sentry integration when disabled."""
        tracker = ErrorTracker(enable_sentry=False)
        
        assert tracker.enable_sentry is False
        
        # Should still work without Sentry
        try:
            raise ValueError("Test")
        except ValueError as e:
            tracker.capture_exception(e)
        
        assert len(tracker.error_history) == 1


@pytest.mark.unit
class TestErrorTrackingHelpers:
    """Test helper functions for error tracking."""
    
    def test_track_error(self):
        """Test track_error convenience function."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            track_error(e, context={'module': 'test'})
        
        # Should have created error in global tracker
        from monitoring.error_tracker import get_error_tracker
        tracker = get_error_tracker()
        assert len(tracker.error_history) > 0
    
    def test_track_supabase_error(self, monkeypatch):
        """Test tracking Supabase-specific errors."""
        monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
        
        try:
            raise Exception("Bucket not found")
        except Exception as e:
            track_supabase_error(
                e,
                operation='upload',
                bucket_name='brand-assets',
                file_name='test.png'
            )
        
        from monitoring.error_tracker import get_error_tracker
        tracker = get_error_tracker()
        
        # Find the Supabase error
        supabase_errors = [err for err in tracker.error_history 
                          if err.module == 'supabase_storage']
        assert len(supabase_errors) > 0
        
        error = supabase_errors[-1]
        assert error.context['operation'] == 'upload'
        assert error.context['bucket_name'] == 'brand-assets'
        assert error.context['file_name'] == 'test.png'
    
    def test_track_aws_error(self, monkeypatch):
        """Test tracking AWS-specific errors."""
        monkeypatch.setenv('AWS_REGION', 'us-east-1')
        
        try:
            raise Exception("Region mismatch")
        except Exception as e:
            track_aws_error(
                e,
                service='bedrock',
                operation='invoke_model',
                region='eu-north-1',
                model_id='amazon.titan-image-generator-v1'
            )
        
        from monitoring.error_tracker import get_error_tracker
        tracker = get_error_tracker()
        
        # Find the AWS error
        aws_errors = [err for err in tracker.error_history 
                     if err.module == 'aws_bedrock']
        assert len(aws_errors) > 0
        
        error = aws_errors[-1]
        assert error.context['service'] == 'bedrock'
        assert error.context['operation'] == 'invoke_model'
        assert error.context['region'] == 'eu-north-1'
    
    def test_track_api_error(self):
        """Test tracking API errors."""
        try:
            raise Exception("API call failed")
        except Exception as e:
            track_api_error(
                e,
                endpoint='/api/ideate',
                method='POST',
                status_code=500,
                query_params={'prompt': 'test'}
            )
        
        from monitoring.error_tracker import get_error_tracker
        tracker = get_error_tracker()
        
        # Find the API error
        api_errors = [err for err in tracker.error_history 
                     if err.module == 'api']
        assert len(api_errors) > 0
        
        error = api_errors[-1]
        assert error.context['endpoint'] == '/api/ideate'
        assert error.context['method'] == 'POST'
        assert error.context['status_code'] == 500
    
    def test_track_ui_error(self):
        """Test tracking UI component errors."""
        try:
            raise Exception("Component render failed")
        except Exception as e:
            track_ui_error(
                e,
                component='CreativeStudio',
                props={'mode': 'generate'}
            )
        
        from monitoring.error_tracker import get_error_tracker
        tracker = get_error_tracker()
        
        # Find the UI error
        ui_errors = [err for err in tracker.error_history 
                    if err.module == 'ui']
        assert len(ui_errors) > 0
        
        error = ui_errors[-1]
        assert error.context['component'] == 'CreativeStudio'
        assert error.context['props']['mode'] == 'generate'


@pytest.mark.unit
class TestErrorEvent:
    """Test ErrorEvent dataclass."""
    
    def test_error_event_creation(self):
        """Test creating an ErrorEvent."""
        event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_type='ValueError',
            message='Test error',
            module='test_module',
            severity='error',
            stack_trace='Traceback...',
            context={'key': 'value'}
        )
        
        assert event.error_type == 'ValueError'
        assert event.message == 'Test error'
        assert event.module == 'test_module'
        assert event.severity == 'error'
        assert event.context['key'] == 'value'


@pytest.mark.unit
class TestErrorMetrics:
    """Test ErrorMetrics dataclass."""
    
    def test_error_metrics_creation(self):
        """Test creating ErrorMetrics."""
        metrics = ErrorMetrics(
            total_errors=10,
            error_rate=0.5,
            errors_by_type={'ValueError': 5, 'TypeError': 5},
            errors_by_module={'module_a': 7, 'module_b': 3},
            recent_errors=[]
        )
        
        assert metrics.total_errors == 10
        assert metrics.error_rate == 0.5
        assert metrics.errors_by_type['ValueError'] == 5
        assert metrics.errors_by_module['module_a'] == 7
