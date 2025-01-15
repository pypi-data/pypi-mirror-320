"""
Enhanced custom exceptions for YouTube Transcript Generator.
"""
from typing import Optional, Any, Dict
from datetime import datetime


class TranscriptGeneratorError(Exception):
    """Base exception for all transcript generator errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.__class__.__name__
        }


class ValidationError(TranscriptGeneratorError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        """Initialize validation error."""
        details = {
            "field": field,
            "invalid_value": str(value) if value is not None else None
        }
        super().__init__(message, "VALIDATION_ERROR", details)


class VideoError(TranscriptGeneratorError):
    """Base class for video-related errors."""
    
    def __init__(
        self,
        message: str,
        video_id: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize video error."""
        self.video_id = video_id
        video_details = {"video_id": video_id, **(details or {})}
        super().__init__(message, error_code, video_details)


class VideoProcessingError(VideoError):
    """Raised when video processing fails."""
    
    def __init__(
        self,
        message: str,
        video_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, video_id, "VIDEO_PROCESSING_ERROR", details)


class VideoNotFoundError(VideoError):
    """Raised when video doesn't exist."""
    
    def __init__(self, video_id: Optional[str] = None):
        super().__init__(
            "Video not found",
            video_id,
            "VIDEO_NOT_FOUND"
        )


class VideoPrivateError(VideoError):
    """Raised when video is private."""
    
    def __init__(self, video_id: Optional[str] = None):
        super().__init__(
            "This video is private",
            video_id,
            "VIDEO_PRIVATE"
        )


class VideoUnavailableError(VideoError):
    """Raised when video is unavailable (region-locked, age-restricted, etc.)."""
    
    def __init__(
        self,
        message: str,
        video_id: Optional[str] = None,
        reason: Optional[str] = None
    ):
        details = {"reason": reason} if reason else None
        super().__init__(message, video_id, "VIDEO_UNAVAILABLE", details)


class AIProcessingError(TranscriptGeneratorError):
    """Raised when AI processing fails."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        ai_details = {"model_name": model_name, **(details or {})}
        super().__init__(message, "AI_PROCESSING_ERROR", ai_details)


class TranscriptionError(TranscriptGeneratorError):
    """Raised when transcription process fails."""
    
    def __init__(
        self,
        message: str,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        trans_details = {
            "source_language": source_language,
            "target_language": target_language,
            **(details or {})
        }
        super().__init__(message, "TRANSCRIPTION_ERROR", trans_details)


class RateLimitError(TranscriptGeneratorError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None
    ):
        details = {
            "retry_after": retry_after,
            "limit_type": limit_type
        }
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class AuthenticationError(TranscriptGeneratorError):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None
    ):
        details = {"service": service} if service else None
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class NetworkError(TranscriptGeneratorError):
    """Raised when network-related operations fail."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        url: Optional[str] = None
    ):
        details = {
            "status_code": status_code,
            "url": url
        }
        super().__init__(message, "NETWORK_ERROR", details)


class ResourceNotFoundError(TranscriptGeneratorError):
    """Raised when a required resource is not found."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, "RESOURCE_NOT_FOUND", details)


class ConfigurationError(TranscriptGeneratorError):
    """Raised when there's a configuration error."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        config_details = {"config_key": config_key, **(details or {})}
        super().__init__(message, "CONFIGURATION_ERROR", config_details)


class CaptionError(VideoError):
    """Raised when there's an issue with video captions."""
    
    def __init__(
        self,
        message: str,
        video_id: Optional[str] = None,
        language: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        caption_details = {"language": language, **(details or {})}
        super().__init__(message, video_id, "CAPTION_ERROR", caption_details)


class TokenLimitError(AIProcessingError):
    """Raised when token limit is exceeded."""
    
    def __init__(
        self,
        token_count: int,
        max_tokens: int,
        model_name: Optional[str] = None
    ):
        message = f"Token count ({token_count}) exceeds maximum allowed ({max_tokens})"
        details = {
            "token_count": token_count,
            "max_tokens": max_tokens
        }
        super().__init__(message, model_name, details)