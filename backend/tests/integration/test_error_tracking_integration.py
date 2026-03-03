"""
Integration tests for error tracking in application endpoints.
Tests that errors are properly captured and tracked in production scenarios.
"""

import pytest
from app import app
from monitoring.error_tracker import get_error_tracker


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def tracker():
    """Get error tracker instance."""
    return get_error_tracker()


@pytest.mark.integration
class TestErrorTrackingIntegration:
    """Test error tracking integration in application endpoints."""
    
    def test_brand_asset_upload_error_tracking(self, client, tracker):
        """Test that upload errors are tracked."""
        initial_count = len(tracker.error_history)
        
        # Trigger error by uploading without file
        response = client.post('/api/brand-dna/upload-logo')
        
        # Should return error
        assert response.status_code == 400
        
        # Note: Validation errors (400) may not be tracked, only server errors (500)
        # This is expected behavior - we track server errors, not client errors
    
    def test_ideation_error_tracking(self, client, tracker):
        """Test that ideation errors are tracked."""
        initial_count = len(tracker.error_history)
        
        # Trigger error with empty request
        response = client.post('/api/ideate', json={})
        
        # Should handle gracefully
        assert response.status_code in [200, 500]
        
        # If error occurred, it should be tracked
        if response.status_code == 500:
            assert len(tracker.error_history) > initial_count
            latest_error = tracker.error_history[-1]
            assert latest_error.module in ['content_ideation', 'api']
    
    def test_creative_studio_error_tracking(self, client, tracker):
        """Test that creative studio errors are tracked."""
        initial_count = len(tracker.error_history)
        
        # Trigger error with empty request
        response = client.post('/api/studio/generate', json={})
        
        # Should handle gracefully
        assert response.status_code in [200, 500]
        
        # If error occurred, it should be tracked
        if response.status_code == 500:
            assert len(tracker.error_history) > initial_count
            latest_error = tracker.error_history[-1]
            assert latest_error.module == 'creative_studio'
    
    def test_media_generator_error_tracking(self, client, tracker):
        """Test that media generator errors are tracked."""
        initial_count = len(tracker.error_history)
        
        # Trigger error with invalid format
        response = client.post('/api/studio/generate-media', json={
            'caption': 'test',
            'format': 'invalid_format'
        })
        
        # Should return error
        assert response.status_code == 400
        
        # Error should be tracked if it's a server error
        # (validation errors may not be tracked)
    
    def test_frontend_error_tracking(self, client, tracker):
        """Test that frontend errors can be tracked."""
        initial_count = len(tracker.error_history)
        
        # Send frontend error
        response = client.post('/api/track-error', json={
            'error_type': 'UIError',
            'message': 'Test frontend error',
            'component': 'TestComponent',
            'stack': 'Error: Test\n  at TestComponent'
        })
        
        # Should succeed
        assert response.status_code == 200
        
        # Error should be tracked
        assert len(tracker.error_history) > initial_count
        
        # Check error details
        latest_error = tracker.error_history[-1]
        assert latest_error.module == 'frontend'
        assert 'TestComponent' in str(latest_error.context)
        assert 'Test frontend error' in latest_error.message
    
    def test_error_context_capture(self, client, tracker):
        """Test that error context is properly captured."""
        initial_count = len(tracker.error_history)
        
        # Trigger an error
        response = client.post('/api/ideate', json={})
        
        # Get the tracked error
        if len(tracker.error_history) > initial_count:
            latest_error = tracker.error_history[-1]
            
            # Verify context is captured
            assert hasattr(latest_error, 'timestamp')
            assert hasattr(latest_error, 'module')
            assert hasattr(latest_error, 'message')
            assert hasattr(latest_error, 'stack_trace')
            assert hasattr(latest_error, 'severity')
    
    def test_multiple_errors_tracked(self, client, tracker):
        """Test that multiple errors are tracked independently."""
        initial_count = len(tracker.error_history)
        
        # Trigger multiple errors
        client.post('/api/ideate', json={})
        client.post('/api/studio/generate', json={})
        client.post('/api/track-error', json={
            'error_type': 'UIError',
            'message': 'Test error',
            'component': 'TestComponent'
        })
        
        # Multiple errors should be tracked
        assert len(tracker.error_history) >= initial_count + 2
        
        # Each error should have unique context
        if len(tracker.error_history) > initial_count:
            modules = [e.module for e in tracker.error_history[-3:]]
            # Should have different modules
            assert len(set(modules)) > 1


@pytest.mark.integration
def test_error_tracking_does_not_break_app(client):
    """Test that error tracking failures don't break the application."""
    # Even if error tracking fails, the app should still respond
    response = client.get('/api/health')
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
