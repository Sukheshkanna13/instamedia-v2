"""
Error Tracker - Captures, logs, and alerts on application errors.

This module provides comprehensive error tracking with:
- Full context capture (stack trace, request, user session, environment)
- Sentry integration for production monitoring
- Structured logging for debugging
- Real-time alerting for critical errors
"""
import os
import logging
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# Sentry SDK (optional - gracefully degrades if not configured)
try:
    import sentry_sdk
    from sentry_sdk import capture_exception, capture_message
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorEvent:
    """Represents a single error event."""
    timestamp: datetime
    error_type: str
    message: str
    module: str
    severity: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorMetrics:
    """Aggregated error metrics."""
    total_errors: int
    error_rate: float
    errors_by_type: Dict[str, int]
    errors_by_module: Dict[str, int]
    recent_errors: List[ErrorEvent]


class ErrorTracker:
    """
    Comprehensive error tracking system with Sentry integration.
    
    Captures full error context including:
    - Stack traces
    - Request details (method, URL, headers, body)
    - User session information
    - Environment-specific data (AWS region, Supabase bucket, etc.)
    
    This helps diagnose production issues quickly, especially the errors
    found in manual testing (bucket not found, region mismatch, etc.)
    """
    
    def __init__(self, enable_sentry: bool = True):
        """
        Initialize the error tracker.
        
        Args:
            enable_sentry: Whether to enable Sentry integration
        """
        self.enable_sentry = enable_sentry and SENTRY_AVAILABLE
        self.error_history: List[ErrorEvent] = []
        self.max_history = 1000  # Keep last 1000 errors in memory
        
        # Initialize Sentry if available and enabled
        if self.enable_sentry:
            self._initialize_sentry()
        else:
            if enable_sentry and not SENTRY_AVAILABLE:
                logger.warning("Sentry SDK not available. Install with: pip install sentry-sdk")
    
    def _initialize_sentry(self):
        """Initialize Sentry SDK with configuration."""
        sentry_dsn = os.getenv('SENTRY_DSN')
        
        if not sentry_dsn:
            logger.warning("SENTRY_DSN not configured. Error tracking will use local logging only.")
            self.enable_sentry = False
            return
        
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=os.getenv('ENVIRONMENT', 'development'),
                traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
                profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
                send_default_pii=False,  # Don't send PII by default
            )
            logger.info("✓ Sentry error tracking initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            self.enable_sentry = False
    
    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> None:
        """
        Capture an exception with full context.
        
        Args:
            exception: The exception to capture
            context: Additional context (request, user, environment)
            severity: Error severity level
        """
        # Build complete error context
        error_context = self._build_error_context(exception, context)
        
        # Get stack trace
        stack_trace = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_type=type(exception).__name__,
            message=str(exception),
            module=error_context.get('module', 'unknown'),
            severity=severity.value,
            stack_trace=stack_trace,
            context=error_context
        )
        
        # Store in history
        self._add_to_history(error_event)
        
        # Log locally
        self._log_error(error_event)
        
        # Send to Sentry if enabled
        if self.enable_sentry:
            self._send_to_sentry(exception, error_context, severity)
        
        # Send alert for critical errors
        if severity == ErrorSeverity.CRITICAL:
            self.send_alert(severity.value, str(exception))
    
    def log_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> None:
        """
        Log an error without an exception object.
        
        Args:
            error_type: Type/category of error
            message: Error message
            context: Additional context
            severity: Error severity level
        """
        # Build error context
        error_context = context or {}
        error_context['error_type'] = error_type
        
        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_type=error_type,
            message=message,
            module=error_context.get('module', 'unknown'),
            severity=severity.value,
            context=error_context
        )
        
        # Store in history
        self._add_to_history(error_event)
        
        # Log locally
        self._log_error(error_event)
        
        # Send to Sentry if enabled
        if self.enable_sentry:
            capture_message(message, level=severity.value)
        
        # Send alert for critical errors
        if severity == ErrorSeverity.CRITICAL:
            self.send_alert(severity.value, message)
    
    def send_alert(self, severity: str, message: str) -> None:
        """
        Send real-time alert for critical errors.
        
        In production, this would integrate with:
        - Email notifications
        - Slack/Discord webhooks
        - PagerDuty
        - SMS alerts
        
        Args:
            severity: Error severity
            message: Alert message
        """
        alert_message = f"[{severity.upper()}] {message}"
        
        # Log alert
        logger.critical(f"🚨 ALERT: {alert_message}")
        
        # TODO: Integrate with notification services
        # - Send email via SendGrid/SES
        # - Post to Slack webhook
        # - Trigger PagerDuty incident
        
        # For now, just log
        logger.info("Alert logged. Configure notification services for real-time alerts.")
    
    def get_error_metrics(self) -> ErrorMetrics:
        """
        Get aggregated error metrics.
        
        Returns:
            ErrorMetrics with counts and distributions
        """
        if not self.error_history:
            return ErrorMetrics(
                total_errors=0,
                error_rate=0.0,
                errors_by_type={},
                errors_by_module={},
                recent_errors=[]
            )
        
        # Count errors by type
        errors_by_type: Dict[str, int] = {}
        for error in self.error_history:
            errors_by_type[error.error_type] = errors_by_type.get(error.error_type, 0) + 1
        
        # Count errors by module
        errors_by_module: Dict[str, int] = {}
        for error in self.error_history:
            errors_by_module[error.module] = errors_by_module.get(error.module, 0) + 1
        
        # Calculate error rate (errors per minute over last hour)
        recent_errors = [e for e in self.error_history 
                        if (datetime.utcnow() - e.timestamp).seconds < 3600]
        error_rate = len(recent_errors) / 60.0 if recent_errors else 0.0
        
        return ErrorMetrics(
            total_errors=len(self.error_history),
            error_rate=error_rate,
            errors_by_type=errors_by_type,
            errors_by_module=errors_by_module,
            recent_errors=self.error_history[-10:]  # Last 10 errors
        )
    
    def _build_error_context(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build complete error context.
        
        Captures:
        - Stack trace
        - Request details (if available)
        - User session (if available)
        - Environment configuration
        """
        error_context = context.copy() if context else {}
        
        # Add environment context
        error_context['environment'] = {
            'aws_region': os.getenv('AWS_REGION'),
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_bucket': os.getenv('SUPABASE_BUCKET_NAME', 'brand-assets'),
            'chromadb_path': os.getenv('CHROMADB_PATH', './chromadb'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
        }
        
        # Add exception details
        error_context['exception'] = {
            'type': type(exception).__name__,
            'message': str(exception),
            'args': exception.args,
        }
        
        return error_context
    
    def _add_to_history(self, error_event: ErrorEvent) -> None:
        """Add error to history, maintaining max size."""
        self.error_history.append(error_event)
        
        # Trim history if too large
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _log_error(self, error_event: ErrorEvent) -> None:
        """Log error locally with structured format."""
        log_message = (
            f"\n{'='*60}\n"
            f"ERROR CAPTURED\n"
            f"{'='*60}\n"
            f"Timestamp: {error_event.timestamp.isoformat()}\n"
            f"Type: {error_event.error_type}\n"
            f"Module: {error_event.module}\n"
            f"Severity: {error_event.severity}\n"
            f"Message: {error_event.message}\n"
        )
        
        if error_event.stack_trace:
            log_message += f"\nStack Trace:\n{error_event.stack_trace}\n"
        
        if error_event.context:
            log_message += f"\nContext:\n"
            for key, value in error_event.context.items():
                log_message += f"  {key}: {value}\n"
        
        log_message += f"{'='*60}\n"
        
        # Log at appropriate level
        if error_event.severity == ErrorSeverity.CRITICAL.value:
            logger.critical(log_message)
        elif error_event.severity == ErrorSeverity.ERROR.value:
            logger.error(log_message)
        elif error_event.severity == ErrorSeverity.WARNING.value:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _send_to_sentry(
        self,
        exception: Exception,
        context: Dict[str, Any],
        severity: ErrorSeverity
    ) -> None:
        """Send error to Sentry with context."""
        try:
            # Set context in Sentry
            if 'request' in context:
                sentry_sdk.set_context("request", context['request'])
            
            if 'user' in context:
                sentry_sdk.set_context("user", context['user'])
            
            if 'environment' in context:
                sentry_sdk.set_context("environment", context['environment'])
            
            # Set tags for filtering
            sentry_sdk.set_tag("module", context.get('module', 'unknown'))
            sentry_sdk.set_tag("severity", severity.value)
            
            # Capture exception
            capture_exception(exception)
            
        except Exception as e:
            logger.error(f"Failed to send error to Sentry: {e}")


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get or create global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR
) -> None:
    """
    Convenience function to track an error.
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            track_error(e, context={'module': 'brand_upload'})
    """
    tracker = get_error_tracker()
    tracker.capture_exception(exception, context, severity)


def track_supabase_error(
    exception: Exception,
    operation: str,
    bucket_name: str,
    file_name: Optional[str] = None
) -> None:
    """
    Track Supabase-specific errors with relevant context.
    
    Captures the "Bucket not found" errors found in manual testing.
    """
    context = {
        'module': 'supabase_storage',
        'operation': operation,
        'bucket_name': bucket_name,
        'file_name': file_name,
        'supabase_url': os.getenv('SUPABASE_URL'),
    }
    track_error(exception, context, ErrorSeverity.ERROR)


def track_aws_error(
    exception: Exception,
    service: str,
    operation: str,
    region: Optional[str] = None,
    model_id: Optional[str] = None
) -> None:
    """
    Track AWS-specific errors with relevant context.
    
    Captures the region mismatch errors found in manual testing.
    """
    context = {
        'module': f'aws_{service}',
        'operation': operation,
        'region': region or os.getenv('AWS_REGION'),
        'model_id': model_id,
    }
    track_error(exception, context, ErrorSeverity.ERROR)


def track_api_error(
    exception: Exception,
    endpoint: str,
    method: str,
    status_code: Optional[int] = None,
    query_params: Optional[Dict] = None
) -> None:
    """
    Track API errors with request context.
    
    Captures API failures that result in blank pages.
    """
    context = {
        'module': 'api',
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'query_params': query_params,
    }
    track_error(exception, context, ErrorSeverity.ERROR)


def track_ui_error(
    exception: Exception,
    component: str,
    props: Optional[Dict] = None
) -> None:
    """
    Track UI component errors.
    
    Captures component rendering failures and non-functional buttons.
    """
    context = {
        'module': 'ui',
        'component': component,
        'props': props,
    }
    track_error(exception, context, ErrorSeverity.ERROR)
